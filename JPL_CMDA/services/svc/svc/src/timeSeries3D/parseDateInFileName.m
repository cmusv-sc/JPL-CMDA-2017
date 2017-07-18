function [startTime, stopTime] = parseDateInFileName(fileName)
%
% This function extract the dates from the file name according to
% CMIP5 convention, "yyyymm"
%
% Author: Chengxing Zhai
% Revision history:
%   2012/12/03:	Initial version, cz
%
dates = sscanf(fileName((end-15):end), '%d-%d.nc');
startTime.year = floor(dates(1)/100);
startTime.month = mod(dates(1),100);
stopTime.year = floor(dates(2)/100);
stopTime.month = mod(dates(2),100);
