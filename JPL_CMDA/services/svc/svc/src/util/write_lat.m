function status = write_lat(file, lat)
%
% This function generates latitude bounds and write both latitude and latitude bounds into
% netcdf file with the appropriate attributes from both latitude and latitude bounds
%
status = 0;

nLat = length(lat);

nccreate(file, 'lat', 'Dimensions', {'lat', nLat}, 'Datatype', 'double');

ncwriteatt(file, 'lat', 'long_name', 'latitude');
ncwriteatt(file, 'lat', 'standard_name', 'latitude');
ncwriteatt(file, 'lat', 'axis', 'Y');
ncwriteatt(file, 'lat', 'units', 'degrees_north');

ncwrite(file, 'lat', lat(:));

