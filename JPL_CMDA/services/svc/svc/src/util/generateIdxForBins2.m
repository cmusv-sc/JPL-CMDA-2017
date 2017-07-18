function [idxForBins, bin_c, nSamples] = generateIdxForBins2(binB, data)
%
% This functino generate data indices for each bin specified by the boundaries of the
% bins.
%
% Input:
%   binB	-- 2 sets of values that define the boundaries of bins for two sets of data
%   data	-- 2 datasets to be sorted out
%
% Output:
%   idxForBins	-- list of index to the data where the corresponding data values are within a 2-d bin,
%		-- (var1, var2)
%   bin_c	-- values at the center of bins
%   nSamples	-- number of nsamples within the 2-d bin
%
% Author: Chengxing Zhai
%
% Revision history:
%
%   20131007:	Initial version, CZ
%

for ii = 1:2
  nBin(ii) = length(binB{ii}) - 1;
end

for ii = 1:2
  bin_c{ii} = (binB{ii}(1:nBin(ii)) + binB{ii}(2:end))/2;
end

idxForBins1 = cell(nBin(1));
nSamples1 = zeros(nBin(1), 'int32'); 

idxForBins = cell(nBin);
nSamples = zeros(nBin, 'int32'); 

[idxForBins1, bin_c{1}, nSamples1] = generateIdxForBins(binB{1}, data{1}.data);
for ii = 1:nBin(1)
  [thisIdx, thisBin_c, thisNSamples] = generateIdxForBins(binB{2}, data{2}.data(idxForBins1{ii}));
  for jj = 1:nBin(2)
    idxForBins{ii,jj} = idxForBins1{ii}(thisIdx{jj});
    nSamples(ii,jj) = thisNSamples(jj);
  end
end
