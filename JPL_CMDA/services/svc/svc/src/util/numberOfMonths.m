function n_month = numberOfMonths(startTime, stopTime)
%
% This routine computes number of months between the start time and
% stop time. The start time and stop time are expressed in a structure
% containing two fields specifying year and month respectively.
%
n_month = (stopTime.year - startTime.year)*12 + (stopTime.month - startTime.month) + 1;
