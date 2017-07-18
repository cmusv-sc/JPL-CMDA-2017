function [idxForBins, bin_c, nSamples] = generateIdxForBins(binB, data)
%
% This functino generate data indices for each bin specified by the boundaries of the
% bins.
%
% Input:
%   binB	-- the boundary values that define all the bins
%   data	-- data to be sorted out
%
% Output:
%   idxForBins	-- the index to the data whose values are within a bin
%   bin_c	-- the center value at the bin
%   nSamples	-- the number of nsamples within the bin
%
% Author: Chengxing Zhai
%
% Revision history:
%
%   20131007:	Initial version, CZ
%

nBin = length(binB) - 1;

bin_c = (binB(1:nBin) + binB(2:end))/2;

idxForBins = cell(nBin,1);
nSamples = zeros(nBin,1, 'int32'); 

idxForBins{1} = find(data >= binB(1) & data <= binB(2));
nSamples(1) = length(idxForBins{1});
for ii = 2:nBin
  idxForBins{ii} = find(data > binB(ii) & data <= binB(ii+1));
  nSamples(ii) = length(idxForBins{ii});
end
