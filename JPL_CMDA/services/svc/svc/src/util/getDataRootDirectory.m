function dataDir = getDataRootDirectory(fileName)
%
% This function returns current data directory
%
% Input:
%   fileName	-- an optional data file name contains the data directory, the defaul file will be used
%		-- if not specified
% Output:
%   dataDir	-- return value of the data diretory

if nargin < 1
  fileName = '../../../data.cfg';
end

fid = fopen(fileName);

dataDir = fscanf(fid, '%s');

fclose(fid);
