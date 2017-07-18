function [startTime, stopTime] = getStartAndStopDates(fileName, useFileName)
%
% This function extract the dates from the file name according to
% CMIP5 convention, "yyyymm"
%
% Author: Chengxing Zhai
% Revision history:
%   2012/12/03:	Initial version, cz
%
if nargin < 2
  useFileName = false;
end

if useFileName
  [startTime, stopTime] = parseDateInFileName(fileName);
else
  [years, months, days] = getTimeVec(fileName);
  startTime.year = years(1);
  startTime.month = months(1);
  stopTime.year = years(end);
  stopTime.month = months(end);
end
