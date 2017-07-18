function anom = simpleAnomaly(data, dim)
%
% This function computes anomaly by removing climatology
%
% Author: Chengxing Zhai
%
% First obtain the dimension information of the data
if nargin < 2
  dim = 1;
  % if the data is a vector, we shall compute the anomaly using the nontrivial dimension.
  if isvector(data) && size(data,1) == 1
    dim = 2;
  end
end

dataSize = size(data);

if dim == 1
  anom = data;
  for jj = 1:12
    idx = jj:12:dataSize(1);
    anom(idx,:) = data(idx,:) - repmat(mean(data(idx,:),1), length(idx),1);
  end
else
  data = reshape(data, prod(dataSize(1:(dim-1))), dataSize(dim), []);
  anom = data;
  for jj = 1:12
    idx = jj:12:dataSize(1);
    anom(:,idx,:) = data(:,idx,:) - repmat(mean(data(:,idx,:),2), [1, length(idx),1]);
  end
  anom = reshape(anom, dataSize);
end

