function flag = dataFileRelevant(fn, startTime, stopTime);
%
% This function returns a true/false flag showing whether a data file is relevant
% for the temporal range specified.
%
% Input:
%   fn		-- file name
%   startTime	-- start time, a structure containing 'year', and 'month' fields
%   stopTime	-- stop time, a structure containing 'year', and 'month' fields
% Output:
%   flag	-- status flag: true(false) = data file does (not) contain data in the specified temporal range.
%
% Author: Chengxing Zhai
%
% Revision history:
%   2012/12/03:	Initial version, cz
%
[startTime_data, stopTime_data] = getStartAndStopDates(fn);
printf('start year = %f\n, month = %f\n', startTime_data.year, startTime_data.month);
printf('stop year = %f\n, month = %f\n', stopTime_data.year, stopTime_data.month);
flag = temporalRangeOverlap(startTime_data, stopTime_data, startTime, stopTime);
