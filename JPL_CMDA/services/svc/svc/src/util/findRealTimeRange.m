function [real_startTime, real_stopTime] = findRealTimeRange(file_start_time, file_stop_time, startTime, stopTime)
%
% This function extract the real time range used to create the climatology data
%
% Author: Seungwon Lee
% Revision history:
%   2013/07/17:	Initial version
%

if length(file_start_time)==1
	real_startTime = findLaterTime(file_start_time{1}, startTime);
	real_stopTime = findEarlierTime(file_stop_time{1}, stopTime);	
else
	file_first_time = file_start_time{1};
	file_last_time = file_stop_time{1};
	for i=2:length(file_start_time)
		file_first_time = findEarlierTime(file_first_time, file_start_time{i});
		file_last_time = findLaterTime(file_last_time, file_stop_time{i});
	end
	real_startTime = findLaterTime(file_first_time, startTime);
	real_stopTime = findEarlierTime(file_last_time, stopTime);	
end
