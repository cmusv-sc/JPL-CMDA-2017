function binB = binBoundarySpec(binB)
%
% This function generates a set of bin boundary values
%
%
% Assuming the last element specifying the number of nBins
nBin = length(binB);

if nBin > 3 && nBin == binB(end) + 2
  binB = binB(1:(nBin-1));
elseif nBin == 3
  if binB(3) <= 0
    binB = [];
  else
    binB = linspace(binB(1), binB(2), binB(3)+1);
  end
else
  error('*** Inconsistent data for bin boundary value specification!!!');
end
