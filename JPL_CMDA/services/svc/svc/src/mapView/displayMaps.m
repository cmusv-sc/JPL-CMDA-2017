function status = displayMaps(dataInfo, figFile, outputFile, displayOpt)
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
%   2016/04/26:	Initial version, cz
%
status = -1;

nVars = length(dataInfo);

% x_opt, y_opt is ignored, it wuold be very rare to use log scale for longitude and latitude
% we need a_opt to determine whether to compute the anomaly
[x_opt, y_opt, z_opt, a_opt, c_opt, cm_opt, nR, nC] = decodeDisplayOpt(displayOpt);

for varI = 1:nVars
  printf('variable number = %d\n', varI);
  nMonths = numberOfMonths(dataInfo(varI).startTime, dataInfo(varI).endTime);
  printf('number of month = %d\n', nMonths);

  nFiles = length(dataInfo(varI).dataFile);
  printf('number of files = %d\n', nFiles);

  dataInfo(varI).dataForDispay = [];
  dataInfo(varI).v_units = [];
  dataInfo(varI).lon = [];
  dataInfo(varI).lat = [];

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

    varIs2d = isNA(dataInfo(varI).plev) || isempty(plevVarName)

    if isempty(monthlyData)
      lon = ncread(thisFile, 'lon');
      lat = ncread(thisFile, 'lat');
      [lon, lat, lonIdx, latIdx] = subIdxLonAndLat(lon, lat, dataInfo(varI).lonRange, dataInfo(varI).latRange);
      nLon = length(lon);
      nLat = length(lat);
      dataInfo(varI).lon = lon;
      dataInfo(varI).lat = lat;
      monthlyData = nan(nLon, nLat, nMonths, 'single');

      if ~varIs2d
        plev = readPressureLevels(thisFile, plevVarName)/100; % we default assume hPa as the units for pressure level
        if strcmp(dataInfo(varI).varName, 'ot') || strcmp(dataInfo(varI).varName, 'os') 
          plev = plev/100; % further convert hPa -> dbar
        end
        [p_idx, p_alphas] = linearInterpHelper(dataInfo(varI).plev, plev, 'log'); % get the layers relevant to the specified pressure level
      end
    end
    v_units = removeTrailingNullChar(ncreadatt(thisFile, dataInfo(varI).varName, 'units'));
    dataInfo(varI).v_units = adjustUnits(v_units, dataInfo(varI).varName);
    [startTime_thisFile, endTime_thisFile] = getStartAndStopDates(thisFile)
    monthIdx1 = numberOfMonths(dataInfo(varI).startTime, startTime_thisFile);
    monthIdx2 = numberOfMonths(dataInfo(varI).startTime, endTime_thisFile);

    nMonths_thisFile = numberOfMonths(startTime_thisFile, endTime_thisFile);

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
    disp(lonIdx);
    if varIs2d
      monthlyData(:,:, monthIdx1:monthIdx2) = ncreadVar(thisFile, dataInfo(varI).varName, [lonIdx(1), latIdx(1),idx2Data_start], [length(lonIdx), length(latIdx), idx2Data_stop-idx2Data_start+1]);
    else
      nLon_tmp = length(lonIdx); nLat_tmp = length(latIdx); nP_tmp = length(p_idx);
      v = ncreadVar(thisFile, dataInfo(varI).varName, [lonIdx(1), latIdx(1),p_idx(1), idx2Data_start], [nLon_tmp, nLat_tmp, nP_tmp, idx2Data_stop-idx2Data_start+1]);
      monthlyData(:,:, monthIdx1:monthIdx2) = reshape(v(:, :, 1, :), nLon_tmp, nLat_tmp, []) * p_alphas(1);
      for pIdx = 2:nP_tmp
        monthlyData(:,:,monthIdx1:monthIdx2) = monthlyData(:,:,monthIdx1:monthIdx2) + reshape(v(:, :, pIdx, :), nLon_tmp, nLat_tmp, []) * p_alphas(pIdx);
      end
    end
    dataInfo(varI).long_name = removeTrailingNullChar(ncreadatt(thisFile, dataInfo(varI).varName, 'long_name'));
  end
  % we check whether to compute anomaly
  if a_opt
    monthlyData = simpleAnomaly(monthlyData, 3);
  end
  % We now determine the relevant months within a year using monthIdx and start month
  monthIdxAdj = mod(dataInfo(varI).monthIdx - dataInfo(varI).startTime.month, 12) + 1;
  dataInfo(varI).dataForDisplay = squeeze(simpleClimatology(monthlyData,3, monthIdxAdj));
  clear v;
