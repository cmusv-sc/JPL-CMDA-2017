function idx = lookupDim(dimName, fileInfo)
%
% This funciton checkes whether the passed in dimension name is an existing dimension
%
idx = find(strcmp({fileInfo.Dimensions.Name}, dimName));
