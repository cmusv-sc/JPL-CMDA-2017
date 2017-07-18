function status = displayThreeDimZonalMean(dataFile, figFile, varName, startTime, stopTime, latRange, plevRange, monthIdx, outputFile, displayOpt)
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
%   latRnage	-- an optional argument to specify box boundary along latitude
%   plevRnage	-- an optional argument to specify pressule levels for alitutde range
%   monthIdx	-- an optional argument to specify months within a year, which is useful for computing climatology for a specific season.
%   outputFile	-- an optional argument to specify output file for storing the plotting data in netcdf format
%   displayOpt	-- an optional argument to specify the option for generating the figure
%
% Output:
%   status	-- a status flag, 0 = okay, -1 something is not right
%
% Author: Chengxing Zhai
%
% Revision history:
%   2012/03/25:	Initial version, cz
%   2013/06/14:	add capability of outputing data file
%
status = -1;

if nargin < 9
  displayOpt = 0;
end

if nargin < 9
  outputFile = [];
end

if nargin < 8
  monthIdx = 1:12;
end

if nargin < 7
  plevRange = [1100, 0]; % hPa, full column
end

if nargin < 6
  latRange = [-90, 90];
end

if plevRange(2)>plevRange(1)
	tmp=plevRange(1);
	plevRange(1)=plevRange(2);
	plevRange(2)=tmp;
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

    latIdx = find(lat <= latRange(2) & lat >= latRange(1));
    nLat = length(latIdx);
    lat = lat(latIdx);

    plev = readPressureLevels(thisFile, plevVarName);
    pIdx = find(plev >= plevRange(2) & plev <= plevRange(1));
    nP = length(pIdx);
    if (~strcmp(varName, 'ot') & ~strcmp(varName, 'os'))
    	plev = plev(pIdx)/100; % convert to hPa
    else
        plev = plev(pIdx)/1e4; % convert to dbar
    end

    monthlyData = nan(nLat, nP, nMonths);
  end

  v_units = ncreadatt(thisFile, varName, 'units');

  v_units = adjustUnits(v_units, varName);
  [startTime_thisFile, endTime_thisFile] = parseDateInFileName(dataFile{fileI});

  monthIdx1 = numberOfMonths(startTime, startTime_thisFile);
  monthIdx2 = numberOfMonths(startTime, endTime_thisFile);

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
  v = ncreadVar(thisFile, varName, [1, latIdx(1), pIdx(1), idx2Data_start], [length(lon), length(latIdx), length(pIdx), idx2Data_stop - idx2Data_start + 1]);
  monthlyData(:,:,monthIdx1:monthIdx2) = meanExcludeNaN(v,1);
  long_name = ncreadatt(thisFile, varName, 'long_name');
  clear v;
end

% We now determine the relevant months within a year using monthIdx and start month
monthIdxAdj = mod(monthIdx - startTime.month, 12) + 1;

var_clim = squeeze(simpleClimatology(monthlyData,3, monthIdxAdj));

[var_clim, lat, plev] = subsetValidData(var_clim, lat, plev);

colorLim = determineDisplayRange(var_clim);

if prod(colorLim) < 0
  cmap = myColorMap(colorLim);
else
  cmap = colormap('jet');
end

[x_opt, y_opt, z_opt] = decodeDisplayOpt(displayOpt);

if z_opt
  z = log10(var_clim' + 1e-4*max(var_clim(:)));
else
  z = var_clim';
end

if y_opt
  y = -log10(plev);
else
  y = -plev;
end

figure;
%contourf(lat, -plev, var_clim, 'linewidth', 2);
contourf(lat, y, z, 30, 'linecolor', 'none');
if ~isempty(find(isnan(var_clim(:))))
  cmap = colormap();
  cmap(1,:) = [1,1,1] * (double(prod(colorLim) >= 0));
end
colormap(cmap);
grid on;
set(gca, 'fontweight', 'bold');
currYTick = get(gca, 'ytick')';
currYTick(currYTick ~= 0) = - currYTick(currYTick ~= 0);
if y_opt
  set(gca, 'yticklabel', num2str(10.^currYTick));
else
  set(gca, 'yticklabel', num2str(currYTick));
end
xlabel('Latitude (deg)');
if (~strcmp(varName, 'ot') & ~strcmp(varName, 'os'))
	ylabel('Pressure level (hPa)');
else
	ylabel('Pressure level (dbar)');
end
cb = colorbar('southoutside');
if z_opt
  set(cb, 'xticklabel', num2str(10.^(get(cb, 'xtick')'),2));
end
set(get(cb,'xlabel'), 'string', [long_name '(' v_units ')'], 'FontSize', 16);
title([long_name ', ' date2Str(startTime, '/') '-' date2Str(stopTime, '/') ' zonal mean map climatology (' v_units '), ' seasonStr(monthIdx)], 'fontsize', 13, 'fontweight', 'bold');
print(gcf, figFile, '-djpeg');

data.dimNames = {'plev', 'latitude'};
data.nDim = 2;
data.dimSize = [length(lat), length(plev)];
data.dimVars = {lat, plev};
data.var = var_clim;
data.varName = varName;
if (~strcmp(varName, 'ot') & ~strcmp(varName, 'os'))
	data.dimVarUnits = {'degree_north', 'hPa'};
else
	data.dimVarUnits = {'degree_north', 'decibar'};
end
data.varUnits = v_units;
data.varLongName = long_name;

status = 0;

if ~isempty(outputFile);
  status = storeDataInNetCDF(data, outputFile);
end
