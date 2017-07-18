function [nR, nC] = designMultiPanel(n, opt)
%
% This function returns number of panels
%
switch (lower(opt))
  case 'map'
    nC = floor(sqrt(n));
    nR = ceil(n/nC);
  otherwise
    nR = floor(sqrt(n));
    nC = ceil(n/nR);
end
