function z = hybridHeight(a, b, zs)
%
% This function computes the hybrid height coordinate levels.
%
nZ = length(b);
[nT, nLat, nLon] = size(zs);

z = repmat(reshape(a, [1, nZ, 1,1]), [nT, 1, nLat, nLon]));
for tI = 1:nT
  z(tI,:,:,:) = z(tI,:,:,:) + reshape(zs(tI,:)*b(:)', 1, 1, nLat, nLon);
end
