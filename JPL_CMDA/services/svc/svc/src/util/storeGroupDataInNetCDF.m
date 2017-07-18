function status = storeGroupDataInNetCDF(data, fileName, opt)
%
% This file stores data in netCDF format
%
status = -1;
nDim = data.nDim;

if nargin < 3
  opt = '';
end

nVar = length(data.vars);

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
    
    for ii = 1:nVar
      nc{data.varNames{ii}} = ncdouble(data.dimNames{:});
      nc{data.varNames{ii}}(:) = data.vars{ii};
      nc{data.varNames{ii}}.units = data.varUnits{ii};
      nc{data.varNames{ii}}.name = data.varLongNames{ii};
    end
    
    close(nc);
  otherwise,
    % create schema
    clear thisSchema;
    thisSchema.Name = '/';
    thisSchema.Format = 'classic';
    if isfield(data, 'globalAtts')
      thisSchema.Attributes = data.globalAtts;
    end

    for ii = 1:nDim
      thisSchema.Dimensions(ii).Name = data.dimNames{ii};
      thisSchema.Dimensions(ii).Length = data.dimSize(ii);
      thisSchema.Dimensions(ii).Unlimited = 0;
      thisSchema.Variables(ii).Name = data.dimNames{ii};
      thisSchema.Variables(ii).Datatype = 'double';
      thisSchema.Variables(ii).Dimensions(1) = thisSchema.Dimensions(ii);
      thisSchema.Variables(ii).Attributes(1) = struct('Name', 'units', 'Value', data.dimVarUnits{ii});
    end
    for ii = 1:nVar
      thisSchema.Variables(nDim+ii).Name = data.varNames{ii};
      thisSchema.Variables(nDim+ii).Datatype = 'single';
      for jj = 1:nDim
        thisSchema.Variables(nDim+ii).Dimensions(jj) = thisSchema.Dimensions(jj);
      end
      thisSchema.Variables(nDim+ii).Attributes(1) = struct('Name', 'units', 'Value', data.varUnits{ii});
      thisSchema.Variables(nDim+ii).Attributes(2) = struct('Name', 'long_name', 'Value', data.varLongNames{ii});
    end
    disp(thisSchema)
    if exist(fileName, 'file')
      delete(fileName);
    end
    ncwriteschema(fileName, thisSchema);
    for ii = 1:nVar
      ncwriteatt(fileName, data.varNames{ii}, '_FillValue', 1e20);
      ncwriteatt(fileName, data.varNames{ii}, 'missing_value', 1e20);
    end
    for ii = 1:nDim
      ncwrite(fileName, thisSchema.Variables(ii).Name, data.dimVars{ii}(:));
    end
    for ii = 1:nVar
      ncwrite(fileName, data.varNames{ii}, data.vars{ii});
    end
end
status = 0;
