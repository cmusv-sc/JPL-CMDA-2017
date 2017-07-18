function value = getValueFromURL(url, key)
%
% This functions retrieve the value associated with a key (passed) assuming format "key1=value1&key2=value2&key3=value3..."
%
key_value_pairs = strchop(url, '&');

idx = find(~cellfun(@isempty, strfind(key_value_pairs, [key '='])));

if ~isempty(idx)
  value = key_value_pairs{idx(1)}((length(key)+2):end);
else
  value = [];
end
