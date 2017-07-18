function status = displayZonalMean(dataInfo, figFile, outputFile, displayOpt)
%
% This function reads relevant data from the data files in the list, process the data, and dispaly two-dimension maps
% for each variables.
%
% Input:
%   dataInfo	-- a structure array contains information of variables
%		-- dataFile	-- a list of relevant data files
%		-- varName	-- the physical variable of interest, or to be displayed
%		-- sourceName	-- information regarding the data source, for dipslay
%   		-- lonRnage	-- an optional argument to specify box boundary along longitude
%   		-- latRnage	-- an optional argument to specify box boundary along latitude
%   		-- plev		-- specifies pressure level(s), single value will be treated as a single level, two values are treated as a range
%   		-- startTime	-- the start time of the temporal window over which the climatology is computed
%   		-- endTime	-- the end time of the temporal window over which the climatology is computed
%   		-- monthIdx	-- idx of the month of interest, this is useful for specify a season.
%   figFile	-- the name of the output file for storing the figure to be displayed
%   outputFile	-- the name of the output file for storing data of used by the figure
%   displayOpt	-- options to specify display
%
% Output:
%   status	-- a status flag, 0 = okay, -1 something is not right
%
% Author: Chengxing Zhai
%
% Revision history:
%   2017/04/10:	Initial version, cz
%
status = -1;

nVars = length(dataInfo);

% x_opt, y_opt is ignored, it wuold be very rare to use log scale for longitude and latitude
% we need a_opt to determine whether to compute the anomaly
[x_opt, y_opt, z_opt, a_opt, c_opt, cm_opt, nR, nC] = decodeDisplayOpt(displayOpt);

lg_str = cell(nVars,1);

