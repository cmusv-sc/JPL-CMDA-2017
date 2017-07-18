function [x_opt, y_opt, z_opt, a_opt, c_opt, cm_opt, nR, nC] = decodeDisplayOpt(dispOpt)
%
% This function decode the display option: historically we packed information
% From LSB, bit 1: x scale (0 = linear, 1 = log)
%           bit 2: y scale (0 = linear, 1 = log)
%           bit 3: z scale (0 = linear, 1 = log)
%           bit 4: flag for anomaly (0 = normal, 1 = anomaly)
%           bit 5: flag for color range (0 = same, 1 = diverse)
%           bit 6-8: colormap 0-7
%           bit 9-12: number of rows for multi panel 
%           bit 13-16: number of cols for multi panel 
%           bit 17-32: unused bits
%
x_opt = mod(dispOpt,2);
dispOpt = floor(dispOpt/2);
y_opt = mod(dispOpt,2);
dispOpt = floor(dispOpt/2);
z_opt = mod(dispOpt,2);
dispOpt = floor(dispOpt/2);
a_opt = mod(dispOpt,2);
dispOpt = floor(dispOpt/2);
c_opt = mod(dispOpt,2);
dispOpt = floor(dispOpt/2);
cm_opt = mod(dispOpt,8);
dispOpt = floor(dispOpt/8);
nR = mod(dispOpt, 16);
dispOpt = floor(dispOpt/16);
nC = mod(dispOpt, 16);

