function folderName = getDataDirectory(scriptName)
% This function helps a script to find its own data directory
% The covention is that the data directory for
%   xxx/scriptName.m
% is
%   xxx/data/
%

folderName = strrep(which(scriptName), [scriptName '.m'], ['data' filesep]);
