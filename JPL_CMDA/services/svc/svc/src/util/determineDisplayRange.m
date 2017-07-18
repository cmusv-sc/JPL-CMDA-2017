function dispRange = determineDisplayRange(data, cfgParams)
%
%
%
data = data(isfinite(data));
m = mean(data(:));
s = sqrt(mean(data(:).^2) - m^2);

if nargin < 2
  n = length(data(:));
  n_sigma = erfcinv(1/(10*n))*sqrt(2);
  dispRange = m + [-1,1]*s*n_sigma;
else
  dispRange = m + [-1,1]*s*cfgParams.xi;
end

min_v = min(data(:));
max_v = max(data(:));

if dispRange(1) < min_v
  dispRange(1) = min_v;
end

if dispRange(2) > max_v
  dispRange(2) = max_v;
end
