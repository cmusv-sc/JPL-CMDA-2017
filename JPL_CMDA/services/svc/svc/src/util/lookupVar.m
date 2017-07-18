function idx = lookupVar(varName, fileInfo)
%
% This funciton checkes whether the passed in dimension name is an existing dimension
%
idx = find(strcmp({fileInfo.Variables.Name}, varName));
