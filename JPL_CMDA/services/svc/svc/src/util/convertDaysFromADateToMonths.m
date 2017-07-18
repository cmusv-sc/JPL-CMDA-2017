function [years, months, dayIndices] = convertDaysFromADateToMonths(date0, dayVec, calendar)
%
% Use the specified calendar to convert the days from a date
% to months and years
%
% Input:
%   date0	-- the reference date
%   dayVec	-- a vector containing days for date0
%   calendar	-- the canlendar to be used for the definition of days and months
%
% Output:
%   years	-- years of the dates specified by the day vector
%   months	-- months of the dates specified by the day vector
%   dayIndices	-- the indices of the days falling into the month.
%

% Determine the time frame in terms of years
minYear = floor(min(dayVec)/366);
maxYear = ceil(max(dayVec)/359);

N = length(dayVec);
years = zeros(N,1);
months = zeros(N,1);
dayIndices = cell(1,N);

dataIdx = 0;

% Loop through the relevant years and determine which month there is data for. 
%
for yearI = minYear:maxYear
  for monthI = 1:12
    idx = dayInThisMonth(date0, dayVec, yearI, monthI, calendar);
    if isempty(idx)
      continue;
    else
      dataIdx = dataIdx + 1;
      years(dataIdx) = yearI + date0(1);
      months(dataIdx) = monthI;
      dayIndices{dataIdx} = idx;
    end
  end
end

years = years(1:dataIdx);
months = months(1:dataIdx);
dayIndices = dayIndices(1:dataIdx);

end


function daysIn = dayInThisMonth(date0, dayVec, year, month, calendar)
%
% This function determines whether a day is in a specified month
% according to specified calendar.
%
switch lower(deblank(calendar)),
  case '360_day',
    firstDayOfThisMonth = year*360 + (month - date0(2))*30 + 1 - date0(3);
    firstDayOfNextMonth = firstDayOfThisMonth + 30;
  case '365_day',
    daysFor12Months = [31,28,31,30,31,30,31,31,30,31,30,31];
    cumDays = cumsum([0,daysFor12Months]);
    firstDayOfThisMonth = year*365 + cumDays(month) - cumDays(date0(2)) + 1 - date0(3);  
    firstDayOfNextMonth = firstDayOfThisMonth + daysFor12Months(month);
  case 'noleap',
    daysFor12Months = [31,28,31,30,31,30,31,31,30,31,30,31];
    cumDays = cumsum([0,daysFor12Months]);
    firstDayOfThisMonth = year*365 + cumDays(month) - cumDays(date0(2)) + 1 - date0(3);  
    firstDayOfNextMonth = firstDayOfThisMonth + daysFor12Months(month);
  case {'gregorian', 'julian', 'standard'},
    jd0 = juliandate(date0(1), date0(2), date0(3));
    firstDayOfThisMonth = juliandate(year + date0(1),month,1) - jd0;
    firstDayOfNextMonth = juliandate(year + date0(1) + floor(month/12),mod(month,12)+1,1) - jd0;
  otherwise,
    warning(['Unknown calendar:' calendar]);
    warning('Assuming Gregorian');
    jd0 = juliandate(date0(1), date0(2), date0(3));
    firstDayOfThisMonth = juliandate(year + date0(1),month,1) - jd0;
    firstDayOfNextMonth = juliandate(year + date0(1) + floor(month/12),mod(month,12)+1,1) - jd0;
end

daysIn = find(dayVec (:) >= firstDayOfThisMonth & dayVec (:) < firstDayOfNextMonth);
%daysIn = find(dayVec (:) > firstDayOfThisMonth & dayVec (:) <= firstDayOfNextMonth);

end