for varI = 1:nVars
  printf('variable number = %d\n', varI);
  nMonths = numberOfMonths(dataInfo(varI).startTime, dataInfo(varI).endTime);
  printf('number of month = %d\n', nMonths);

  nFiles = length(dataInfo(varI).dataFile);
  printf('number of files = %d\n', nFiles);

  lg_str{varI} = [strrep(dataInfo(varI).sourceName, '_', '\_') ', ' date2Str(dataInfo(varI).startTime) '-' date2Str(dataInfo(varI).endTime) ', ' seasonStr(dataInfo(varI).monthIdx)];

  dataInfo(varI).dataForDisplay = [];
  dataInfo(varI).v_units = [];
  dataInfo(varI).lat = [];
  dataInfo(varI).p = [];

  monthlyData = [];
  v = [];
  lon = [];
  lat = [];
  plev = [];

  for fileI = 1:nFiles
    thisFile = dataInfo(varI).dataFile{fileI};
    fileInfo = ncinfo(thisFile);
    varinfo = fileInfo.Variables;

    plevVarName = [];
    for ii = 1:length(varinfo)
      varNameList{ii} = [varinfo(ii).Name];
      if strcmp('plev', varNameList{ii})
        plevVarName = 'plev';
        break;
      elseif strcmp('lev', varNameList{ii})
        plevVarName = 'lev';
      end
    end

    varIs2d = isNA(dataInfo(varI).plev) || isempty(plevVarName);
    dataIs2d = varIs2d;

    if isempty(monthlyData)
      lon = ncread(thisFile, 'lon');
      lat = ncread(thisFile, 'lat');
      [lon, lat, lonIdx, latIdx] = subIdxLonAndLat(lon, lat, dataInfo(varI).lonRange, dataInfo(varI).latRange);
      nLat = length(lat);
      dataInfo(varI).lat = lat;

      % if the specified pressure leve is only one level, we then interpolate the data to the pressure level
      if ~varIs2d
        nP = length(dataInfo(varI).plev);
        plev = readPressureLevels(thisFile, plevVarName)/100; % we default assume hPa as the units for pressure level
        p_units = 'hPa';
        if strcmp(dataInfo(varI).varName, 'ot') || strcmp(dataInfo(varI).varName, 'os')
          plev = plev/100; % from hPa -> dbar
          p_units = 'dbar';
        end
        if nP == 1
          dataIs2d = true;
          [p_idx, p_alphas] = linearInterpHelper(dataInfo(varI).plev, plev, 'log'); % get the layers relevant to the specified pressure level
        else
          pIdx = indexWithin(plev, [min(dataInfo(varI).plev), max(dataInfo(varI).plev)]);;
          dataInfo(varI).p = plev(pIdx);
          dataIs2d = false;
          nP = length(pIdx);
        end
      else
        dataIs2d = true;
      end
      if dataIs2d 
        monthlyData = nan(nLat, nMonths, 'single');
      else
        monthlyData = nan(nLat, nP, nMonths, 'single');
      end
    end
    v_units = removeTrailingNullChar(ncreadatt(thisFile, dataInfo(varI).varName, 'units'));
    dataInfo(varI).v_units = adjustUnits(v_units, dataInfo(varI).varName);
    [startTime_thisFile, endTime_thisFile] = getStartAndStopDates(thisFile)
    monthIdx1 = numberOfMonths(dataInfo(varI).startTime, startTime_thisFile);
    monthIdx2 = numberOfMonths(dataInfo(varI).startTime, endTime_thisFile);
    nMonths_thisFile = numberOfMonths(startTime_thisFile, endTime_thisFile);

    timeDim = 3;
    if ~varIs2d
      timeDim = 4;
    end

    idx2Data_start = 1;
    idx2Data_stop = nMonths_thisFile;

    if monthIdx1 <= 1
      idx2Data_start = 1 + (1 - monthIdx1);
      monthIdx1 = 1;
    end

    if monthIdx2 >= nMonths
      idx2Data_stop = idx2Data_stop - (monthIdx2 - nMonths);
      monthIdx2 = nMonths;
    end

    disp(latIdx);
    nLon_tmp = length(lonIdx);
    if varIs2d
      v = ncreadVar(thisFile, dataInfo(varI).varName,[lonIdx(1), latIdx(1), idx2Data_start], [nLon_tmp, nLat, idx2Data_stop - idx2Data_start + 1]);
      monthlyData(:,monthIdx1:monthIdx2) = reshape(meanExcludeNaN(v,1), nLat, []);
    else
      if dataIs2d
        v = ncreadVar(thisFile, dataInfo(varI).varName,[lonIdx(1), latIdx(1), p_idx(1), idx2Data_start], [nLon_tmp, nLat, length(p_idx), idx2Data_stop - idx2Data_start + 1]);
        monthlyData(:, monthIdx1:monthIdx2) = reshape(meanExcludeNaN(v(:, :, 1, :),1) * p_alphas(1), nLat, []);
        for pI = 2:length(p_idx)
          monthlyData(:,monthIdx1:monthIdx2) = monthlyData(:,monthIdx1:monthIdx2) + reshape(meanExcludeNaN(v(:, :, pI, :),1), nLat, []) * p_alphas(pI);
        end
      else
        v = ncreadVar(thisFile, dataInfo(varI).varName,[lonIdx(1), latIdx(1), pIdx(1), idx2Data_start], [nLon_tmp, nLat, nP, idx2Data_stop - idx2Data_start + 1]);
        monthlyData(:,:,monthIdx1:monthIdx2) = reshape(meanExcludeNaN(v,1), nLat, nP, []);
      end
    end
    dataInfo(varI).long_name = removeTrailingNullChar(ncreadatt(thisFile, dataInfo(varI).varName, 'long_name'));
  end
  % we check whether to compute anomaly
  if a_opt
    monthlyData = simpleAnomaly(monthlyData, timeDim-1);
  end
  % We now determine the relevant months within a year using monthIdx and start month
  monthIdxAdj = mod(dataInfo(varI).monthIdx - dataInfo(varI).startTime.month, 12) + 1;
  dataInfo(varI).dataForDisplay = reshape(simpleClimatology(monthlyData,timeDim-1, monthIdxAdj), nLat, []);
  clear v;
