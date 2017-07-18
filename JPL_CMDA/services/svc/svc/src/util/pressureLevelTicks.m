function pTick = pressureLevelTicks(p_min, p_max, dp)
%
% This function gives the ptick locations
%

n_min = round(p_min/dp); 
n_max = round(p_max/dp); 

pTick = (n_min:n_max)'*dp;
