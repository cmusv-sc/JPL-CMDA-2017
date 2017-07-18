function idx = indexWithin(data_vec, valueRange)
%
% This function returns the index within the value Range (inclusive);
%
% Input:
%   data_vec    -- a vector contains the data
%   valueRange  -- an interval specifying the data range, [min, max] or [max, min]
% Output:
%   idx         -- index to the data vector for data within the specified value range.
%
idx = find(data_vec >= min(valueRange) & data_vec <= max(valueRange));
