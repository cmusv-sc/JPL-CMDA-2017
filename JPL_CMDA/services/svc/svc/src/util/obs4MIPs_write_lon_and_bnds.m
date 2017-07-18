function status = obs4MIPs_write_lon_and_bnds(file, lon)
%
% This function generates longitude bounds and write both longitude and longitude bounds into
% netcdf file with the appropriate attributes from both longitude and longitude bounds
%
status = 0;

if max(lon) > 360 || min(lon) < 0 
  status = 1;
  lon = mod(lon, 360); % make longintude between [0, 360]
  warning('!!! longitude has vales outside the nominal longitude range [0, 360)!');
end

[lon_ascent, idx] = sort(lon);

if norm(lon_ascent - lon) > 0
  status = 1;
  warning('!!! longitude is not monotonically increasing!');
  lon = lon_ascent;
end

nLon = length(lon);
lon_bnds = zeros(nLon, 2);

dlon = 0.5*(lon(2) - lon(1)); % assuming uniform grid

lon_bnds(:,1) = lon - dlon*0.5;
lon_bnds(:,2) = lon + dlon*0.5;

nccreate(file, 'lon', 'Dimensions', {'lon', nLon}, 'Datatype', 'double');
nccreate(file, 'lon_bnds', 'Dimensions', {'lon', nLon, 'bnds', 2}, 'Datatype', 'double');

ncwriteatt(file, 'lon', 'long_name', 'longitude');
ncwriteatt(file, 'lon', 'standard_name', 'longitude');
ncwriteatt(file, 'lon', 'axis', 'X');
ncwriteatt(file, 'lon', 'units', 'degrees_east');
ncwriteatt(file, 'lon', 'bounds', 'lon_bnds');

ncwrite(file, 'lon', lon(:));
ncwrite(file, 'lon_bnds', lon_bnds);
