function str = date2Str(aDate, opt)
%
% This function returns the string specified by aDate
% which contains "year", "month", and "day".
%
% Input:
%   aDate	-- a structure containing at least 'year', optionally 'month'
%		-- and 'day'.
%   opt		-- optional argument for the separator between 'year', 'month'
%		-- and 'day'.
%
% Output:
%   str		-- an output string for a date
%
% Author: Chengxing Zhai
%
% Revision history:
%   2012/12/17:	Initial version, cz
%
if nargin < 2
  opt = '';
end

str = num2str(aDate.year);

if isfield(aDate, 'month')
  str = [str opt month2Str(aDate.month)];
end

if isfield(aDate, 'day')
  str = [str opt day2Str(aDate.day)];
end
