function p = hybridSigmaPressure(a, p0, b, ps)
%
% This function computes the hybrid sigma coordinate levels.
%
nP = length(b);
[nT, nLat, nLon] = size(ps);

p = repmat(reshape(a*p0, [1, nP, 1,1]), [nT, 1, nLat, nLon]));
for tI = 1:nT
  p(tI,:,:,:) = p(tI,:,:,:) + reshape(ps(tI,:)*b(:)', 1, 1, nLat, nLon);
end
