function fileName_short = limitFileNameLength(fileName, n)
% 
% This function limit the file length to (2*n+5);
%
if nargin < 2
  n = 50;
end

if length(n) == 1
  if length(fileName) > (2*n+5)
    fileName_short = [fileName([1:n]), '_xxx_' fileName(end+[(-(n-1)):0])];
  else
    fileName_short = fileName;
  end
else
  if length(fileName) > (sum(n(1:2)) + 5)
    fileName_short = [fileName([1:n(1)]), '_xxx_' fileName(end+[(-(n(2)-1)):0])];
  else
    fileName_short = fileName;
  end
end
