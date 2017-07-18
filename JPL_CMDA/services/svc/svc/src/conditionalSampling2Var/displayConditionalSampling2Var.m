function status = displayConditionalSampling2Var (dataFile, varName, startTime, stopTime, lonRange, latRange, monthIdx, plevRange, largeScaleDataFile1, largeScaleVarName1, largeScaleValueBinB1, largeScalePlev1, largeScaleDataFile2, largeScaleVarName2, largeScaleValueBinB2, largeScalePlev2, outputFile, figFile, displayOpt)
%
% This function extracts relevant data from the data file list according
% the specified temporal range [startTime, stopTime]
%
% Input:
%   dataFile	-- a list of relevant data files
%   figFile	-- the name of the output file for storing the figure to be displayed
%   varName	-- the physical variable of interest, or to be displayed, CMIP5 variable name used in netcdf file
%   startTime	-- the start time of the temporal window over which the climatology is computed, string 'yyyymm'
%   stopTime	-- the stop time of the temporal window over which the climatology is computed, string 'yyyymm'
%   lonRnage	-- longitude boundary specification, expect [min, max] (deg)
%   latRnage	-- latitude boundary specification, expect [min, max] (deg)
%   monthIdx	-- specify months within a year, which is useful for computing climatology for a specific season.
%   plevRange	-- presssure level range in units of (Pa)
%   largeScaleDataFile	-- a list of relevant large scale data files
%   largeScaleVarName	-- CMIP5 name for the large scale variable
%   largeScaleValueBinB	-- bin boundary specification, either as a vector of bin boundaries or [min,max,nBin]
%   largeScalePlev	-- pressure level for the large scale variable, e.g. vertical velocity at 50000Pa
%   outputFile	-- a data file for storing plotting data in netcdf format
%   displayOpt	-- flags to specify display scale, linear vs logarithmic, 3-bits, in the order (z,y,x), 0=lin, 1=log, 
%
% Output:
%   status	-- a status flag, 0 = okay, -1 something is not right
%
% Author: Chengxing Zhai
%
% Revision history:
%   2013/09/30:	Initial version, cz
%
status = -1;

if nargin < 19
  displayOpt = 0;
end

% Need to read out first the data to be sorted
nMonths = numberOfMonths(startTime, stopTime);
monthList = monthListWithin(startTime, stopTime, monthIdx);

printf('number of month = %d\n', nMonths);

monthlyData = [];

% Let us first assume the same grid
% We now sort the large scale variable aaccording to the bin
% sorted data mean and stddev for each bin
v_sorted_m = [];
v2_sorted_m = [];
v_sorted_std = [];

dataIsTwoDim = false;

nFiles = length(dataFile);
printf('number of files = %d\n', nFiles);
lon = [];
lat = [];

file_start_time = {};
file_end_time = {};

