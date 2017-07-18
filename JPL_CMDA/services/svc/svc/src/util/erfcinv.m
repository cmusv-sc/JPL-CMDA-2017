function y = erfcinv(x)
%
% This function is the inverse function of erfc(x) = 1 - sqrt(2/pi)*int_0^x e^(-t^2) dt
%
y = erfinv(1 - x);
