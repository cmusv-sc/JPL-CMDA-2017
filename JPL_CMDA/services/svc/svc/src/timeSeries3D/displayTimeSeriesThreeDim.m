function status = displayTimeSeriesThreeDim(dataFile, figFile, varName, startTime, stopTime, thisPlev, lonRange, latRange)
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
%   lonRange	-- an optional argument to specify box boundary along longitude
%   latRange	-- an optional argument to specify box boundary along latitude
%   plevRange	-- an optional argumetn to specify the pressure level range
%
% Output:
%   status	-- a status flag, 0 = okay, -1 something is not right
%
% Author: Chengxing Zhai
%
% Revision history:
%   2012/12/10:	Initial version, cz
%   2012/02/06: Added more arguments to facilitate a customized regional and seasonal climatology
%   2012/02/25:	Added pressure level for computing average of a physical quantify distributed over a three dimensional space.
%
if nargin < 8
  latRange = [-90, 90];
end

if nargin < 7
  lonRange = [0, 360];
end 

status = -1;

nMonths = numberOfMonths(startTime, stopTime);

printf('number of month = %d\n', nMonths);

monthlyData = [];

nFiles = length(dataFile);

printf('number of files = %d\n', nFiles);
v = [];
lon = [];
lat = [];

for fileI = 1:nFiles
  fd = netcdf(dataFile{fileI}, 'r');

  varinfo = ncvar(fd);

  plevVarName = [];
  for ii = 1:length(varinfo)
    varNameList{ii} = ncname(varinfo{ii});
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
    lon = fd{'lon'}(:);
    lat = fd{'lat'}(:);
    if strcmp(plevVarName, 'plev')
      plev = fd{'plev'}(:);
    else
      p0 = 1.013e5; % 1atm = 1.013e5 Pa
      plev = fd{'lev'}(:)*p0;
    end
    [lon, lat, lonIdx, latIdx] = subIdxLonAndLat(lon, lat, lonRange, latRange);

    nLat = length(latIdx);
    monthlyData = nan(nMonths,1);
    [p_idx, p_alphas] = linearInterpHelper(thisPlev, plev, 'log');
  end

  v = fd{varName}(:);
  if ~isempty(fd{varName}.missing_value)
    v(abs(v - fd{varName}.missing_value) < 1) = NaN;
  end
  v_units = fd{varName}.units;
  v_units = adjustUnits(v_units, varName);
  [startTime_thisFile, stopTime_thisFile] = parseDateInFileName(dataFile{fileI});

  monthIdx1 = numberOfMonths(startTime, startTime_thisFile);
  monthIdx2 = numberOfMonths(startTime, stopTime_thisFile);

  nMonths_thisFile = size(v,1);

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

  disp(size(v));
  disp(latIdx);
  disp(lonIdx);
  monthlyData(monthIdx1:monthIdx2) = p_alphas(1) * meanExcludeNaN(meanExcludeNaN(squeeze(v(idx2Data_start:idx2Data_stop, p_idx(1), latIdx,lonIdx)),2),3);
  for pIdx = 2:length(p_idx)
    monthlyData(monthIdx1:monthIdx2) = monthlyData(monthIdx1:monthIdx2) + p_alphas(pIdx) * meanExcludeNaN(meanExcludeNaN(squeeze(v(idx2Data_start:idx2Data_stop, p_idx(pIdx), latIdx,lonIdx)),2),3);
  end
  ncclose(fd);
end

yearVec = startTime.year:stopTime.year;
nYears = length(yearVec);
yearStr = cell(nYears, 1);
for ii = 1:nYears
  yearStr{ii} = num2str(yearVec(ii));
end
deltaYear = 1+floor(nYears/12);

figure(1);
clf;
plot(1:nMonths, monthlyData, 's-', 'linewidth', 2);
xlabel('Year')
set(gca, 'xtick', [(2-startTime.month):12*deltaYear:nMonths]);
set(gca, 'xticklabel', {yearStr{1:deltaYear:end}}); 
set(gca, 'fontweight', 'bold');
grid on;
ylabel(['Mean (' v_units ')']);
title([varName ' at ' num2str(round(thisPlev/100)) 'hPa, average value over lon(' num2str(lonRange(1)) ',' num2str(lonRange(2)) ')deg, lat(' num2str(latRange(1)) ',' num2str(latRange(2)) ')deg, (' v_units ')']);
print(gcf, figFile, '-djpeg');
