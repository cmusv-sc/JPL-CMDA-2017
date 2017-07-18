function C = findLaterTime(A, B)
C=A;
if B.year>A.year
	C=B;
elseif B.year==A.year && B.month>A.month
	C=B;
end

