function v = ncreadVar(file, var, start, count, strid)
%
% This function reads variable with name specified by var and store in v
% It makes missing value and _fillValue "NaN"
%
ncid = netcdf_open(file, 'NOWRITE');
varId = netcdf_inqVarID(ncid, var);
if nargin < 3
  v = netcdf_getVar(ncid, varId);
elseif nargin == 3
  v = netcdf_getVar(ncid, varId, start-1); % start, 0 based index,
elseif nargin == 4
  v = netcdf_getVar(ncid, varId, start-1, count); % start, 0 based index
else
  v = netcdf_getVar(ncid, varId, start-1, count, stride); % start, 0 based index
end

if hasAttribute(file, var, 'missing_value')
  missingValue = single(ncreadatt(file, var, 'missing_value'));
  v(abs(v - missingValue) < 1e-6 ) = NaN;
end
if hasAttribute(file, var, '_fillvalue')
  fillValue = single(ncreadatt(file, var, '_fillvalue'));
  v(abs(v - fillValue) < 1e-6 ) = NaN;
end

if hasAttribute(file, var, '_FillValue')
  fillValue = single(ncreadatt(file, var, '_FillValue'));
  v(abs(v - fillValue) < 1e-6 ) = NaN;
end

if hasAttribute(file, var, 'scale_factor')
  scale_factor = ncreadatt(file, var, 'scale_factor');
  v = single(v)*scale_factor;
end
if hasAttribute(file, var, 'add_offset')
  add_offset = ncreadatt(file, var, 'add_offset');
  v = single(v) + add_offset;
end

netcdf_close(ncid);
