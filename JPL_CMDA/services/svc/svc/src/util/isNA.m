function status = isNA(v)
%
% This function tests whether any element in v has fillValue
%

thresh = 1;
fillValue = -999999;
status = sum(abs(v - fillValue) < thresh) > 0;
