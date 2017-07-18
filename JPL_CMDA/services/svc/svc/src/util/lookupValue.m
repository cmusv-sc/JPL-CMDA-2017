function value = lookupValue(nameValueStructArray, name)
%
% This function enables to lookup the value using name as an entry
%
idx = find(strcmp({nameValueStructArray.Name}, name));
value = nameValueStructArray(idx).Value;

