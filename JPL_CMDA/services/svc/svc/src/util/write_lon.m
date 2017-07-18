function status = write_lon(file, lon)
%
% This function generates longitude bounds and write both longitude and longitude bounds into
% netcdf file with the appropriate attributes from both longitude and longitude bounds
%
status = 0;

nLon = length(lon);

nccreate(file, 'lon', 'Dimensions', {'lon', nLon}, 'Datatype', 'double');

ncwriteatt(file, 'lon', 'long_name', 'longitude');
ncwriteatt(file, 'lon', 'standard_name', 'longitude');
ncwriteatt(file, 'lon', 'axis', 'X');
ncwriteatt(file, 'lon', 'units', 'degrees_east');

ncwrite(file, 'lon', lon(:));
