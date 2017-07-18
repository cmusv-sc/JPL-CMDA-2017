function [startTime, stopTime] = parseDateInFileName(fileName)
%
% This function extract the dates from the file name according to
% CMIP5 convention, "yyyymm"
%
% Author: Chengxing Zhai
% Revision history:
%   2012/12/03:	Initial version, cz
%
date2 = str2num(fileName((end-8):(end-3)));
stopTime.year = floor(date2/100);
stopTime.month = mod(date2,100);

startTime = [];
if strcmp(fileName(end-9), '-') || strcmp(fileName(end-9), '-')
  date1 = str2num(fileName((end-15):(end-10)));
  if ~isempty(date1)
    startTime.year = floor(date1/100);
    startTime.month = mod(date1,100);
  end
end

if isempty(startTime)
  startTime = stopTime;
end
