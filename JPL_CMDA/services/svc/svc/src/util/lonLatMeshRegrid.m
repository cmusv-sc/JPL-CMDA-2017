function v_regrid = lonLatMeshRegrid(v, thisLon, thisLat, lon, lat, method);
%
% This function regrids data v, which has the first two dimensions to be thisLon, and thisLat,
% into the specified longitude an latitude and keep the rest of the dimension the same.
%
if nargin < 6
  method = 'linear';
end

size_v = size(v);
v = v(:,:,:); % make it no more than 3-d

nMaps = size(v,3);
nLon = length(lon);
nLat = length(lat);
v_regrid = zeros(nLon, nLat, nMaps);

for ii = 1:nMaps
  v_regrid(:, :, ii) = twoDimInterpOnSphere(thisLon, thisLat, v(:,:,ii), lon, lat, method);
end

if length(size_v) > 3
  size_v(1:2) = [nLon, nLat];
  v_regrid = reshape(v_regrid, size_v); 
end
