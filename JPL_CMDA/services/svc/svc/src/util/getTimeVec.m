function [years, months, indices] = getTimeVec(fileName)
%
% This function extracts the time points from the specified
% cmip5 netcdf data file using the calendar attributes and units
%
%

ts = ncread(fileName, 'time');
if hasAttribute(fileName, 'time', 'calendar')
  cal = ncreadatt(fileName, 'time', 'calendar');
else
  cal = 'gregorian';
  warning('!!! no calendar attribute, using Gregorian!');
end
unitsSpec = ncreadatt(fileName, 'time', 'units');

[units_str, str_res] = strtok(unitsSpec);
date0 = sscanf(str_res, ' since %d-%d-%d');

switch lower(units_str)
   case 'hours',
     ts = ts/24;
   case 'days',
     % doing nothing
   otherwise,
     warning(['!!! Unknown time units string: ' unts_str ' , days assumed.']);
end
[years, months, indices] = convertDaysFromADateToMonths(date0, ts, cal);

