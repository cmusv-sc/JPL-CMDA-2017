function status = displayTwoDimSlice(dataFile, figFile, varName, startTime, stopTime, thisPlev, lonRange, latRange, monthIdx, outputFile, displayOpt)
%
% This function extracts relevant data from the data file list according
% the specified temporal range [startTime, stopTime], longitude & latitude range, and seasonal months in a year
% of a 3-D field at the specified level.
%
% Input:
%   dataFile	-- a list of relevant data files
%   figFile	-- the name of the output file for storing the figure to be displayed
%   varName	-- the physical variable of interest, or to be displayed
%   startTime	-- the start time of the temporal window over which the climatology is computed
%   stopTime	-- the stop time of the temporal window over which the climatology is computed
%   thisPlev	-- pressure level to be displayed, a linear interpolation is used based on the log(pressure)		
%   lonRnage	-- an optional argument to specify box boundary along longitude
%   latRnage	-- an optional argument to specify box boundary along latitude
%   monthIdx	-- an optional argument to specify months within a year, which is useful for computing climatology for a specific season.
%   outputFile	-- an optional argument to specify the netcdf data filename for outputing 
%
% Output:
%   status	-- a status flag, 0 = okay, -1 something is not right
%
% Author: Chengxing Zhai
%
% Revision history:
%   2013/03/25:	Initial version, cz
%

if nargin < 10
  outputFile = [];
end

if nargin < 9
  monthIdx = 1:12;
end

if nargin < 8
  latRange = [-90, 90];
end

if nargin < 7
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

    [lon, lat, lonIdx, latIdx] = subIdxLonAndLat(lon, lat, lonRange, latRange);
    nLon = length(lon);
    nLat = length(lat);

    [p_idx, p_alphas] = linearInterpHelper(thisPlev, plev, 'log'); % get the layers relevant to the specified pressure level
    monthlyData = nan(nLon, nLat, nMonths, 'single');
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
  disp(lonIdx);
  
  nLon_tmp = length(lonIdx); nLat_tmp = length(latIdx); nP_tmp = length(p_idx);
  v = ncreadVar(thisFile, varName, [lonIdx(1), latIdx(1),p_idx(1), idx2Data_start], [nLon_tmp, nLat_tmp, nP_tmp, idx2Data_stop-idx2Data_start+1]);
  monthlyData(:,:, monthIdx1:monthIdx2) = reshape(v(:, :, 1, :), nLon_tmp, nLat_tmp, []) * p_alphas(1);
  for pIdx = 2:length(p_idx)
    monthlyData(:,:,monthIdx1:monthIdx2) = monthlyData(:,:,monthIdx1:monthIdx2) + reshape(v(:, :, pIdx, :), nLon_tmp, nLat_tmp, []) * p_alphas(pIdx);
  end
  long_name = ncreadatt(thisFile, varName, 'long_name');
  clear v;
end

% We now determine the relevant months within a year using monthIdx and start month

monthIdxAdj = mod(monthIdx - startTime.month, 12) + 1;

var_clim = squeeze(simpleClimatology(monthlyData,3, monthIdxAdj));

% x_opt, y_opt is ignored, it wuold be very rare to use log scale for longitude and latitude
[x_opt, y_opt, z_opt] = decodeDisplayOpt(displayOpt);

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
if z_opt
  set(cb, 'xticklabel', num2str(10.^(get(cb, 'xtick')'),3));
end
set(get(cb,'xlabel'), 'string', [long_name '(' v_units ')'], 'FontSize', 16);
plev_units = 'hPa';
if strcmp(varName, 'ot') || strcmp(varName, 'os') 
  plev_units = 'dbar';
end
title(h, [long_name ', at ' num2str(round(thisPlev/100)) plev_units ', ' date2Str(startTime, '/') '-' date2Str(stopTime, '/') ' climatology (' v_units '), ' seasonStr(monthIdx)]);
print(gcf, figFile, '-djpeg');

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
