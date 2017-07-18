function [A_mu, A_sigma, B_c, nSamples] = scatterAonB(A, B, bins)
%
% This function uses the specified bin values to sort B.
% Because A an B share the same index,
% A is also sorted acccording to its corresponding elements in B.
%
% Usage: [A_mu, A_sigma, B_c, nSamples] = scatterAonB(A, B, bins)
%
% Input:
%   A		-- vector A, assume 1 x n or n x 1
%   B		-- vector B, assume 1 x n or n x 1
%   bins	-- contains boundary values of bins to be used for
%		-- binning B, nBin+1 values
% 
% Output:
%   A_mu	-- average value of A within each bin
%   A_sigma	-- standard deviation of A values within each bin
%   B_c		-- center value each bin
%   nSamples	-- number of samples within each bin
% 
% Author: Chengxing Zhai
% Revision history:
%   2013/08/30: Initial version, cz
%

nBins = length(bins) - 1;

A_mu = zeros(nBins,1);
B_c  = zeros(nBins,1);
A_sigma = zeros(nBins,1);
nSamples = zeros(nBins,1);

for binI = 1:nBins
  B_c(binI) = mean(bins(binI+(0:1)));
  if binI == 1
    idx = find(B(:) >= bins(1) & B(:) <= bins(2));
  else
    idx = find(B(:) > bins(binI) & B(:) <= bins(binI+1));
  end
  A_bin = A(idx);
  dataIdx = find(~isnan(A_bin));
  nSamples(binI) = length(dataIdx);
  if nSamples(binI) >= 1
    A_mu(binI) = mean(A_bin(dataIdx));
    A_sigma(binI) = std(A_bin(dataIdx));
  else
    warning(['Zero sample found in bin No. ' num2str(binI)]);
    A_mu(binI) = NaN;
    A_sigma(binI) = NaN;
  end
end
