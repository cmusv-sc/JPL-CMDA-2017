function [status, idx] = isSubgrid(grid1, grid2)
%
% This function tests whether grid1 is a subgrid of grid2
%
status = false;

idx = [];

for ii = 1:length(grid1)
  [mV, mIdx] =  min(abs(grid2 - grid1(ii)));
  if mV == 0
    idx = [idx, mIdx];
  else
    return;
  end
end
status = true;
