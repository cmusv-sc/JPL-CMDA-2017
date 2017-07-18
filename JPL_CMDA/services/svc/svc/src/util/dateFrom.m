function newDate = dateFrom(origDate, nMonth)
%
% This function find a new date that is "nMonth" from a starting date "origDate"
%
newMonth = origDate.month + nMonth;

newDate.month = 1 + mod(newMonth-1,12);

newDate.year = origDate.year + (newMonth - newDate.month)/12;
