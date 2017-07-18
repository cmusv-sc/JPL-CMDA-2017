function str_out = removeTrailingNullChar(str_in)
%
% This function removes the trailing null character
%

if uint8(str_in(end)) == 0
  str_out = str_in(1:(end-1));
else
  str_out = str_in;
end
