function p = sigmaPressure(ptop, sigma, ps)
%
% This function computes the sigma coordinate pressure levels.
%
p = hybridSigmaPressure(1-sigma, ptop, sigma, ps);
