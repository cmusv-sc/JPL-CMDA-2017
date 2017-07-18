fn = '/home/zhai/cmip5/ukmo/hadgem2-a/ts_Amon_HadGEM2-A_amip_r1i1p1_197809-200811.nc';
fd = netcdf(fn, 'r');

ts = fd{'ts'}(:);
lon = fd{'lon'}(:);
lat = fd{'lat'}(:);

ts_clim = simpleClimatology(ts,1);

