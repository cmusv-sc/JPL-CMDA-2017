function grid = generateUniformGrid(x_min, x_max, dx)
%
% This function creates a uniform grid
%
nGrid = ceil((x_min - x_max)/dx);
grid_start = x_min + dx(0:(nGrid-1));
grid_end = [x_min + dx(1:(nGrid-1)), x_max];
