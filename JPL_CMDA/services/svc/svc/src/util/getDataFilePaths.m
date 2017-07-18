function dataFileFullPath = getDataFilePaths(sourceName, varName, startTime, stopTime)

dataRootDir = [getDataRootDirectory() '/cmip5/'];

[center,model] = strtok(sourceName, '_');
model = model(2:end); % get rid of '_'

dataDir = [dataRootDir  center '/' model '/regridded/']; 
dataFiles = dir([dataDir '/' varName '_*.nc']);
nDataFiles = length(dataFiles);

% If no data, let us find the data at the defaul directory
if nDataFiles < 1
  dataDir = [dataRootDir  center '/' model '/break/']; 
  dataFiles = dir([dataDir '/' varName '_*.nc']);
  nDataFiles = length(dataFiles);
  if nDataFiles < 1
    dataDir = [dataRootDir  center '/' model '/']; 
    dataFiles = dir([dataDir '/' varName '_*.nc']);
    nDataFiles = length(dataFiles);
  end
end

if nDataFiles < 1
  error(['Variable: ' varName ' for data source: ' sourceName ' not found!']); 
end

dataFileFullPath = [];
idx = 1;
for ii = 1:nDataFiles
  thisFile = [dataDir '/' dataFiles(ii).name];
  if dataFileRelevant(thisFile, startTime, stopTime)
    dataFileFullPath{idx} = thisFile;
    idx = idx + 1;
  end
end
