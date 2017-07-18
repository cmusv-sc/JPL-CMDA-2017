function status = displayTimeSeriesTwoDim(dataFile, figFile, varName, startTime, stopTime, lonRange, latRange, outputFile, displayOpt)
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

if nargin < 9
  displayOpt = 0;
end

if nargin < 8
  outputFile = [];
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

for fileI = 1:nFiles
  thisFile = dataFile{fileI};

  if isempty(monthlyData)
    lon = ncread(thisFile, 'lon');
    lat = ncread(thisFile, 'lat');

    [lon, lat, lonIdx, latIdx] = subIdxLonAndLat(lon, lat, lonRange, latRange);

    nLat = length(latIdx);
    monthlyData = nan(nMonths,1);
  end

  v_units = ncreadatt(thisFile, varName, 'units');
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

  %disp(size(v));
  %disp(latIdx);
  %disp(lonIdx);
  %monthlyData(monthIdx1:monthIdx2) = meanExcludeNaN(meanExcludeNaN(v(idx2Data_start:idx2Data_stop,latIdx,lonIdx),2),3);
  v = ncreadVar(thisFile, varName, [lonIdx(1), latIdx(1), idx2Data_start], [length(lonIdx), length(latIdx), idx2Data_stop - idx2Data_start + 1]);
  monthlyData(monthIdx1:monthIdx2) = averageOverSphere(v, lat);
  long_name = ncreadatt(thisFile, varName, 'long_name');
  clear v;
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

[x_opt, y_opt, z_opt] = decodeDisplayOpt(displayOpt);

figure(1);
clf;
plot(1:nMonths, monthlyData, 's-', 'linewidth', 2);
xlabel('Year')
set(gca, 'fontweight', 'bold');
set(gca, 'xtick', x_tick_vec);
set(gca, 'xticklabel', x_label_str);
grid on;
ylabel(['Mean (' v_units ')']);
title(strrep([varName ', average value over lon(' num2str(lonRange(1)) ',' num2str(lonRange(2)) ')deg, lat(' num2str(latRange(1)) ',' num2str(latRange(2)) ')deg, (' v_units ')'], '_', '\_'));
if x_opt
  set(gca, 'xscale', 'log');
end
if y_opt | z_opt
  set(gca, 'yscale', 'log');
end
print(gcf, figFile, '-djpeg');

data.dimNames = {'monthIdx'};
data.nDim = 1;
data.dimSize = [nMonths];
data.dimVars = {1:nMonths};
data.var = monthlyData;
data.varName = varName;
data.dimVarUnits = {'month'};
data.varUnits = v_units;
data.varLongName = long_name;

status = 0;

if ~isempty(outputFile);
  status = storeDataInNetCDF(data, outputFile);
end
