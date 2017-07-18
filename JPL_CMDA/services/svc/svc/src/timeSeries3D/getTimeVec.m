function [years, months, indices] = getTimeVec(fileName)
%
% This function extracts the time points from the specified
% cmip5 netcdf data file using the calendar attributes and units
%
%

fd = netcdf(fileName, 'r');
cal = fd{'time'}.calendar;
ts = fd{'time'}(:);
unitsSpec = fd{'time'}.units;
close(fd);

date0 = sscanf(unitsSpec, 'days since %d-%d-%d');
[years, months, indices] = convertDaysFromADateToMonths(date0, ts, cal);

