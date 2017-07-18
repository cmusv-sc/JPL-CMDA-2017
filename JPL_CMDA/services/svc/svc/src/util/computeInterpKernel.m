function K = computeInterpKernel(x0, x, method)
%
% usage: K = computeInterpKernel(x0, x)
%
% This function computes the linear transform matrix for interpolation
% from x0 to x. This is useful for resampling many sets of functions
% from x0 to x, i.e.  y = K*y0.
%
% Input:
%   x0	-- default sampling points, n0 x 1
%   x	-- default resampling points, n x 1
% Output:
%
%   K	-- kernal matrix, dimension n x n0
%
n0 = length(x0);
f0 = eye(n0);

K = zeros(length(x), n0);

% determine the points need to be extrapolated and assign to these points
% using the nearest neighbor method
[minV, minIdx] = min(x0);
[maxV, maxIdx] = max(x0);

idx_interp = find(x >= minV & x <= maxV);
for ii = 1:n0
  K(idx_interp,ii) = interp1(x0(:), f0(:,ii), x(idx_interp), method);
end

% For points beyond maximal value of x0, assign the value at the maximal x0
idx_beyond_max = find(x > maxV);
K(idx_beyond_max, maxIdx) = 1;
% For points beyond minimal value of x0, assign the value at the minimal x0
idx_beyond_min = find(x < minV);
K(idx_beyond_min, minIdx) = 1;
