function str = seasonStr(monthIdx)
%
% This function returns a string of the initials of each month in the list
%
%
% Input:
%   monthIdx	-- a vector containing the month index in a year, 1,2, ..., 12 corresponding
%		-- to Jan, Feb, ..., Dec
% Output:
%   str		-- a string describe contains the initials of the month in the passed list
%		-- e.g. JJA for 6,7,8, or summer season for northern hemisphere.
%

monthInitials = 'JFMAMJJASOND';

if length(monthIdx) == 12
  str = 'Annual';
  return;
else
  str = monthInitials(monthIdx); 
end
