function [idx, alphas] = linearInterpHelper(x, xvec, opt)
%
% This function helps to determine the indices between which the value "x" resides.
% We assume xvec is monotonic
% Usage:
%
%   [idx, alphas] = linearInterpHelper(x, xvec, opt)
%

if nargin < 3
  opt = 'lin';
end 

[mV, idx] = min(abs(xvec - x));

% x might not be within the interval
if idx == 1 | idx == length(xvec) | xvec(idx) == x 
  alphas = 1;
  return;
else
  if prod(xvec(idx+(0:1)) - x) < 0
    idx = idx + (0:1);
  else
    idx = idx - (0:1);
  end
end

switch lower(opt)
  case 'log',
    alphas(1) = (log(x) - log(xvec(idx(2))))/(log(xvec(idx(1))) - log(xvec(idx(2))));   
  case 'lin',
    alphas(1) = (x - xvec(idx(2)))/(xvec(idx(1)) - xvec(idx(2)));
  otherwise,
    error(['unknown option: ' opt]);
end
alphas(2) = 1 - alphas(1);
