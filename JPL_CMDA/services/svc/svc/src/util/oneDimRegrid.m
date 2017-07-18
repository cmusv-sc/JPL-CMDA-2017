function v_regrid = oneDimRegrid(v, this_x, x, dim, method);
%
% This function regrids data v along the specified dimension (dim, with grid this_x) into a new grid values (x) using
% the specified method (method).
%
if nargin < 5
  method = 'linear';
end

v_size = size(v);
v_size(dim) = length(x); % the end product dimension.

thisIdx = strfind(lower(method), 'log_');

if isempty(thisIdx)
  K = computeInterpKernel(this_x, x, method);
else
  K = computeInterpKernel(log(this_x), log(x), method((thisIdx(1)+4):end));
end

n_x = length(this_x);
if dim == 1
  v = v(:,:);
  n = size(v,2);
  v_regrid = reshape(matrixMultiplicationWithNan(K, v), v_size);
elseif dim == length(v_size)
  v = reshape(v, [], n_x); 
  v_regrid = reshape(matrixMultiplicationWithNan(v, K'), v_size);
else
  n1 = prod(v_size(1:(dim-1)));
  n2 = prod(v_size((dim+1):end));
  size_tmp = [n1, n_x, n2];
  v = reshape(v, size_tmp);
  v_regrid = zeros([n1, length(x), n2], 'single');
  if n1 >= n2
    for ii = 1:n2
      v_regrid(:,:,ii) = matrixMultiplicationWithNan(v(:,:,ii), K');
    end
  else
    for ii = 1:n1
      v_regrid(ii,:,:) = reshape(matrixMultiplicationWithNan(reshape(v(ii,:,:), n_x, []), K'), [1, n_x, n2]);
    end
  end
end

v_regrid = reshape(v_regrid, v_size);
