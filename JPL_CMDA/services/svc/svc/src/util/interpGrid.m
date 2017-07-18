function newGrid = interpGrid(origGrid, nTimes)

if nargin < 2
  nTimes = 1;
end

if nTimes == 1
  newGrid = zeros(length(origGrid)*2 - 1, 1);
  newGrid(1:2:end) = origGrid;
  newGrid(2:2:end) = 0.5*(origGrid(1:(end-1)) + origGrid(2:end));
elseif nTimes < 1
  error(['Invalid second argument nTimes = ' num2str(nTimes) '!']);
else
  newGrid = interpGrid(interpGrid(origGrid, nTimes-1));
end

