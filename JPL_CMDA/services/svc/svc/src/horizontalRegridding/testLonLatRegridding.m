%inputFile = '/mnt/hgfs/cmacws/data1/data/cmip5/ncc/noresm/tos_Omon_NorESM1-ME_historical_r1i1p1_199501-200512.nc';
%inputFile = '/mnt/hgfs/cmacws/data1/data/cmip5/giss/e2-r/tos_Omon_GISS-E2-R_historical_r1i1p1_200101-200512.nc';
%inputFile = '/mnt/hgfs/cmacws/data1/data/cmip5/giss/e2-r/original/ta_Amon_GISS-E2-R_historical_r1i1p1_195101-200512.nc';
inputFile = '/mnt/hgfs/cmacws/data1/data/cmip5/giss/e2-r/original/rlut_Amon_GISS-E2-R_historical_r1i1p1_195101-197512.nc';

outputFile = '/tmp/xxx3.nc';
varName = 'rlut';
%varName = 'ta';

lat = 2*(-45:45);
lon = 2.5*(0:143);
%lat = -9:2:9;
%lon = 1.25+2.5*(0:8);

delete(outputFile);

status = regridLonAndLat(inputFile, outputFile, varName, lon, lat);
