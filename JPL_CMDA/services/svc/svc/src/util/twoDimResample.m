function z = twoDimResample(x0, y0, z0, x, y, method)
%
% usage:  z = twoDimResample(x0, y0, z0, x, y, method)
%
% This script resamples a two dimensional data set to a new grid using
% various methods specified by "opt".
% Possible methods:
%   nearest	--  using the nearest neighbor
%   linear	-- linear interpolation a two dimensional grid data
%
% Input:
%   x0		-- an existing grid point x coordinates, dimension = N_x0 x 1
%   y0		-- an existing grid point y coordinates, dimension = N_y0 x 1
%   z0		-- data values at the existing grid points, dimension = N_x0 x N_y0
%   x		-- x coordinates of the grid points to be resampled
%   y		-- y coordinates of the grid points to be resampled
%   method	-- specifying the method to be used, default to nearest
%
% Output:
%
%   z	-- resampled data at the specified points
%

if nargin < 6
  method = 'nearest'; % default to use the nearest neighbor interpolation
end

[xx0, yy0] = meshgrid(x0, y0);
[xx, yy] = meshgrid(x, y);

z = interp2(xx0, yy0, z0, xx, yy, method); % use matlab interpolation routine.
