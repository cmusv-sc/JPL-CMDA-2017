function v_regrid = threeDimMeshRegrid(v, thisLon, thisLat, thisP, lon, lat, plev, method);
%
% This function regrids data v, whose first three dimensions to be thisLon, thisLat, and thisPlev
% into the specified longitude (lon), latitude (lat), and pressure levels (plev),
% and keep the rest of the dimension the same.
%
if nargin < 8
  method = 'linear';
end

v_2d_regrid = lonLatMeshRegrid(v, thisLon, thisLat, lon, lat, method);

% We now regrid the vertical level
v_regrid = oneDimRegrid(v_2d_regrid, log(thisP), log(plev), 3, method);
