function termVar = lookupTermName(termName, termNamePairs, defaultValue)
nVar = size(termNamePairs, 2);

if nargin < 3
  tempVar = [];
else
  termVar = defaultValue;
end

for ii = 1:nVar
  if strcmp([termName ':'], termNamePairs{1,ii})
    termVar = termNamePairs{2,ii};
    return;
  end
end
