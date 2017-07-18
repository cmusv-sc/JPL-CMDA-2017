function formula = formulaParser(formula_str)
%
% This function parses the formula in string
%
%

% Remove the indexing to array 
formula_str = regexprep(formula_str, '\([A-z]\)', '');
formula_str = regexprep(formula_str, '\([A-z,\,]*\)', '');

% Let us first add the relevant operations by an extra space
formula_str = strrep(formula_str, '*', ' * ');
formula_str = strrep(formula_str, '+', ' + ');
formula_str = strrep(formula_str, '=', ' = ');
formula_str = strrep(formula_str, '  ', ' ');
formula_str = removeTrailingNullChar(formula_str);

% Now the operators and variables are separated by spaces, parse it
terms = strchop(formula_str, ' ');

% Let us first find the "=" sign
equalIdx = find(~cellfun('isempty', strfind(terms, '=')));

% Left hand side
lhs = {terms{1:(equalIdx-1)}};
rhs = {terms{(equalIdx+1):end}};

% Let us assemble the formula
formula.output = lhs;
formula.inputVars = {rhs{1:2:end}};
formula.op = {rhs{2:2:end}};
