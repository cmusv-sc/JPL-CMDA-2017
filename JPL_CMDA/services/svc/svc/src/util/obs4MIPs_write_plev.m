function [status, idx] = obs4MIPs_write_plev(file, plev)
%
% This function write pressure levels into file and add the relevant attributes
% according to CMIP5 convention
%
plev = double(plev(:)); % make sure it is a row vector
status = 0;

if ~isempty(find(plev < 0))
  status = -1;
  error('*** negative pressure level exists!');
end


% Make sure that the pressure levels decrease monotonically.
[plev_descent, idx] = sort(plev, 'descend');

if norm(plev_descent - plev) > 0
  status = 1;
  warning('!!! pressure level does not monotonically decrease!');
  plev = plev_descent;
end

nP = length(plev);

nccreate(file, 'plev', 'Dimensions', {'plev', nP}, 'Datatype', 'double');

ncwriteatt(file, 'plev', 'long_name', 'pressure');
ncwriteatt(file, 'plev', 'standard_name', 'air_pressure');
ncwriteatt(file, 'plev', 'axis', 'Z');
ncwriteatt(file, 'plev', 'positive', 'down');
ncwriteatt(file, 'plev', 'units', 'Pa');

ncwrite(file, 'plev', plev);

