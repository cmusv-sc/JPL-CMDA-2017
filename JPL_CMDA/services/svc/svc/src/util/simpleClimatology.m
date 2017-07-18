function avg = simpleClimatology(data, dim, monthIdx)
%
% This function computes climatology by taking an average over the monthly
% data index, which is the index for dimension "dim".
%
% Author: Chengxing Zhai
%
% Revision history:
% 2012/11/01:	Initial version, cz
%

if nargin < 3
  monthIdx = 1:12; % Let the default value of months to cover the whole year
end

% First obtain the dimension information of the data
dataSize = size(data);

% To make the code generic, we reshape the data to make the data a
% 3-d array with the second dimension
% corresponding to the monthly index.
data = reshape(data, prod(dataSize(1:(dim-1))), dataSize(dim), prod(dataSize((dim+1):end)));
dataSize(dim) = 1;

avg = zeros(dataSize);
for ii = monthIdx
  avg(:) = avg(:) + reshape(meanExcludeNaN(data(:,ii:12:end,:),2), [], 1);
end

avg = avg/length(monthIdx);
