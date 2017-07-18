function binB = generateBinB(data, nBin, n_min)
%
% This function generates bin boundaries according to the data
%
if nargin < 2
  nBin = 10; % default to use 10 bins
end

if nargin < 3
  n_min = 100;
end

data_valid = data(isfinite(data));
data_valid_sorted = sort(data_valid);

N = length(data_valid);
nAvgSample = floor(N/nBin);

binB = data_valid_sorted([1+(0:(nBin-1))*nAvgSample, N]);

binB = binB(:)';

if nAvgSample < 1.5*n_min
  return;
end

binB_new = linspace(data_valid_sorted(1), data_valid_sorted(end), nBin+1);

iIter = 1;
nIter = 100;

while ~isempty(find(findNumberOfSamplesInEachBin(data_valid_sorted, binB_new) < n_min,1))

  binB_new = 0.8*binB_new + 0.2*binB;
  iIter = iIter + 1
  if iIter > nIter
    break;
    warning(['!!! Did not find a set of bin boundary values satisfying the minimum population condition, min sample = ' num2str(min(findNumberOfSamplesInEachBin(data_valid_sorted, binB_new)))]);
  end
end

binB = binB_new;

end

function nSamples = findNumberOfSamplesInEachBin(sorted_data, binB)

nBin = length(binB) - 1;
nSamples = zeros(nBin,1);
N = length(sorted_data);

idx_from_min = 1;
for ii = 1:(nBin-1)
  nSamples(ii) = find(sorted_data(idx_from_min:N) > binB(ii+1), 1) - 1;
  idx_from_min = idx_from_min + nSamples(ii); 
end

nSamples(nBin) = N - idx_from_min;

end
