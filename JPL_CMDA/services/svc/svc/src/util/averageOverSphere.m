function avg = averageOverSphere(data, lat, latRange, lon, lonRange, w)
%
% This function computes the average of data over sphere assuming that the first two dimensions
% are longitude and latitude respectively. It excludes data points that do not have valid values, e.g. NaN Inf
%
% Input:
%   data	-- lon x lat x optional dimensions
%   lat		-- latitude grid values
%   latRange	-- latitude range specifying the boundary of box in form of [min_lat, max_lat]
%   lon		-- longitude grid values
%   lonRange	-- longitude range specifiying the boundary of box in form of [min_lon, max_lon]
%   w		-- an optional weighting factor
%		-- longitude grid and range are optional
%
% Output:
%   avg		-- average of the data over the specified region
%  

dataSize = size(data);

cosLat = cos(lat*pi/180);

if nargin > 5
  w = w .* repmat(cosLat(:)', [dataSize(1),1]);
else
  w = repmat(cosLat(:)', [dataSize(1),1]);
end

repSize = dataSize; repSize(1:2) = 1; 
w = repmat(w, repSize);

w(~isfinite(data)) = 0;
data(~isfinite(data)) = 0;

if nargin > 4
  lonIdx = find(lon >= lonRange(1) & lon <= lonRange(2));
else
  lonIdx = 1:dataSize(1);
end

if nargin > 2
  latIdx = find(lat >= latRange(1) & lat <= latRange(2));
else
  latIdx = 1:dataSize(2);
end

data = reshape(data(lonIdx, latIdx,:), [], prod(dataSize(3:end)));
w = reshape(w(lonIdx, latIdx,:), [], prod(dataSize(3:end)));

avg = squeeze(sum(w .* data)) ./ sum(w);

if length(dataSize) > 3
  avg = reshape(avg, dataSize(3:end));
end
