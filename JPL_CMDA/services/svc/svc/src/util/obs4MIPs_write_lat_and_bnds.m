function status = obs4MIPs_write_lat_and_bnds(file, lat)
%
% This function generates latitude bounds and write both latitude and latitude bounds into
% netcdf file with the appropriate attributes from both latitude and latitude bounds
%
status = 0;

if abs(lat) > 90
  status = -1;
  error('!!! latitude has vales outside the range [-90, 90]!');
end

[lat_ascent, idx] = sort(lat);

if norm(lat_ascent - lat) > 0
  status = 1;
  warning('!!! latitude does not monotonically increase!');
  lat = lat_ascent;
end

nLat = length(lat);
lat_bnds = zeros(nLat, 2);

dlat = 0.5*(lat(2) - lat(1)); % assuming uniform grid

lat_bnds(:,1) = lat - dlat*0.5;
lat_bnds(:,2) = lat + dlat*0.5;

% limit lat_bnds to +/-90
lat_bnds(lat_bnds > 90) = 90;
lat_bnds(lat_bnds < -90) = -90;

nccreate(file, 'lat', 'Dimensions', {'lat', nLat}, 'Datatype', 'double');
nccreate(file, 'lat_bnds', 'Dimensions', {'lat', nLat, 'bnds', 2}, 'Datatype', 'double');

ncwriteatt(file, 'lat', 'long_name', 'latitude');
ncwriteatt(file, 'lat', 'standard_name', 'latitude');
ncwriteatt(file, 'lat', 'axis', 'Y');
ncwriteatt(file, 'lat', 'units', 'degrees_north');
ncwriteatt(file, 'lat', 'bounds', 'lat_bnds');

ncwrite(file, 'lat', lat(:));
ncwrite(file, 'lat_bnds', lat_bnds);