end

if dataIs2d
colorOrder = {'b', 'g', 'r', 'm', 'c', 'k'};
markerOrder = {'s', 'o', 'd', 'v', '^', 'p', '>', '<', 'x', '*', 'h'};

yLim = rangeOfDataInStructArray(dataInfo, 'dataForDisplay');
Y_range = diff(yLim);

figure(1);
clf;
for varI = 1:nVars
  lin_style = [colorOrder{1 + mod(varI-1,6)} markerOrder{1 + mod(varI-1, 11)} '-'];
  plot(dataInfo(varI).lat, dataInfo(varI).dataForDisplay, lin_style, 'linewidth', 2);
  hold on;
end
if Y_range > 0
  ylim(yLim + [-0.1 , nVars*0.1]*Y_range); 
end
xlabel('Latitude (deg)')
set(gca, 'fontweight', 'bold');
grid on;
ylabel(['Mean (' dataInfo(1).v_units ')']);
if nVars > 1
  legend(lg_str);
  title([dataInfo(1).long_name ', zonal mean (' dataInfo(1).v_units ')']);
else
  title([dataInfo(1).long_name ', zonal mean value over lon(' num2str(dataInfo(1).lonRange(1)) ',' num2str(dataInfo(1).lonRange(2)) ')deg, (' dataInfo(1).v_units ')']);
end

if x_opt
  set(gca, 'xscale', 'log');
end
if y_opt | z_opt
  set(gca, 'yscale', 'log');
end
print(gcf, figFile, '-djpeg');

status = 0;
if nVars == 1
  data.dimNames = {'latitude'};
  data.nDim = 1;
  data.dimSize = [length(dataInfo(1).lat)];
  data.dimVars = {dataInfo(1).lat};
  data.var = dataInfo(1).dataForDisplay;
  data.varName = dataInfo(1).varName;
  data.dimVarUnits = {'degree_north'};
  data.varUnits = dataInfo(1).v_units;
  data.varLongName = dataInfo(1).long_name;
  status = storeDataInNetCDF(data, outputFile);
else
  % When there are multiple variables, we regrid them into the same latitude grid and store them
  dlat = 1; % FIX, this is hard coded resolution of 1 deg for latitude, it should be updated by user if desired
  interp_method = 'linear'; % FIX, this should be also determined by user
  latRange = rangeOfDataInStructArray(dataInfo, 'lat');
  lat = latRange(1):dlat:latRange(2);
  nLat = length(lat);
  dataForDisplay = zeros(nLat, nVars);
  for varI = 1:nVars
    dataForDisplay(:,varI) = interp1(dataInfo(varI).lat, dataInfo(varI).dataForDisplay, lat, interp_method); 
  end

  data.dimNames = {'lat', 'varIdx'};
  data.nDim = 2;
  data.dimSize = [nLat, nVars];
  data.dimVars = {lat, 1:nVars};
  data.var = dataForDisplay;
  data.varName = dataInfo(1).varName;
  data.dimVarUnits = {'degrees_north', 'N/A'};
  data.varUnits = dataInfo(1).v_units;
  data.varLongName = dataInfo(1).long_name;
  status = storeDataInNetCDF(data, outputFile);
end
else
% If not specified by user, nR & nC will be 0
if nR*nC == 0
  [nR, nC] = designMultiPanel(nVars, 'map');
end

% default color range to be the same for all the plots
cLim = rangeOfDataInStructArray(dataInfo, 'dataForDisplay');

if prod(cLim) < 0
  cmap = myColorMap(cLim);
else
  cmap = colormap('jet');
end