for fileI = 1:nFiles
  thisFile = dataFile{fileI};

  if isempty(v_sorted_m)
    lon = ncread(thisFile, 'lon');
    lat = ncread(thisFile, 'lat');

    [lon, lat, lonIdx, latIdx] = subIdxLonAndLat(lon, lat, lonRange, latRange);
    nLon = length(lon);
    nLat = length(lat);

    largeScaleVarData = cell(2,1);

    % This loads the large scale variabe data
    largeScaleVarData{1} = readAndRegridTwoDimData(largeScaleDataFile1, largeScaleVarName1, startTime, stopTime, lon, lat, largeScalePlev1);
    largeScaleVarData{2} = readAndRegridTwoDimData(largeScaleDataFile2, largeScaleVarName2, startTime, stopTime, lon, lat, largeScalePlev2);

    largeScaleVarNames = {largeScaleVarName1, largeScaleVarName1};

    nBinB = [length(largeScaleValueBinB1), length(largeScaleValueBinB2)];
    largeScaleValueBinB = {largeScaleValueBinB1, largeScaleValueBinB2};
    for ii = 1:2
      if nBinB(ii) <= 0
        largeScaleValueBinB{ii} = generateBinB(largeScaleVarData{ii}.data(:), 20);
      elseif nBinB(ii) == 1
        largeScaleValueBinB{ii} = generateBinB(largeScaleVarData{ii}.data(:), largeScaleValueBinB{1});
      elseif nBinB(ii) == 2
        largeScaleValueBinB{ii} = linspace(largeScaleValueBinB{ii}(1), largeScaleValueBin{ii}(2), 10 + 1);
      elseif nBinB(ii) == 3
        if largeScaleValueBin{ii}(3) <= 0
          largeScaleValueBinB{ii} = generateBinB(largeScaleVarData{ii}.data(:), 20);  
        else
          largeScaleValueBinB{ii} = linspace(largeScaleValueBinB{ii}(1), largeScaleValueBin{ii}(2), largeScaleValueBin{ii}(3) + 1);
        end
      end
      nBinB(ii) = length(largeScaleValueBinB{ii});
    end
    nBins = nBinB - 1;

    n_sorted = zeros(nBins);

    [idxArrayForEachBin, binCenterValues, nSamples] = generateIdxForBins2(largeScaleValueBinB, largeScaleVarData);

    if isempty(plevRange)
      dataIsTwoDim = true;
      nP = 1;
    elseif max(plevRange) <= 0
      dataIsTwoDim = true;
      nP = 1;
    else
      dataIsTwoDim = false;
      plev = readPressureLevels(thisFile, 'plev');
      if length(plevRange) == 1
        [mV, mIdx] = min(abs(plevRange - plev));
      else
        mIdx = find(plev >= min(plevRange) & plev <= max(plevRange));
      end
      plev = plev(mIdx);
      nP = length(plev);
    end

    long_name = ncreadatt(thisFile, varName, 'long_name');

    v_sorted_m = zeros(nBins, 'single');
    v2_sorted_m = zeros(nBins, 'single');
    v_sorted_std = zeros(nBins, 'single');
    n_sorted_valid = zeros(nBins, 'single');
  end


  v_units = ncreadatt(thisFile, varName, 'units');

  [startTime_thisFile, endTime_thisFile] = parseDateInFileName(dataFile{fileI});

  file_start_time{fileI} = startTime_thisFile;
  file_end_time{fileI} = endTime_thisFile;

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
  monthListThisFile = find(monthList >= monthIdx1 & monthList <= monthIdx2);
  nMonthInThisFile = length(monthListThisFile);

  timeIdx = idx2Data_start:idx2Data_stop;
  for monthI = 1:nMonthInThisFile
    thisMonth = monthListThisFile(monthI);
    if dataIsTwoDim
      thisTwoDimSlice = ncreadVar(thisFile, varName, [lonIdx(1), latIdx(1), timeIdx(monthI)], [length(lonIdx), length(latIdx), 1]);
    else
      thisTwoDimSlice = meanExcludeNaN(ncreadVar(thisFile, varName, [lonIdx(1), latIdx(1), mIdx(1), timeIdx(monthI)], [length(lonIdx), length(latIdx), length(mIdx), 1]), 3); % average over relevant levels
    end
    for binI1 = 1:nBins(1)
      for binI2 = 1:nBins(2)
        idx_thisBin = idxArrayForEachBin{binI1, binI2};
        idx_in_thisFile = mod(idx_thisBin(find(idx_thisBin > (thisMonth-1)*nLat*nLon & idx_thisBin <= thisMonth*nLat*nLon))-1, nLat*nLon) + 1;

        dataInThisBin = thisTwoDimSlice(idx_in_thisFile);
        dataValidIdx = find(isfinite(dataInThisBin));
        n_sorted_valid(binI1,binI2) = n_sorted_valid(binI1,binI2) + length(dataValidIdx);
        v_sorted_m(binI1, binI2) = v_sorted_m(binI1, binI2) + sum(dataInThisBin(dataValidIdx));
        v2_sorted_m(binI1, binI2) = v2_sorted_m(binI1, binI2) + sum(dataInThisBin(dataValidIdx).^2);
      end
    end
  end
end

v_sorted_m = v_sorted_m ./ n_sorted_valid;
v2_sorted_m = v2_sorted_m ./ n_sorted_valid;
v_sorted_stdsq = (v2_sorted_m - v_sorted_m.^2) ./ (n_sorted_valid - 1);
v_sorted_std = zeros(size(v_sorted_stdsq), 'single');
v_sorted_std(v_sorted_stdsq >= 0) = sqrt(v_sorted_stdsq (v_sorted_stdsq >= 0));

% We now determine the relevant time range used for this climatology calculation
[real_startTime, real_stopTime] = findRealTimeRange(file_start_time, file_end_time, startTime, stopTime);

[x_opt, y_opt, z_opt] = decodeDisplayOpt(displayOpt);
titleStr = [long_name ', sorted by ' largeScaleVarData{1}.name ' and ' largeScaleVarData{2}.name ', ' date2Str(startTime, '/') '-' date2Str(stopTime, '/')];

for ii = 1:2
if isfield(largeScaleVarData{ii}, 'plev')
  if (~strcmp(largeScaleVarNames{ii}, 'ot') & ~strcmp(largeScaleVarNames{ii}, 'os'))
    labelStr{ii} = [largeScaleVarData{ii}.name ' at ' num2str(round(mean(largeScaleVarData{ii}.plev)/100)) 'hPa (' largeScaleVarData{ii}.units ')' ]
  else
    labelStr{ii} = [largeScaleVarData{ii}.name ' at ' num2str(round(mean(largeScaleVarData{ii}.plev)/10000)) 'dbar (' largeScaleVarData{ii}.units ')' ]
  end
