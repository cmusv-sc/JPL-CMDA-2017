function cmap = myColorMap(clim, opt)
%
% This function generates a 64x3 array representing RGB values
% for a color scheme covering range specified by clim
%
% Input:
%   clim	-- color value range, [min, max]
%   opt		-- an option used to determine whether to use linear
%		-- or log scale
% Output:
%   cmap	-- a 64x3 matrix representing the RGB values for 64
%		-- data value
%
if nargin < 2
  opt = 'sqrt'; % square root is a nomial color scheme
end

cmap = ones(64, 3);

if prod(clim) < 0
  color_0 = [1,1,1];
  color_neg = [0, 0, 1];
  color_pos = [1, 0, 0];
  color_blend = [0, 0, 0];

  switch lower(opt)
    case 'log',
      zeroColorIdx = ceil((0 - clim(1))/(clim(2) - clim(1))*64);
      scale_factor_neg = log(zeroColorIdx:-1:1)'/log(1+zeroColorIdx);
      scale_factor_pos = log(1:(64-zeroColorIdx))'/log(65-zeroColorIdx);
    case 'lin',
      zeroColorIdx = ceil((0 - clim(1))/(clim(2) - clim(1))*64);
      normF_pos = max([1, 64-zeroColorIdx]);
      normF_neg = max([1,zeroColorIdx]);
      scale_factor_neg = ((zeroColorIdx-1):-1:0)'/normF_neg;
      scale_factor_pos = (1:(64-zeroColorIdx))'/normF_pos;
    case 'lin0',
      zeroColorIdx = 32;
      normF_pos = max([1, 64-zeroColorIdx]);
      normF_neg = max([1,zeroColorIdx]);
      scale_factor_neg = ((zeroColorIdx-1):-1:0)'/normF_neg;
      scale_factor_pos = (1:(64-zeroColorIdx))'/normF_pos;
    case {'jet', 'hsv', 'hot', 'cool', 'summer', 'winter', 'spring', 'autumn', 'gray', 'bone', 'copper', 'pink', 'prism', 'flag'}
      cmap = colormap(lower(opt)); 
      return;
    otherwise,
      zeroColorIdx = ceil((0 - clim(1))/(clim(2) - clim(1))*64);
      normF_pos = max([1, 64-zeroColorIdx]);
      normF_neg = max([1,zeroColorIdx]);
      scale_factor_neg = sqrt(((zeroColorIdx-1):-1:0)'/normF_neg);
      scale_factor_pos = sqrt((1:(64-zeroColorIdx))'/normF_pos);
  end

  cmap(1:zeroColorIdx,:) = scale_factor_neg*color_neg + (1-scale_factor_neg)*color_0 + (scale_factor_neg .* (1 - scale_factor_neg)) * color_blend;
  cmap((zeroColorIdx+1):64,:) = scale_factor_pos*color_pos + (1-scale_factor_pos)*color_0 + (scale_factor_pos .* (1 - scale_factor_pos)) * color_blend;
else
  switch lower(opt)
    case {'jet', 'hsv', 'hot', 'cool', 'summer', 'winter', 'spring', 'autumn', 'gray', 'bone', 'copper', 'pink', 'prism', 'flag'}
      cmap = colormap(lower(opt)); 
    otherwise,
cmap = [ 0         0    0.5625
         0         0    0.6250
         0         0    0.6875
         0         0    0.7500
         0         0    0.8125
         0         0    0.8750
         0         0    0.9375
         0         0    1.0000
         0    0.0625    1.0000
         0    0.1250    1.0000
         0    0.1875    1.0000
         0    0.2500    1.0000
         0    0.3125    1.0000
         0    0.3750    1.0000
         0    0.4375    1.0000
         0    0.5000    1.0000
         0    0.5625    1.0000
         0    0.6250    1.0000
         0    0.6875    1.0000
         0    0.7500    1.0000
         0    0.8125    1.0000
         0    0.8750    1.0000
         0    0.9375    1.0000
         0    1.0000    1.0000
    0.0625    1.0000    0.9375
    0.1250    1.0000    0.8750
    0.1875    1.0000    0.8125
    0.2500    1.0000    0.7500
    0.3125    1.0000    0.6875
    0.3750    1.0000    0.6250
    0.4375    1.0000    0.5625
    0.5000    1.0000    0.5000
    0.5625    1.0000    0.4375
    0.6250    1.0000    0.3750
    0.6875    1.0000    0.3125
    0.7500    1.0000    0.2500
    0.8125    1.0000    0.1875
    0.8750    1.0000    0.1250
    0.9375    1.0000    0.0625
    1.0000    1.0000         0
    1.0000    0.9375         0
    1.0000    0.8750         0
    1.0000    0.8125         0
    1.0000    0.7500         0
    1.0000    0.6875         0
    1.0000    0.6250         0
    1.0000    0.5625         0
    1.0000    0.5000         0
    1.0000    0.4375         0
    1.0000    0.3750         0
    1.0000    0.3125         0
    1.0000    0.2500         0
    1.0000    0.1875         0
    1.0000    0.1250         0
    1.0000    0.0625         0
    1.0000         0         0
    0.9375         0         0
    0.8750         0         0
    0.8125         0         0
    0.7500         0         0
    0.6875         0         0
    0.6250         0         0
    0.5625         0         0
    0.5000         0         0
];
end

if clim(1) > 0
  cmap = lin2log(cmap, clim);
elseif clim(1) == 0
  cmap = lin2log(cmap, [clim(2)^1/64,clim(2)]);
elseif clim(2) == 0
  cmap = flipud(lin2log(flipud(cmap), [abs(clim(1))^1/64,abs(clim(1))]));
else
  cmap = flipud(lin2log(flipud(cmap), abs(clim([2,1]))));
end
end

cmap ( cmap > 1) = 1;
