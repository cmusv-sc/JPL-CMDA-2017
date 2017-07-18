function date = str2date(date_str)
%
% This function converts date string into date structure
%
date.year = str2num(date_str(1:4));
if length(date_str) > 4
  date.month = str2num(date_str(5:6));
end
if length(date_str) > 6
  date.day = str2num(date_str(7:end));
end

