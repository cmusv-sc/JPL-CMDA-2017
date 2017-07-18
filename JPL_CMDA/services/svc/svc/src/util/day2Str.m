function str =day2Str(day, opt)
%
% This is a utility function to convert a numerical day into str
%
% Input:
%   day		-- numerical value specifying a date within a month 1-31 or
%		-- witin a year.
%   opt		-- an optional argument to determine the format for coversion.
%
% Output:
%   str		-- output string
%  
% Author: Chengxing Zhai
%
% Revision history:
%   2012/12/17:	Initial version, cz
%
if nargin < 2
  opt = 'two-digit';
end
switch lower(opt)
  case {'two-digit', 'double-digit', '2-digit'},
    str = [num2str(floor(mod(day,100)/10)), num2str(mod(day,10))];
  case {'three-digit', 'triple-digit', '3-digit'},
    str = [num2str(floor(day/100)), num2str(floor(mod(day,100)/10)), num2str(mod(day,10))];
  otherwise,
    str = num2str(round(day));
end
