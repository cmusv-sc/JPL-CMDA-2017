function status = displayTwoDimZonalMean(dataFile, figFile, varName, startTime, stopTime, latRange, monthIdx, outputFile, displayOpt)
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
%   latRnage	-- an optional argument to specify box boundary along latitude
%   monthIdx	-- an optional argument to specify months within a year, which is useful for computing climatology for a specific season.
%   outuptFile	-- an optional argument to specify output data file
%
% Output:
%   status	-- a status flag, 0 = okay, -1 something is not right
%
% Author: Chengxing Zhai
%
% Revision history:
%   2012/12/10:	Initial version, cz
%   2012/02/06: Added more arguments to facilitate a customized regional and seasonal climatology
%   2013/06/14: added extra argument to specify output data file name, in netcdf format
%
status = -1;

if nargin < 9
  displayOpt = 0; % this flag encodes the options for display
end

[x_opt, y_opt, z_opt] = decodeDisplayOpt(displayOpt);

if nargin < 8
  outputFile = [];
end

if nargin < 7
  monthIdx = 1:12;
end

if nargin < 6
  latRange = [-90, 90];
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

    latIdx = find(lat <= latRange(2) & lat >= latRange(1));
    nLat = length(latIdx);
    lat = lat(latIdx);

    monthlyData = nan(nLat, nMonths, 'single');
  end

  v_units = ncreadatt(thisFile, varName, 'units');

  [startTime_thisFile, stopTime_thisFile] = parseDateInFileName(dataFile{fileI});

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


  monthlyData(:, monthIdx1:monthIdx2) = meanExcludeNaN(ncreadVar(thisFile, varName, [1, latIdx(1), idx2Data_start], [length(lon), length(latIdx), idx2Data_stop - idx2Data_start + 1]), 1);
  long_name = ncreadatt(thisFile, varName, 'long_name');
end

% We now determine the relevant months within a year using monthIdx and start month
monthIdxAdj = mod(monthIdx - startTime.month, 12) + 1;

% We now determine the relevant time range used for this climatology calculation

[real_startTime, real_stopTime] = findRealTimeRange(file_start_time, file_stop_time, startTime, stopTime);

var_clim = squeeze(simpleClimatology(monthlyData,2, monthIdxAdj));
figure;
plot(lat, var_clim, 'ks-', 'linewidth', 2);
if x_opt
  set(gca, 'xscale', 'log');
end
if y_opt | z_opt
  set(gca, 'yscale', 'log');
end
grid on;
set(gca, 'fontweight', 'bold');
xlabel('Latitude (deg)');
%ylabel(['Zonal mean (' v_units ')']);
ylabel([ long_name ' (' v_units ')']);
title([varName ', ' date2Str(real_startTime, '/') '-' date2Str(real_stopTime, '/') ' zonal mean climatology (' v_units '), ' seasonStr(monthIdx)], 'fontsize', 13, 'fontweight', 'bold');
print(gcf, figFile, '-djpeg');

data.dimNames = {'latitude'};
data.nDim = 1;
data.dimSize = [length(lat)];
data.dimVars = {lat};
data.var = var_clim;
data.varName = varName;
data.dimVarUnits = {'degree_north'};
data.varUnits = v_units;
data.varLongName = long_name;

status = 0;

if ~isempty(outputFile);
  status = storeDataInNetCDF(data, outputFile);
end
