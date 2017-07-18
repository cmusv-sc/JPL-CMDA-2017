function z = twoDimInterpOnSphere(lon0, lat0, z0, lon, lat, method)
%
% This function does two dimensional interpolation on a sphere
%
% Let us handle the special boundary condition here:
% i.e. longitude is periodical, P = 360 degree
%      lattitude is singular at +/- 90 degree
lonExt = lon0(:);
latExt = lat0(:);
N_x0 = length(lon0);
N_y0 = length(lat0);

extLon0 = lon0(1) > 0;
if extLon0
  lonExt = [lon0(end)-360; lonExt]; % interpolating between smallest and largest longitudes
end

extLon360 = lon0(end) < 360;
if extLon360
  lonExt = [lonExt; lon0(1)+360]; % interpolating between largest and smallest longitudes
end

extLatBegin = abs(lat0(1)) < 90;
if extLatBegin
  latExt = [sign(lat0(1))*90; latExt]; % add one pole
end

extLatEnd = abs(lat0(end)) < 90;
if extLatEnd
  latExt = [latExt; 90*sign(lat0(end))]; % add north pole
end

zExt = zeros(length(lonExt), length(latExt));
zExt(extLon0+(1:N_x0), extLatBegin+(1:N_y0)) = z0;
if extLon0
  zExt(1,extLatBegin+(1:N_y0)) = z0(end, :);
end
if extLon360
  zExt(end,extLatBegin+(1:N_y0)) = z0(1, :);
end
if extLatBegin
  zExt(:, 1) = mean(zExt(:,2));
end
if extLatEnd
  zExt(:, end) = mean(zExt(:,end-1));
end

% We need to ensure that lon is within the domain
smallIdx = find(lon < min(lonExt(:)));
lon(smallIdx) = lon(smallIdx) + 360;
largeIdx = find(lon > max(lonExt(:)));
lon(largeIdx) = lon(largeIdx) - 360;
  
z = twoDimResample(lonExt, latExt, zExt', lon, lat, method)';