end

% If not specified by user, nR & nC will be 0
if nR*nC == 0
  [nR, nC] = designMultiPanel(nVars, 'map');
end

% default color range to be the same for all the plots
cLim = [min(dataInfo(1).dataForDisplay(:)), max(dataInfo(1).dataForDisplay(:))];
for ii = 2:nVars
  cLim(1) = min([min(dataInfo(varI).dataForDisplay(:)), cLim(1)]);
  cLim(2) = max([max(dataInfo(varI).dataForDisplay(:)), cLim(2)]);
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
cfgParams.xlabelOff = false;
cfgParams.ylabelOff = false;
[h, cb] = displayTwoDimData(dataInfo(varI).lon, dataInfo(varI).lat, z, gca, cfgParams);
if ~c_opt
  disp(cLim);
  caxis(cLim);
end
set(h, 'fontsize', 12, 'fontweight', 'bold');
if z_opt
  set(cb, 'xticklabel', num2str(10.^(get(cb, 'xtick')'),3));
end
set(get(cb,'xlabel'), 'string', [dataInfo(varI).long_name '(' dataInfo(varI).v_units ')'], 'FontSize', 16);
plev_units = 'hPa';
if strcmp(dataInfo(varI).varName, 'ot') || strcmp(dataInfo(varI).varName, 'os') 
  plev_units = 'dbar';
end
if varIs2d
  %title(h, [dataInfo(varI).long_name ', ' date2Str(dataInfo(varI).startTime, '/') '-' date2Str(dataInfo(varI).endTime, '/') ' climatology (' dataInfo(varI).v_units '), ' seasonStr(dataInfo(varI).monthIdx)]);
  title(h, strrep([dataInfo(varI).sourceName ', ' dataInfo(varI).varName ' (' dataInfo(varI).v_units ')' ], '_', '\_'));
else
  %title(h, [dataInfo(varI).long_name ', at ' num2str(round(dataInfo(varI).plev)) plev_units ', ' date2Str(dataInfo(varI).startTime, '/') '-' date2Str(dataInfo(varI).endTime, '/') ' climatology (' dataInfo(varI).v_units '), ' seasonStr(dataInfo(varI).monthIdx)]);
  title(h, strrep([dataInfo(varI).sourceName ', ' dataInfo(varI).varName ', at ' num2str(round(dataInfo(varI).plev)) plev_units ' (' dataInfo(varI).v_units ')' ], '_', '\_'));
end
end
print(gcf, figFile, '-S1000,1000', '-djpeg');

status = 0;
if nVars == 1
  data.dimNames = {'longitude', 'latitude'};
  data.nDim = 2;
  data.dimSize = [length(dataInfo(1).lon), length(dataInfo(1).lat)];
  data.dimVars = {dataInfo(1).lon, dataInfo(1).lat};
  data.var = dataInfo(1).dataForDisplay;
  data.varName = dataInfo(1).varName;
  data.dimVarUnits = {'degree_east', 'degree_north'};
  data.varUnits = dataInfo(1).v_units;
  data.varLongName = dataInfo(1).long_name;
  if ~isempty(outputFile);
    status = storeDataInNetCDF(data, outputFile);
  end
else
  for ii = 1:nVars
    data.varDimIdx{ii} = 2*(ii-1)+(1:2);
    data.dimNames{2*(ii-1)+1} = ['longitude_' num2str(ii)];
    data.dimNames{2*(ii-1)+2} = ['latiitude_' num2str(ii)];
    data.dimVarUnits{2*(ii-1)+1} = 'degree_east';
    data.dimVarUnits{2*(ii-1)+2} = 'degree_north';
    data.dimSize(2*(ii-1)+1) = length(dataInfo(varI).lon);
    data.dimSize(2*(ii-1)+2) = length(dataInfo(varI).lat);
    data.dimVars{2*(ii-1)+1} = dataInfo(varI).lon;
    data.dimVars{2*(ii-1)+2} = dataInfo(varI).lat;
    data.vars{ii} = dataInfo(varI).dataForDisplay;
    data.varNames{ii} = [dataInfo(varI).varName '_' num2str(ii)];
    data.varUnits{ii} = dataInfo(varI).v_units;
    data.varLongNames{ii} = dataInfo(varI).long_name;
  end
  data.nDim = nVars*2;
  if ~isempty(outputFile);
    status = storeMultiVarDataInNetCDF(data, outputFile);
  end
end
