function [lon_sub, lat_sub, lonIdx, latIdx] = subIdxLonAndLat (lon, lat, lonRange, latRange)
%
% This function returns a set of the longitude and latitude grid index that are within the
% specified longitude and latitude range. Note that we allow user to specify the longitude
% range with values in interval [-360, 360]
%
%
% Input:
%   lon		-- longitude grid
%   lat		-- latitude grid
%   lonRange	-- a 2x1 or 1x2 vector specifying the range of longitude of interest in format
%		-- [lon_min, lon_max]
%   latRange	-- a 2x1 or 1x2 vector specifying the range of longitude of interest in format
%		-- [lat_min, lat_max]
%
% Output:
%   lon_sub	-- subgrid of longitude
%   lat_sub	-- subgrid of latitude
%   lonIdx	-- index to longitude grid for points within the longitude range
%   latIdx	-- index to longitude grid for points within the latitude range


% Let us first find latitude index
latIdx = find(lat <= latRange(2) & lat >= latRange(1));
lat_sub = lat(latIdx);

% We need to handle the case when the longitude has negative values wrapping around 0
if lonRange(1) >= 0
  lonIdx = find(lon <= lonRange(2) & lon >= lonRange(1));
  lon_sub = lon(lonIdx);
else
  lon_neg = lon - 360;
  if lonRange(2) < 0
    lonIdx = find(lon_neg <= lonRange(2) & lon_neg >= lonRange(1));
    lon_sub = lon_neg(lonIdx);
  else
    lonIdx = find(lon <= lonRange(2));
    lonIdx_neg = find(lon_neg >= lonRange(1));
    lon_sub = [lon_neg(lonIdx_neg); lon(lonIdx)];
    lonIdx = [lonIdx_neg; lonIdx];
  end
end
