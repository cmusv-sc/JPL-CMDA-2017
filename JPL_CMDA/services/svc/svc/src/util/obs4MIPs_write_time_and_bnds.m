function [status, idx] = obs4MIPs_write_time_and_bnds(file, time_bnds, timeRef)
%
% This function generates latitude bounds and write both latitude and latitude bounds into
% netcdf file with the appropriate attributes from both latitude and latitude bounds
%
status = -1;

time = mean(time_bnds,2);

[time_ascent, idx] = sort(time);

nT = length(time);

if norm(time_ascent - time) > 0
  status = 1;
  warning('!!! time sampling points do not increase monotonically! Need to re-index the data');
  time = time_ascent;
end

nccreate(file, 'time', 'Dimensions', {'time', nT}, 'Datatype', 'double');
nccreate(file, 'time_bnds', 'Dimensions', {'bnds', 2, 'time', nT}, 'Datatype', 'double');

ncwriteatt(file, 'time', 'long_name', 'time');
ncwriteatt(file, 'time', 'standard_name', 'time');
ncwriteatt(file, 'time', 'axis', 'T');
ncwriteatt(file, 'time', 'units', ['days since ' datestr([timeRef.year, timeRef.month, timeRef.day, 0, 0, 0], 'yyyy-mm-dd')]);
ncwriteatt(file, 'time', 'calendar', 'julian');
ncwriteatt(file, 'time', 'bounds', 'time_bnds');

ncwrite(file, 'time', time);
ncwrite(file, 'time_bnds', time_bnds');

status = 0;

