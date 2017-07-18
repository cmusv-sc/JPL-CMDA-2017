function s = range2str(r, n)
%
% This function converts an interval into a string '(a,b)' for convenience
%
if nargin < 2
  n = 3;
end
s = ['(' num2str(r(1), n) ', ' num2str(r(2), n) ')']; 
