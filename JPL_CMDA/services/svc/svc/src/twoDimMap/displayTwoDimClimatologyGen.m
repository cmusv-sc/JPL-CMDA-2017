function status = displayTwoDimClimatologyGen(dataFile, figFile, varName, startTime, stopTime, lonRange, latRange, monthIdx, outputFile, displayOpt)
%
% This function extracts relevant data from the data file list according
% the specified temporal range [startTime, stopTime]
%
% Input:
%   dataFile	-- a list of relevant data files
%   figFile	-- the name of the output file for storing the figure to be displayed
%   varName	-- the physical variable of interest, or to be displayed
%   startTime	-- the start time of the temporal window over which the climatology is computed
%   stopTime	-- the stop time of the temporal window over which the climatology is computed
%   lonRnage	-- an optional argument to specify box boundary along longitude
%   latRnage	-- an optional argument to specify box boundary along latitude
%   monthIdx	-- an optional argument to specify months within a year, which is useful for computing climatology for a specific season.
%   outputData	-- an optional argument to determine whether to generate a data file
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

if nargin < 10
  displayOpt = 0;
end

if nargin < 9
  outputFile =  [];
end

if nargin < 8
  monthIdx = 1:12;
end

if nargin < 7
  latRange = [-90, 90];
end

if nargin < 6
  lonRange = [0, 360];
end 

nMonths = numberOfMonths(startTime, stopTime);

printf('number of month = %d\n', nMonths);

monthlyData = [];

nFiles = length(dataFile);

printf('number of files = %d\n', nFiles);
lon = [];
lat = [];
file_start_time = {};
file_stop_time = {};

for fileI = 1:nFiles
  thisFile = dataFile{fileI};

  if isempty(monthlyData)
    lon = ncread(thisFile, 'lon');
    lat = ncread(thisFile, 'lat');

    [lon, lat, lonIdx, latIdx] = subIdxLonAndLat(lon, lat, lonRange, latRange);
    nLon = length(lon);
    nLat = length(lat);

    long_name = ncreadatt(thisFile, varName, 'long_name');
    monthlyData = nan(nLon, nLat, nMonths, 'single');
  end

  v_units = ncreadatt(thisFile, varName, 'units');
  [startTime_thisFile, stopTime_thisFile] = parseDateInFileName(thisFile);

  file_start_time{fileI} = startTime_thisFile;
  file_stop_time{fileI} = stopTime_thisFile;

  monthIdx1 = numberOfMonths(startTime, startTime_thisFile);
  monthIdx2 = numberOfMonths(startTime, stopTime_thisFile);
  nMonths_thisFile = numberOfMonths(startTime_thisFile, stopTime_thisFile);

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

  monthlyData(:, :, monthIdx1:monthIdx2) = ncreadVar(thisFile, varName, [lonIdx(1), latIdx(1), idx2Data_start], [length(lonIdx), length(latIdx), idx2Data_stop - idx2Data_start + 1]);
end

% We now determine the relevant months within a year using monthIdx and start month

monthIdxAdj = mod(monthIdx - startTime.month, 12) + 1;

% We now determine the relevant time range used for this climatology calculation

[real_startTime, real_stopTime] = findRealTimeRange(file_start_time, file_stop_time, startTime, stopTime);

% x_opt, y_opt is ignored, it wuold be very rare to use log scale for longitude and latitude
[x_opt, y_opt, z_opt] = decodeDisplayOpt(displayOpt);

var_clim = squeeze(simpleClimatology(monthlyData,3, monthIdxAdj));
if z_opt
  z = log10(var_clim + 1e-4*max(var_clim(:)));
  cfgParams.logScale = true;
else
  z = var_clim;
end
cfgParams.xlabelOff = false;
cfgParams.ylabelOff = false;
figure;
[h, cb] = displayTwoDimData(lon, lat, z, gca, cfgParams);
title(h, [long_name ', ' date2Str(real_startTime, '/') '-' date2Str(real_stopTime, '/') ' climatology (' v_units '), ' seasonStr(monthIdx)]);
if z_opt
  set(cb, 'xticklabel', num2str(10.^(get(cb, 'xtick')'),3));
end
set(get(cb,'xlabel'), 'string', [long_name ' (' v_units ')'], 'FontSize', 16);
print(gcf, figFile, '-djpeg');
% adding title for color bar

data.dimNames = {'longitude', 'latitude'};
data.nDim = 2;
data.dimSize = [length(lon), length(lat)];
data.dimVars = {lon, lat};
data.var = var_clim;
data.varName = varName;
data.dimVarUnits = {'degree_east', 'degree_north'};
data.varUnits = v_units;
data.varLongName = long_name;

status = 0;

if ~isempty(outputFile);
  status = storeDataInNetCDF(data, outputFile);
end