else
  labelStr{ii} = [largeScaleVarData{ii}.name '(' largeScaleVarData{ii}.units ')' ];
end
end

% we comment the display portion, python code will create the figure
if false
figure;

if z_opt
  z = log10(v_sorted_m' + 1e-4*(max(v_sorted_m(:)))); % to have dynamic range of 10^4
else
  z = v_sorted_m';
end

if y_opt
  y = log10(binCenterValues{2});
else
  y = binCenterValues{2};
end

if x_opt
  x = log10(binCenterValues{1});
else
  x = binCenterValues{1};
end

[z_valid, y_valid, x_valid] = subsetValidData(z, y, x);

gFilter = gaussianFilter(3, 1);

badDataFrac = sum(sum(~isfinite(z_valid)))/length(z_valid(:));
if badDataFrac > 0.2
  surface(x_valid, y_valid, z_valid, 'linestyle', 'none', 'edgecolor', 'none');
else
  if badDataFrac < 0.02
    if badDataFrac < 0.005
      gFilter = gaussianFilter(5, 1.5);
    end
    surface(interpGrid(x_valid, 2), interpGrid(y_valid,2), filter2(gFilter, interp2(z_valid, 2)), 'linestyle', 'none', 'edgecolor', 'none');
  else
    surface(interpGrid(x_valid, 2), interpGrid(y_valid,2), interp2(z_valid, 2), 'linestyle', 'none', 'edgecolor', 'none');
  end
end
hold on;
[c2, h2] = contour3(interpGrid(x_valid, 2), interpGrid(y_valid,2), filter2(gFilter, interp2(n_sorted_valid,2)'));
ylim([min(interpGrid(y_valid, 2)), max(interpGrid(y_valid, 2))]);
set(gca, 'yticklabel', num2str(get(gca, 'ytick')'));
xlim([min(interpGrid(x_valid, 2)), max(interpGrid(x_valid, 2))]);
set(h2, 'linecolor', [0.1, 0.1, 0.1], 'linewidth', 1);
set(h2, 'levellistmode', 'manual');
l_list = round(get(h2, 'levellist')/10)*10;
set(h2, 'levellistmode', 'manual');
set(h2, 'levellist', l_list);
clabel(c2, h2, l_list(1:2:end), 'fontsize', 12, 'fontweight', 'bold', 'color', [0, 0, 0], 'rotation', 0);
set(h2,'ShowText','on','TextStep',get(h2,'LevelStep')*2)

if ~isempty(find(isnan(v_sorted_m(:))))
  cmap = colormap();
  cmap(1,:) = [1,1,1];
  colormap(cmap);
end
grid on;
set(gca, 'fontweight', 'bold');
if y_opt
  set(gca, 'yticklabel', num2str(10.^(currYTick)));
end
ylabel(labelStr{2});
if x_opt
  currXTick = get(gca, 'xtick')';
  set(gca, 'xticklabel', num2str(10.^(currXTick))); % 
end
xlabel(labelStr{1});
  
cLim = [min(z_valid(:)), max(z_valid(:))];
caxis(cLim);
if prod(cLim) < 0
  colormap(myColorMap(cLim, 'lin0'));
end
cb = colorbar('southoutside');
if z_opt
  set(cb, 'xticklabel', num2str(10.^(get(cb, 'xtick')'),3));
end
set(get(cb,'xlabel'), 'string', [long_name '(' v_units ')'], 'FontSize', 16);

title(titleStr, 'fontsize', 13, 'fontweight', 'bold');
%print(gcf, figFile, '-djpeg');
% adding title for color bar
end

if strcmp(largeScaleVarName1, largeScaleVarName2)
  data.dimNames = {[largeScaleVarName1 'Bin1'], [largeScaleVarName2 'Bin2']};
else
  data.dimNames = {[largeScaleVarName1 'Bin'], [largeScaleVarName2 'Bin']};
end
data.nDim = 2;
data.dimSize = nBins;
data.dimVars = binCenterValues;
data.vars = {v_sorted_m, n_sorted_valid, v_sorted_std}
data.varName = varName;
data.dimVarUnits = {largeScaleVarData{1}.v_units, largeScaleVarData{2}.v_units};
data.varNames = {varName, [varName '_nSample'], [varName '_std']};
data.varUnits = {v_units, '1', v_units};
data.varLongNames = {long_name, [long_name ' number of samples in bins'], [long_name ' standard deviations']};
data.globalAtts(1).Name = 'title';
data.globalAtts(1).Value = titleStr;
data.globalAtts(2).Name = 'x_labelStr';
data.globalAtts(2).Value = labelStr{1};
data.globalAtts(3).Name = 'y_labelStr';
data.globalAtts(3).Value = labelStr{2};

status = 0;

if ~isempty(outputFile);
  status = storeGroupDataInNetCDF(data, outputFile);
end
