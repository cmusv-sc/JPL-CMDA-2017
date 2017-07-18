function strs = strchop(str_input, delimiter)

str_remain = str_input;
ii = 1;
while str_remain
  [p, str_remain] = strtok(str_remain, delimiter);
  strs{ii} = p;
  ii = ii + 1;
end 
