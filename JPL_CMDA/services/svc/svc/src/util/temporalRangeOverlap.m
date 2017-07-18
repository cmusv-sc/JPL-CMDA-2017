function overlap = temporalRangeOverlap(startTime1, stopTime1, startTime2, stopTime2)
%
% This function determines whether two temporal intervals overlap.
%
% Author: Chengxing Zhai
% Revision history:
%   2012/12/03:	Initial version, cz
%
overlap = ~earlierThan(stopTime1, startTime2) & ~laterThan(startTime1, stopTime2);
