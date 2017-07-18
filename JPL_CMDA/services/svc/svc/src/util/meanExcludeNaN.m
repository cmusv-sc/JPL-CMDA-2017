function meanV = meanExcludeNaN(v, dim, w)
%
% Usage: meanV = meanExcludeNaN(v, dim)
%
% This function computes average excluding NaN, which may be the value of
% some of the elements of v
%
% Input:
%   v	-- vector or matrix containing all the data
%   dim	-- dimension along which the mean value is computed
%   w	-- an optional weigthing factor
%
% Output:
%
%   meanV	-- computed average value to be returned
%
% Author: Chengxing Zhai
%
% Revision history:
%   2012/11/01:	Initial version, cz

if nargin < 3
  v_size = size(v);
  if nargin < 2
    dim = find(v_size > 1, 1, 'first');
  end
  meanV = single(sum(~isnan(v), dim));
  v(isnan(v)) = 0;
  meanV = sum(v, dim) ./ meanV;
else
  % Replace all the NaN with 0 to exclude them in computing mean 
  w(isnan(v)) = 0;
  v(isnan(v)) = 0;

  meanV = sum(v .* w, dim) ./ sum(w , dim);
end
