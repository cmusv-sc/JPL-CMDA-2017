function [data_valid, r_valid, c_valid] = subsetValidData(data, r, c)
%
% This function subset the data to get rid of invalid data
%
data_valid_mask = isfinite(data);

r_idx = sum(data_valid_mask,2) > 0;
c_idx = sum(data_valid_mask) > 0;

data_valid = data(r_idx, c_idx);


if nargin < 3
  % assume vector, ignore vector row/column convention
  if size(data,1) == 1
    r_valid = r(c_idx);
  elseif size(data,2) == 1
    r_valid = r(r_idx);
  else
    error('Data is two dimensional, need information for both row and column!');
  end
else
  c_valid = c(c_idx);
  r_valid = r(r_idx);
end
