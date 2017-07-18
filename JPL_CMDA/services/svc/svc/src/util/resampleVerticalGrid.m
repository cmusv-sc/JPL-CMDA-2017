function status = resampleVerticalGrid(file_in, file_out, varName, plev)
%
% This file resamples the data in file_in vertically to the specified grid "plev"
% and then write the file to file_out. 
%

status = -1;

% get some info
inFileInfo = ncinfo(file_in);
varInfo = inFileInfo.Variables;

outFileInfo.Name = inFileInfo.Name;
outFileInfo.Format = inFileInfo.Format;
outFileInfo.Groups = inFileInfo.Groups;
outFileInfo.Attributes = inFileInfo.Attributes;

no_bnds = false;
dimNames = {'time', 'lon', 'lat', 'bnds'};
nDims = length(dimNames);

for ii = 1:nDims
  idx = lookupDim(dimNames{ii}, inFileInfo);
  if length(idx) == 1
    outFileInfo.Dimensions(ii) = inFileInfo.Dimensions(idx(1));
  else
    if ii == nDims
      nDims = nDims - 1; 
      no_bnds = true;
    else
      error(['!!! missing dimension info: ' dimNames{ii} ]);
    end
  end
end

nP = length(plev);
outFileInfo.Dimensions(nDims+1) = struct('Name', 'plev', 'Length', nP, 'Unlimited', false);

if no_bnds
  varList = {'lon', 'lat', 'time', varName};
else
  varList = {'lon', 'lat', 'time', 'lon_bnds', 'lat_bnds', 'time_bnds', varName};
end

nVar = length(varList);

for ii = 1:nVar
  idx = lookupVar(varList{ii}, inFileInfo);
  if length(idx) == 1
    outFileInfo.Variables(ii) = rmfield(inFileInfo.Variables(idx(1)), 'Checksum'); % "checksum is not implemented for netcdf-3
  else
    error(['!!! missing variable: ' varList{ii} ]);
    keyboard;
  end
  if strcmp(varList{ii}, varName)
    outFileInfo.Variables(ii).Dimensions(1:4) = outFileInfo.Dimensions([2,3,nDims+1,1]);
  end
end

ncwriteschema(file_out, outFileInfo);

for ii = 1:(nVar -1)
  ncwrite(file_out, varList{ii}, ncread(file_in, varList{ii}));
end

status = write_plev(file_out, plev);

data = single(ncread(file_in, varName));

[nLon, nLat, nP_orig, nT] = size(data);

data_regrided = zeros(nLon, nLat, nP, nT, 'single');

