function dataRange = rangeOfDataInStructArray(data_array, fieldName)
%
% This function returns range of data stored in a data array
%
n = length(data_array);
if n < 1
  dataRange = [];
else
  dataRange = [eval(['min(data_array(1).' fieldName '(:));']), eval(['max(data_array(1).' fieldName '(:));'])];
  for ii = 2:n
    dataRange(1) = min(dataRange(1), eval(['min(data_array(' num2str(ii) ').' fieldName '(:));']));
    dataRange(2) = max(dataRange(2), eval(['max(data_array(' num2str(ii) ').' fieldName '(:));']));
  end
end
