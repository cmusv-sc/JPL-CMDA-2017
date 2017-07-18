function twoDimData = readTwoDimData(dataFiles, varName, startTime, stopTime, lonRange, latRange, pRange)
%
% This function reads two dimensional data from netcdf files and concatenate along the
% time dimension (3rd dimension)
%
status = -1;

% Need to read out first the data to be sorted

nMonths = numberOfMonths(startTime, stopTime);

printf('number of month = %d\n', nMonths);

if isempty(pRange)
  noVertDim = true;
else
  noVertDim = (max(pRange) <= 0);
end

twoDimData.data = [];

nFiles = length(dataFiles);

for fileI = 1:nFiles
  thisFile = dataFiles{fileI};
  if isempty(twoDimData.data)
    lon = ncread(thisFile, 'lon');
    lat = ncread(thisFile, 'lat');
    [lon, lat, lonIdx, latIdx] = subIdxLonAndLat(lon, lat, lonRange, latRange);
    nLon = length(lon);
    nLat = length(lat);

    twoDimData.name = ncreadatt(thisFile, varName, 'long_name');
    twoDimData.units = ncreadatt(thisFile, varName, 'units');
    twoDimData.data = nan(nLon, nLat, nMonths, 'single');

    % Check 3-d
    if ~noVertDim
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
        noVertDim = true;
        warning('No variable for pressure level found, assuming two dimensional field');
      else
        plev = readPressureLevels(thisFile, plevVarName);
        if length(pRange) == 1
          [mV, pIdx] = min(abs(plev - pRange));
        else
          pIdx = find(plev >= min(pRange) & plev <= max(pRange));
        end
      end
    end
  end

  v = single(ncread(thisFile, varName));
  if hasAttribute(thisFile, varName, 'missing_value')
    missingValue = ncreadatt(thisFile, varName, 'missing_value');
    v(abs(v - missingValue) < 1) = NaN;
  end
  if hasAttribute(thisFile, varName, '_FillValue')
    missingValue = ncreadatt(thisFile, varName, '_FillValue');
    v(abs(v - missingValue) < 1) = NaN;
  end

  twoDimData.v_units = ncreadatt(thisFile, varName, 'units');

  [startTime_thisFile, stopTime_thisFile] = parseDateInFileName(thisFile);

  file_start_time{fileI} = startTime_thisFile;
  file_stop_time{fileI} = stopTime_thisFile;

  monthIdx1 = numberOfMonths(startTime, startTime_thisFile);
  monthIdx2 = numberOfMonths(startTime, stopTime_thisFile);

  if noVertDim
    nMonths_thisFile = size(v,3);
  else
    nMonths_thisFile = size(v,4);
  end

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

  if noVertDim
    twoDimData.data(:, :, monthIdx1:monthIdx2) = v(lonIdx, latIdx, idx2Data_start:idx2Data_stop);
  else
    twoDimData.data(:, :, monthIdx1:monthIdx2) = squeeze(meanExcludeNaN(v(lonIdx, latIdx, pIdx, idx2Data_start:idx2Data_stop), 3));
  end
  clear v;
end

twoDimData.lon = lon;
twoDimData.lat = lat;
twoDimData.startTime = startTime;
twoDimData.stopTime = stopTime;
if ~noVertDim
  twoDimData.plev = plev(pIdx);
end

