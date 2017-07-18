function resp = gaussianFilter(n, sigma)
%
% This function creates a Gaussian filter profile
%
% Input:
%   n           -- dimension
%   sigma       -- response width
%
% Output:
%   resp        -- response profile
x = (1:n) - (1+n)/2;
xx = repmat(x(:), 1, n);
yy = xx';

resp = exp(-(xx.^2 + yy.^2)/(2*sigma^2));
resp = resp / sum(resp(:));
