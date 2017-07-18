function status = copyVar(nc_to, nc_from, varName)
%
% This function copies a variable from netcdf object "nc_from" to "nc_to"
%

status = -1;

% We first create the variable
nc_to{varName} = nc_from{varName};

% copy the value
nc_to{varName}(:) = nc_from{varName}(:);

% copy the attributes
status = copyAtt(nc_to{varName}, nc_from{varName});
