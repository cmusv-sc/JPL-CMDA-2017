function plev = readPressureLevels(fn, plevVarName)

if strcmp(plevVarName, 'plev')
  plev = ncread(fn, 'plev');
  units = ncreadatt(fn, 'plev', 'units');
  switch lower(units)
    case {'dbar', 'decibar'},
      plev = plev * 1e4; % convert from dbar to Pa
    case 'bar',
      plev = plev * 1e5; % convert from bar to Pa
    case {'milibar', 'mbar', 'hpa', 'millibars'},
      plev = plev * 1e2; % convert from mbar to Pa
    otherwise,
      %% don't do anything
  end
else
  lev = ncread(fn, 'lev');
  units = ncread(fn, 'lev', 'units');
  switch lower(units)
    case 'm',
      plev = altitude2Pressure(lev/1000)*100; % m -> Km -> hPa -> Pa
  
    otherwise,
      p0 = 1.013e5; % 1atm = 1.013e5 Pa
      plev = lev(:)*p0;
  end
end
