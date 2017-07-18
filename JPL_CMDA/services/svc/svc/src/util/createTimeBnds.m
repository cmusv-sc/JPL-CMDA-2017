function time_bnds = createTimeBnds(startTime, endTime, refTime)
%
% This function creates the boundaries for the time dimension.
%
n = numberOfMonths(startTime, endTime);

time_bnds = zeros(n,2);

refDatenum = datenum(refTime.year, refTime.month, refTime.day);

for ii = 1:n
  thisDate = dateFrom(startTime, (ii-1));
  thisDatenum = datenum(thisDate.year, thisDate.month,1);
  time_bnds(ii,1) = thisDatenum - refDatenum;
end

time_bnds(1:(n-1),2) = time_bnds(2:n,1);
thisDate = dateFrom(endTime, 1);
thisDatenum = datenum(thisDate.year, thisDate.month,1);
time_bnds(n,2) = thisDatenum - refDatenum;