figure;
frameSize_X = 100 + 800*nC;
frameSize_Y = 100 + 450*nR;
set(gcf, 'position', [100, 200, frameSize_X, frameSize_Y]);
set(gcf, 'paperpositionmode', 'auto');
set(gcf, 'papersize', [frameSize_X, frameSize_Y]*15/max([frameSize_X, frameSize_Y]));
for varI = 1:nVars
subplot(nR, nC, varI);
if z_opt
  z = log10(dataInfo(varI).dataForDisplay + 1e-4*max(dataInfo(varI).dataForDisplay(:)));
  cfgParams.logScale = true;
else
  z = dataInfo(varI).dataForDisplay;
end
if y_opt
  y = -log10(dataInfo(varI).p);
else
  y = -dataInfo(varI).p;
end
x = dataInfo(varI).lat;
contourf(x, y, z', 30, 'linecolor', 'none');
set(gca, 'fontweight', 'bold');
currYTick = get(gca, 'ytick')';
currYTick(currYTick ~= 0) = - currYTick(currYTick ~= 0);
xlabel('Latitude (deg)');
if y_opt
  set(gca, 'yticklabel', num2str(10.^currYTick));
else
  set(gca, 'yticklabel', num2str(currYTick));
end
if ~c_opt
  disp(cLim);
  caxis(cLim);
end
colormap(cmap);
if z_opt
  set(cb, 'xticklabel', num2str(10.^(get(cb, 'xtick')'),3));
end
cb = colorbar('southoutside');
set(get(cb,'xlabel'), 'string', [dataInfo(varI).long_name '(' dataInfo(varI).v_units ')'], 'FontSize', 16);
ylabel(['Pressure level (' p_units ')']);
title(strrep([dataInfo(varI).sourceName ', ' dataInfo(varI).varName ', ' date2Str(dataInfo(varI).startTime) '-' date2Str(dataInfo(varI).endTime) ', ' seasonStr(dataInfo(varI).monthIdx) ',  (' dataInfo(varI).v_units ')' ], '_', '\_'));
end
print(gcf, figFile, '-S1000,1000', '-djpeg');

if nVars == 1
  data.dimNames = {'latitude', 'plev'};
  data.nDim = 2;
  data.dimSize = [length(dataInfo(1).lat), length(dataInfo(1).p)];
  data.dimVars = {dataInfo(1).lat, dataInfo(1).p};
  data.var = dataInfo(1).dataForDisplay;
  data.varName = dataInfo(1).varName;
  data.dimVarUnits = {'degree_north', 'plev'};
  data.varUnits = dataInfo(1).v_units;
  data.varLongName = dataInfo(1).long_name;
  status = storeDataInNetCDF(data, outputFile);
else
  pRange = rangeOfDataInStructArray(dataInfo, 'plev');
  latRange = rangeOfDataInStructArray(dataInfo, 'lat');
  dlat = 1; % FIX, this should not be harded coded, should be configurable by user
  dp = 50; %hPa, FIX, this should not be harded coded, should be configurable by user
  lat = latRange(1):dlat:latRange(2);
  plev = pRange(1):dp:pRange(2);
  nP = length(plev);
  nLat = length(lat);
  inter_method = 'linear';
  dataForDisplay = zeros(nLat, nP, nVars);

  [xx_regrid, yy_regrid] = meshgrid(log(plev), lat);
  for varI = 1:nVars
    [xx_orig, yy_orig] = meshgrid(log(dataInfo(varI).p), dataInfo(varI).lat);
    dataForDisplay(:,:,varI) = interp2(xx_orig, yy_orig, dataInfo(varI).dataForDisplay, xx_regrid, yy_regrid);
  end
  data.dimNames = {'latitude', 'plev', 'varIdx'};
  data.nDim = 3;
  data.dimSize = [nLat, nP, nVars];
  data.dimVars = {lat, plev, 1:nVars};
  data.var = dataForDisplay;
  data.varName = dataInfo(1).varName;
  data.dimVarUnits = {'degree_north', 'plev', 'N/A'};
  data.varUnits = dataInfo(1).v_units;
  data.varLongName = dataInfo(1).long_name;
  status = storeDataInNetCDF(data, outputFile);
end
end
