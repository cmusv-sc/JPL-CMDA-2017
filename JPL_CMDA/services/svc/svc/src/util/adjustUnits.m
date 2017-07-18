function units_adj = adjustUnits(units, varName)

switch varName
  case 'cli', 
    units_adj = 'Kg/Kg';
  case 'clw', 
    units_adj = 'Kg/Kg';
  case 'hus',
    units_adj = 'Kg/Kg';
  otherwise,
    units_adj = units;
end
