function status = regridLonAndLat(inputFile, outputFile, varName, lon, lat)
%
% This function regrids data in input file according to the specified longitude
% an latitude and output the data to output file
%
status = -1;

% Let us get the information from the input file
inFileInfo = ncinfo(file_in);

data = ncread(inputFile, varName);

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

nLon = length(lon);
nLat = length(lat);

for fileI = 1:nFiles
  thisFile = dataFiles{fileI};
  if isempty(twoDimData.data)
    lon_data = ncread(thisFile, 'lon');
    lat_data = ncread(thisFile, 'lat');

    if isvector(lon_data) & isvector(lat_data)
      % Let us determine whether 
      [lonGrid_status, lonIdx] = isSubgrid(lon, lon_data);
      [latGrid_status, latIdx] = isSubgrid(lat, lat_data);
      if lonGrid_status & latGrid_status
        opt = 'subidxing';
      else
        opt = '2d_interp_reg';
        nLon_data = length(lon_data);
        nLat_data = length(lat_data);
      end
    else
      opt = '2d_interp_irreg';
      [nLon_data, nLat_data] = size(lon_data);
      lonlon = repmat(lon(:), 1, nLat);
      latlat = repmat(lat(:)', nLon, 1);
    end

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
    tmpData = v(:, :, idx2Data_start:idx2Data_stop);
  else
    tmpData = squeeze(meanExcludeNaN(v(:,:,pIdx,idx2Data_start:idx2Data_stop), 3));
  end

  switch opt
    case '2d_interp_reg',
      disp('regridding a regular 2-d grid');
      tic;
      for monthI = monthIdx1:monthIdx2
        twoDimData.data(:, :, monthI) = twoDimInterpOnSphere(lon_data, lat_data, squeeze(tmpData(:, :, monthI - monthIdx1 + 1)), lon, lat, 'linear');
      end
      toc;
    case '2d_interp_irreg',
      disp('regridding an irregular 2-d grid');
      tic;
      for monthI = monthIdx1:monthIdx2
        twoDimData.data(:, :, monthI) = griddata(lon_data, lat_data, squeeze(tmpData(:,:,monthI - monthIdx1 + 1)), lonlon, latlat, 'linear');
      end
      toc;
    case 'subidx',
      disp('subindexing a regular 2-d grid');
      tic;
      twoDimData.data(:, :, monthIdx1:monthIdx2) = tmpData(lonIdx, latIdx, :);
      toc;
    otherwise, % treating as sub indexing
      disp(['Other option: ' opt ', using sub indexing']);
      tic;
      twoDimData.data(:, :, monthIdx1:monthIdx2) = tmpData(lonIdx, latIdx, :);
      toc;
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

status = 0;
