function jd = juliandate(varargin)
%
% this function is borrowed from matlab
% 
[year month day hour min sec] = datevec(datenum(varargin{:}));

for k = length(month):-1:1
    if ( month(k) <= 2 ) % January & February
        year(k)  = year(k) - 1.0;
        month(k) = month(k) + 12.0;
    end
end

jd = floor( 365.25*(year + 4716.0)) + floor( 30.6001*( month + 1.0)) + 2.0 - ...
    floor( year/100.0 ) + floor( floor( year/100.0 )/4.0 ) + day - 1524.5 + ...
    (hour + min/60 + sec/3600)/24;
