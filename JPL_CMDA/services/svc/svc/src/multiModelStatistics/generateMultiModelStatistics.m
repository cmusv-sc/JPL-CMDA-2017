function status = generateMultiModelStatistics(dataInfo, startTime, stopTime, figFile, outputFile, displayOpt)
%
% This function extracts relevant data from the data file list according
% the specified temporal range [startTime, stopTime]
%
% Input:
%   dataInfo	-- a structure array contains information of variables
%		-- dataFile	-- a list of relevant data files
%		-- varName	-- the physical variable of interest, or to be displayed
%		-- sourceName	-- information regarding the data source, for dipslay
%   		-- lonRnage	-- an optional argument to specify box boundary along longitude
%   		-- latRnage	-- an optional argument to specify box boundary along latitude
%   		-- plev	-- specifies pressure level(s), single value will be treated as a single level, two values are treated as a range
%   startTime	-- the start time of the temporal window over which the climatology is computed
%   stopTime	-- the stop time of the temporal window over which the climatology is computed
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
%   2012/12/10:	Initial version, cz
%   2012/02/06: Added more arguments to facilitate a customized regional and seasonal climatology
%
status = -1;

nVars = length(dataInfo);
nMonths = numberOfMonths(startTime, stopTime);
printf('number of month = %d\n', nMonths);

dataForDisplay = zeros(nMonths, nVars);

lg_str = cell(nVars,1);
v_units = cell(nVars,1);
for varI = 1:nVars
varName = dataInfo(varI).varName;
lg_str{varI} = [strrep(dataInfo(varI).sourceName, '_', '\_') ', lon' range2str(dataInfo(varI).lonRange) 'deg, lat' range2str(dataInfo(varI).latRange) 'deg'];

monthlyData = [];
nFiles = length(dataInfo(varI).dataFile);
v = [];
lon = [];
lat = [];

for fileI = 1:nFiles
  thisFile = dataInfo(varI).dataFile{fileI};

  if isempty(monthlyData)
    lon = ncread(thisFile, 'lon');
    lat = ncread(thisFile, 'lat');

    [lon, lat, lonIdx, latIdx] = subIdxLonAndLat(lon, lat, dataInfo(varI).lonRange, dataInfo(varI).latRange);

    monthlyData = nan(nMonths,1);
  end

  v_units{varI} = 'DefaultUnits';
  if hasAttribute(thisFile, varName, 'units')
    v_units{varI} = deblank(ncreadatt(thisFile, varName, 'units'));
  end

  [startTime_thisFile, stopTime_thisFile] = getStartAndStopDates(thisFile);

  monthIdx1 = numberOfMonths(startTime, startTime_thisFile);
  monthIdx2 = numberOfMonths(startTime, stopTime_thisFile);

  % Determine whether this variable is 2-d or 3-d
  f_info = ncinfo(thisFile);
  varList = {f_info.Variables.Name};
  idx = find(strcmp(varList, 'plev'));
  nMonths_thisFile = numberOfMonths(startTime_thisFile, stopTime_thisFile);

  varIs2d = isNA(dataInfo(varI).plev) || isempty(idx);

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

  nLon_tmp = length(lonIdx);
  nLat_tmp = length(latIdx);
  if varIs2d
    v = ncreadVar(thisFile, varName, [lonIdx(1), latIdx(1), idx2Data_start], [nLon_tmp, nLat_tmp, idx2Data_stop - idx2Data_start + 1]);
    monthlyData(monthIdx1:monthIdx2) = averageOverSphere(v, lat, dataInfo(varI).latRange);
  else
    plev = ncread(thisFile, 'plev') / 100; % using hPa as units
    [p_idx, p_alphas] = linearInterpHelper(dataInfo(varI).plev, plev, 'log');
    n_p = length(p_idx);
    v = ncreadVar(thisFile, varName, [lonIdx(1), latIdx(1), idx2Data_start, p_idx(1)], [nLon_tmp, nLat_tmp, n_p, idx2Data_stop - idx2Data_start + 1]);
    monthlyData(monthIdx1:monthIdx2) = p_alphas(1) * averageOverSphere(reshape(v(:, :, 1, :), nLon_tmp, nLat_tmp, []), lat, dataInfo(varI).latRange);
    for pIdx = 2:length(p_idx)
      monthlyData(monthIdx1:monthIdx2) = monthlyData(monthIdx1:monthIdx2) + p_alphas(pIdx) * averageOverSphere(reshape(v(:, :, pIdx, :), nLon_tmp, nLat_tmp, []), lat, dataInfo(varI).latRange);
    end
  end
  long_name{varI} = 'DefaultDataName';
  if hasAttribute(thisFile, varName, 'long_name');
    long_name{varI} = deblank(ncreadatt(thisFile, varName, 'long_name'));
  end
  clear v;
