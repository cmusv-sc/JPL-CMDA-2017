function C = matrixMultiplicationWithNan(A, B)
%
% This function computes matrix multipiclation C = AB, where
% A may contain "NaN" and B is sparse. We use NaN*0 = 0 instead of
% NaN. This is done by computing only the matrix multiplication 
% on the nonzero elements of B.
%

nCol = size(B, 2);

C = zeros(size(A,1), nCol);

for colI = 1:nCol
  % Find the nonzero indices in sparse matrix B
  nonZeroIdx = find(B(:,colI) ~= 0);
  C(:, colI) = A(:,nonZeroIdx) * B(nonZeroIdx, colI);
end