% We now go through the vertical coordinate
for varI = 1:length(varInfo)
  thisVarName = varInfo(varI).Name;
  if ~isempty(strfind(thisVarName, 'plev'))
    plev_orig = ncread(file_in, 'plev');
    % Compute a kernel matrix for computing linear interpolation
    % to save time. Interpolation is done using log scale
    K = computeInterpKernel(log(plev_orig(:)), log(plev(:)), 'linear');
    for tI = 1:nT
      data_regrided(:,:,:,tI) = reshape(matrixMultiplicationWithNan(reshape(data(:,:,:,tI), nLon*nLat, nP_orig),K'), nLon, nLat, nP);
    end
    ncwrite(file_out, varName, data_regrided);
    status = 0;
    return;
  elseif ~isempty(strfind(thisVarName, 'lev'))
    levelVarName = thisVarName;
    levelVarIdx = varI;
    break;
  end
end

if isempty(levelVarName)
  error('No vertical coordinate found!'); 
end

% We  now get the information regarding the vertical coordinate,i.e. sigma or hybrid sigma coordinate
formula_str = lookupValue(varInfo(levelVarIdx).Attributes, 'formula');
standard_name = removeTrailingNullChar(lookupValue(varInfo(levelVarIdx).Attributes, 'standard_name'));
terms = lookupValue(varInfo(levelVarIdx).Attributes, 'formula_terms');
if isempty(formula_str)
  warning('No formula is found!');
end
formula = formulaParser(formula_str);
termPairs = reshape(strchop(terms, ' '),  2, []);

switch lower(standard_name)
  case {'atmosphere_ln_pressure_coordinate'},
    % Let us parse the formula
    formula_str_simple = strrep(formulat_str, 'exp', ' ');
    formula_str_simple = strrep(formulat_str_simple, '(', ' ');
    formula_str_simple = strrep(formulat_str_simple, ')', ' ');
    formula = formulaParser(formula_str_simple);
    
    p_ref_var = lookupTermName(formula.inputVars{1}, termPairs, 'p0');
    p0 = ncread(file_in, p_ref_var);
    lev_var = lookupTermName(formula.inputVars{2}, termPairs, 'lev');
    lev = ncread(file_in, lev_var);
    plev_orig = p0 * exp(-lev);
    K = computeInterpKernel(log(plev_orig(:)), log(plev(:)), 'linear');
    for tI = 1:nT
      data_regrided(:,:,:,tI) = reshape(reshape(data(:,:,:,tI), nLon*nLat, nP_orig)*K', nLon, nLat, nP);
    end
    ncwrite(file_out, varName, data_regrided);
    status = 0;
    return;
  case {'atmosphere_sigma_coordinate'},
    ptop_var = lookupTermName(formula.inputVars{1}, termPairs, 'ptop');
    ptop = ncread(file_in, ptop_var);
    b_var = lookupTermName(formula.inputVars{2}, termPairs, 'b');
    b = ncread(file_in, b_var);
    ps_var = lookupTermName(formula.inputVars{3}, termPairs, 'ps');
    ps = ncread(file_in, ps_var) - ptop;
    pverFunc = @(lonI, latI, tI) ptop*a + ps(lonI, latI, tI)*b;
  case {'atmosphere_hybrid_sigma_pressure_coordinate'},
    varIdx = 1;
    if length(formula.op) == 2
      if strcmp(formula.op{varIdx}, '+')
        ap_var = lookupTermName(formula.inputVars{1}, termPairs, 'ap');
        ap = ncread(file_in, ap_var);
        varIdx = varIdx+1;
      else
        error('Unconventional formula for hybrid sigma pressure coordinate!');
      end
    else
      a_var = lookupTermName(formula.inputVars{varIdx}, termPairs, 'a');
      a = ncread(file_in, a_var);
      varIdx = varIdx+1;
      p_ref_var = lookupTermName(formula.inputVars{varIdx}, termPairs, 'p0');
      p0 = ncread(file_in, p_ref_var);
      varIdx = varIdx+1;
      ap = a*p0;
    end
    b_var = lookupTermName(formula.inputVars{varIdx}, termPairs, 'b');
    b = ncread(file_in, b_var);
    varIdx = varIdx+1;
    ps_var = lookupTermName(formula.inputVars{varIdx}, termPairs, 'ps');
    ps = ncread(file_in, ps_var);
    pverFunc = @(lonI, latI, tI) ap + b*ps(lonI, latI, tI);
  case {'atmosphere_hybrid_height_coordinate'}
    a_var = lookupTermName(formula.inputVars{1}, termPairs, 'a');
    a = ncread(file_in, a_var);
    b_var = lookupTermName(formula.inputVars{2}, termPairs, 'b');
    b = ncread(file_in, b_var);
    orog_var = lookupTermName(formula.inputVars{3}, termPairs, 'orog');
    orog = ncread(file_in, orog_var);
    pverFunc = @(lonI, latI, tI) altitude2Pressure(a + orog(lonI, latI, tI)*b);
  otherwise,
    error('unknown vertical coordinate!');
end

for lonI = 1:nLon
  for latI = 1:nLat
    for tI = 1:nT
      this_p = pverFunc(lonI, latI, tI);
      % Use linear interpolation on log(p)
      data_regrided(lonI, latI, :, tI) = interp1(log(this_p), squeeze(data(lonI, latI, :, tI)), log(plev), 'linear');
    end
  end
end

ncwrite(file_out, varName, data_regrided);
status = 0;
