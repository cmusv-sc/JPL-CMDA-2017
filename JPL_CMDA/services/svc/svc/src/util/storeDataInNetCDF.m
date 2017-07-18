function status = storeDataInNetCDF(data, fileName, opt)
%
% This file stores data in netCDF format
%
status = -1;
nDim = data.nDim;

if nargin < 3
  opt = '';
end

switch lower(opt)

  case 'octcdf',
    nc = netcdf(fileName, 'c');

    for ii = 1:nDim
      nc(data.dimNames{ii}) = data.dimSize(ii);
    end
    for ii = 1:nDim
      nc{data.dimNames{ii}} = ncdouble(data.dimNames{ii});
    end

    for ii = 1:nDim
      nc{data.dimNames{ii}}(:) = data.dimVars{ii};
    end

    for ii = 1:nDim
      nc{data.dimNames{ii}}.units = data.dimVarUnits{ii};
    end
    
    nc{data.varName} = ncdouble(data.dimNames{:});
    nc{data.varName}(:) = data.var;
    nc{data.varName}.units = data.varUnits;
    nc{data.varName}.name = data.varLongName;
    
    close(nc);
  otherwise,
    % create schema
    clear thisSchema;
    thisSchema.Name = '/';
    thisSchema.Format = 'classic';

    for ii = 1:nDim
      thisSchema.Dimensions(ii).Name = data.dimNames{ii};
      thisSchema.Dimensions(ii).Length = data.dimSize(ii);
      thisSchema.Dimensions(ii).Unlimited = 0;
      thisSchema.Variables(ii).Name = data.dimNames{ii};
      thisSchema.Variables(ii).Datatype = 'double';
      thisSchema.Variables(ii).Dimensions(1) = thisSchema.Dimensions(ii);
      thisSchema.Variables(ii).Attributes(1) = struct('Name', 'units', 'Value', data.dimVarUnits{ii});
    end
    thisSchema.Variables(nDim+1).Name = data.varName;
    thisSchema.Variables(nDim+1).Datatype = 'single';
    for ii = 1:nDim
      thisSchema.Variables(nDim+1).Dimensions(ii) = thisSchema.Dimensions(ii);
    end
    thisSchema.Variables(nDim+1).Attributes(1) = struct('Name', 'units', 'Value', data.varUnits);
    thisSchema.Variables(nDim+1).Attributes(2) = struct('Name', 'long_name', 'Value', data.varLongName);
    %thisSchema.Variables(nDim+1).Attributes(3) = struct('Name', '_FillValue', 'Value', 1.0e20);
    %thisSchema.Variables(nDim+1).Attributes(4) = struct('Name', 'missing_value', 'Value', 1.0e20);
    disp(thisSchema)
    if exist(fileName, 'file')
      delete(fileName);
    end
    ncwriteschema(fileName, thisSchema);
    ncwriteatt(fileName, data.varName, '_FillValue', 1e20);
    ncwriteatt(fileName, data.varName, 'missing_value', 1e20);
    for ii = 1:nDim
      ncwrite(fileName, thisSchema.Variables(ii).Name, data.dimVars{ii}(:));
    end
    ncwrite(fileName, data.varName, data.var);
end
status = 0;
