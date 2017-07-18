function status = displayVerticalProfile(dataFile, figFile, varName, startTime, stopTime, lonRange, latRange, monthIdx, outputFile, displayOpt)
%
% This function extracts relevant data from the data file list according
% the specified temporal range [startTime, stopTime], longitude and latitude ranges
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
%   outputFile	-- an optional argument to specify data file name for outputing data used in plot
%
% Output:
%   status	-- a status flag, 0 = okay, -1 something is not right
%
% Author: Chengxing Zhai
%
% Revision history:
%   2012/12/10:	Initial version, cz
%   2012/02/06: Added more arguments to facilitate a customized regional and seasonal climatology
%   2013/06/14: Added capability for outputing plotting data
%

if nargin < 10
  displayOpt = 2; % only set the y to be log scale
end

if nargin < 9
  outputFile = [];
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
v = [];
lon = [];
lat = [];
plev = [];

for fileI = 1:nFiles
  thisFile = dataFile{fileI};
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
  if isempty(plevVarName)
    error('No variable for pressure level found!');
  end

  if isempty(monthlyData)
    lon = ncread(thisFile, 'lon');
    lat = ncread(thisFile, 'lat');

    plev = readPressureLevels(thisFile, plevVarName);
    nP = length(plev);
    if (~strcmp(varName, 'ot') & ~strcmp(varName, 'os'))
    	plev = plev/100; % convert to hPa
    else
        plev = plev/1e4; % convert to dbar
    end
    [lon, lat, lonIdx, latIdx] = subIdxLonAndLat(lon, lat, lonRange, latRange);
    nLon = length(lon);
    nLat = length(lat);

    monthlyData = nan(nP, nMonths, 'single');
  end

  v_units = ncreadatt(thisFile, varName, 'units');
  v_units = adjustUnits(v_units, varName);
  [startTime_thisFile, stopTime_thisFile] = parseDateInFileName(dataFile{fileI});

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

  disp(latIdx);
  %monthlyData(:, monthIdx1:monthIdx2) = squeeze(meanExcludeNaN(meanExcludeNaN(v(lonIdx, latIdx, :, idx2Data_start:idx2Data_stop),1),2));
  
  v = ncreadVar(thisFile, varName, [lonIdx(1), latIdx(1), 1, idx2Data_start], [length(lonIdx), length(latIdx), length(plev), idx2Data_stop - idx2Data_start + 1]);
  monthlyData(:, monthIdx1:monthIdx2) = squeeze(averageOverSphere(v, lat));
  long_name = ncreadatt(thisFile, varName, 'long_name');
  clear v;
end

% We now determine the relevant months within a year using monthIdx and start month
monthIdxAdj = mod(monthIdx - startTime.month, 12) + 1;

var_clim = squeeze(simpleClimatology(monthlyData,2, monthIdxAdj));

[var_clim, plev] = subsetValidData(var_clim, plev);

[x_opt, y_opt, z_opt] = decodeDisplayOpt(displayOpt);

figure;
y_plev = -plev;
if y_opt
  semilogy(var_clim, y_plev, 'ks-', 'linewidth', 2);
else
  plot(var_clim, y_plev, 'ks-', 'linewidth', 2);
end
if x_opt || z_opt
  set(gca, 'xscale', 'log');
end
grid on;
set(gca, 'fontweight', 'bold');
currYTick = pressureLevelTicks(min(y_plev), max(y_plev), 100);
set(gca, 'ytick', currYTick);
currYTick(currYTick ~= 0) = - currYTick(currYTick ~= 0);
set(gca, 'yticklabel', num2str(currYTick));
%xlabel(['Average (' v_units ')']);
xlabel([long_name ' (' v_units ')']);
if (~strcmp(varName, 'ot') & ~strcmp(varName, 'os'))
	ylabel('Pressure Level (hPa)');
else
	ylabel('Pressure Level (dbar)');
end
ylim([min(y_plev)-0.001, max(y_plev)+0.001]);

%xlim(max(var_clim)*[1e-4, 1.1]);
%xlim([min(var_clim)*0.9, max(var_clim)*1.1]);
title([varName ', ' date2Str(startTime, '/') '-' date2Str(stopTime, '/') ' vertical profile climatology (' v_units '), ' seasonStr(monthIdx)], 'fontsize', 13, 'fontweight', 'bold');
print(gcf, figFile, '-djpeg');

data.dimNames = {'plev'};
data.nDim = 1;
data.dimSize = [length(plev)];
if (~strcmp(varName, 'ot') & ~strcmp(varName, 'os'))
	data.dimVars = {plev/100};
	data.dimVarUnits = {'hPa'};
else
	data.dimVars = {plev};
	data.dimVarUnits = {'dbar'};
end
data.var = var_clim;
data.varName = varName;
data.varUnits = v_units;
data.varLongName = long_name;

status = 0;

if ~isempty(outputFile);
  status = storeDataInNetCDF(data, outputFile);
end
