function monthList = monthListWithin(startTime, stopTime, monthIdx)
%
% This utilty function returns the month list between start and stop time (including both start and end)
%
dYear = stopTime.year - startTime.year;

months = repmat(monthIdx(:)', 1, dYear+1) + reshape(repmat((0:dYear)*12, length(monthIdx),1), 1, []);

startMonth = startTime.month;
stopMonth = stopTime.month + dYear*12;

monthList = months(find(months >= startMonth & months <= stopMonth)) - startTime.month + 1;

