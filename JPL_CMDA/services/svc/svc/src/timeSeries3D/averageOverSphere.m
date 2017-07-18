function avg = averageOverSphere(data, lat, latRange, lon, lonRange, w)
%
% This function computes the average of data over sphere assuming that the first two dimensions
% are longitude and latitude respectively.
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

cosLat = cos(lat(:)*pi/180);

if nargin > 4
  lonIdx = find(lon >= lonRange(1) & lon <= lonRange(2));
else
  lonIdx = 1:dataSize(end);
end

if nargin > 2
  latIdx = find(lat >= latRange(1) & lat <= latRange(2));
else
  latIdx = 1:dataSize(end-1);
end

if nargin > 5
  w = w(latIdx, lonIdx) .* repmat(cosLat(latIdx), [1,length(lonIdx)]);
else
  w = repmat(cosLat(latIdx), [1, length(lonIdx)]);
end

data = reshape(data, [prod(dataSize(1:(end-2))), dataSize((end-1):end)]);
data = data(:,latIdx, lonIdx); 
w = repmat(reshape(w, [1, dataSize((end-1):end)]), [prod(dataSize(1:(end-2))),1,1]);

w(~isfinite(data)) = 0;
data(~isfinite(data)) = 0;

w = reshape(w, size(w,1), []);
data = reshape(data, size(w,1), []);

avg = squeeze(sum(w .* data, 2) ./ sum(w,2));

if length(dataSize) > 3
  avg = reshape(avg, dataSize(1:(end-2)));
end