end

dataForDisplay(:,varI) = monthlyData;
%lg_str{varI} = [lg_str{varI} ':' long_name{varI}];
lg_str{varI} = [lg_str{varI} ':' varName];

end

nMonths = numberOfMonths(startTime, stopTime);

yearSet = false;
if nMonths < 18
  x_tick_vec = 1:nMonths
  x_label_str = cell(nMonths,1);
  for ii = 1:nMonths
    thisDate = dateFrom(startTime, ii -1);
    if thisDate.month == 1
      x_label_str{ii} = num2str(thisDate.year);
      yearSet = true;
    else
      x_label_str{ii} = month2Str(thisDate.month, 'text_3');
    end
  end
  if ~yearSet
    x_label_str{1} = [num2str(startTime.year) x_label_str{1}]; % make sure the year is displayed
  end
else
  nYears = stopTime.year - startTime.year + 1;
  deltaYear = 1+floor(nYears/12);
  nXTick = ceil(nYears/deltaYear);

  yearVec = startTime.year+deltaYear*(0:nXTick);
  x_label_str = cell(nXTick+1, 1);
  for ii = 1:(nXTick+1)
    x_label_str{ii} = num2str(yearVec(ii));
  end
  x_tick_vec = (2-startTime.month)+(12*deltaYear)*(0:nXTick);
end

firstDataIdx = find(sum(isfinite(dataForDisplay),2) > 0, 1, 'first');
lastDataIdx = find(sum(isfinite(dataForDisplay),2) > 0, 1, 'last');
dataForPlotIdx = firstDataIdx:lastDataIdx;

% The last option specifies whether display anomaly in a separate panel
[x_opt, y_opt, z_opt, a_opt] = decodeDisplayOpt(displayOpt);

if a_opt
  dataForDisplay = simpleAnomaly(dataForDisplay,1);
end

colorOrder = {'b', 'g', 'r', 'm', 'c', 'k'};
markerOrder = {'s', 'o', 'd', 'v', '^', 'p', '>', '<', 'x', '*', 'h'};

Y_min = min(dataForDisplay(:));
Y_max = max(dataForDisplay(:));
Y_range = Y_max - Y_min;

figure(1);
clf;
for varI = 1:nVars
lin_style = [colorOrder{1 + mod(varI-1,6)} markerOrder{1 + mod(varI-1, 11)} '-'];
plot(dataForPlotIdx, dataForDisplay(dataForPlotIdx,varI), lin_style, 'linewidth', 2);
hold on;
end
if Y_range > 0
  ylim([Y_min, Y_max] + [-0.05 , nVars*0.05]*Y_range); 
end
xlabel('Year')
set(gca, 'fontweight', 'bold');
set(gca, 'xtick', x_tick_vec);
set(gca, 'xticklabel', x_label_str); 
grid on;
ylabel(['Mean (' v_units{1} ')']);
if nVars > 1
legend(lg_str, 'location', 'best');
title([long_name{1} ', regional average (' v_units{1} ')']);
else
title([long_name{1} ', average value over lon(' num2str(dataInfo(1).lonRange(1)) ',' num2str(dataInfo(1).lonRange(2)) ')deg, lat(' num2str(dataInfo(1).latRange(1)) ',' num2str(dataInfo(1).latRange(2)) ')deg, (' v_units{1} ')']);
end

if x_opt
  set(gca, 'xscale', 'log');
end
if y_opt | z_opt
  set(gca, 'yscale', 'log');
end
print(gcf, figFile, '-djpeg');

data.dimNames = {'monthIdx', 'varIdx'};
data.nDim = 2;
data.dimSize = [nMonths, nVars];
data.dimVars = {1:nMonths, 1:nVars};
data.var = dataForDisplay;
data.varName = dataInfo(1).varName;
data.dimVarUnits = {'month', 'N/A'};
data.varUnits = v_units{1};
data.varLongName = long_name{1};

status = 0;

if ~isempty(outputFile)
  status = storeDataInNetCDF(data, outputFile);
end
