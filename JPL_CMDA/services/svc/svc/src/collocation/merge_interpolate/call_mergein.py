from ctypes import *
import numpy as N
import time
import math

# load the shared library
ms=CDLL('./_mergein.so')

latmin = -113
latmax = -111
lonmin = 81
lonmax = 83
print 'latmin: ', latmin
print 'latmax: ', latmax
print 'lonmin: ', lonmin
print 'lonmax: ', lonmax

latinc = 1.0
loninc = 1.0
print 'latinc: ', latinc
print 'loninc: ', loninc

W = 0.001
R = 0.8
T0 = 1000.0
print 'time weight: ', W
print 'search radius: ', R
print 'time of interest: ', T0

# input array
# lat, lon, time, value
sz1 = 3  # num of query points
qry_lat=N.array(range(sz1),dtype=N.float64)
qry_lon=N.array(range(sz1),dtype=N.float64)
qry_t=N.array(range(sz1),dtype=N.float64)
qry_val=N.array(range(sz1),dtype=N.float64)

for i in range(0, sz1):
    ### qry_t[i] = T0 + 30
    qry_t[i] = T0

### for i in range(0, sz1/2):
    ### qry_t[i] = T0

### for i in range(sz1/2+1, sz1):
    ### qry_t[i] = T0

for i in range(0, sz1):
    qry_val[i] = i + 500.0
    print 'qry_val: ', qry_val[i]

qry_lat[0] = -113
for i in range(1, sz1):
    qry_lat[i] = qry_lat[i-1] + 0.5

qry_lon[0] = 81
for i in range(1, sz1):
    qry_lon[i] = qry_lon[i-1] + 0.6

# memory for output lat, lon, value
nlat = int(math.ceil((latmax - latmin)/latinc)) + 1
nlon = int(math.ceil((lonmax - lonmin)/loninc)) + 1
print 'nlat: ', nlat
print 'nlon: ', nlon

# uniform grid
grid_lat = N.array(range(nlat*nlon),dtype=N.float64)
grid_lon = N.array(range(nlat*nlon),dtype=N.float64)
value = N.array(range(nlat*nlon),dtype=N.float64)

print 'nan: ', float('nan')

for i in range(0, nlat*nlon):
    value[i] = float('nan')

print '***** before calling C'

flag_nearest = 1
start = time.time()
rt1 = ms.mergein(qry_lat.ctypes.data_as(c_void_p), qry_lon.ctypes.data_as(c_void_p), 
       qry_t.ctypes.data_as(c_void_p), qry_val.ctypes.data_as(c_void_p),int(sz1),
       c_double(latmin), c_double(latmax), c_double(lonmin), c_double(lonmax), c_double(latinc), c_double(loninc),
       c_double(W), c_double(R), grid_lat.ctypes.data_as(c_void_p), grid_lon.ctypes.data_as(c_void_p), c_double(T0), 
       value.ctypes.data_as(c_void_p), int(nlat), int(nlon), int(flag_nearest))
print 'rt1: ', rt1
print ''

print 'grid point value: '
for i in range(0, nlat*nlon):
    print value[i]

end = time.time()
print '****** elasped time: ', end - start

