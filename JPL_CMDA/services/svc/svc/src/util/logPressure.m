function p = logPressure(p0, lev)
%
% This function computes the log pressure levels
%
p = p0 * exp(-lev);
