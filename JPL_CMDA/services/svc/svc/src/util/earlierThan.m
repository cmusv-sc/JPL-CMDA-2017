function flag = earlierThan(time1, time2)
%
% A utility function facilitating the comparison of time structure
% that contains "year" and "month" data fields.
%
% Author: Chengxing Zhai
% Revision history:
%   2012/12/03:	Initial version, cz
%
flag = (time1.year < time2.year) | (time1.year == time2.year && time1.month < time2.month);
