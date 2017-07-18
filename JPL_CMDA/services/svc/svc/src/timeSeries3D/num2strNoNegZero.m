function str = num2strNoNegZero(num)
%
% This is a utilty function does the same as num2str except
% it ensures '-0' or '0' are both coverted to '0'
%
% Input:
%   num		-- the number to be converted to a string
%
% Output:
%   str		-- the result string

% Let us ensure or the '-0' is 0
num(num == 0) = 0;
str = num2str(num);
