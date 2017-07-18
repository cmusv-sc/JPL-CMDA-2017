function str = month2Str(month, opt)
%
% This is a utility function to convert a numerical number month into str
%
% Input:
%   month	-- numerical value specifying a month 1-12.
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
persistent monthStrs;

if isempty(monthStrs)
  monthStrs = {'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'};
end

if nargin < 2
  opt = 'two_digit';
end

switch lower(opt)
  case 'text_3',
    str = [monthStrs{month}(1:3)];
  case 'text',
    str = monthStrs{month};
  case 'two_digit',
    str = [num2str(floor(month/10)) num2str(mod(month,10))];
  otherwise,
    str = num2str(month);
end
