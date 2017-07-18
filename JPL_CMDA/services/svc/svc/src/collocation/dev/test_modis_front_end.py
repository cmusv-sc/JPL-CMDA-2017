#
# This unittest is geared toward testing the reshaping functionality in
# select front ends.
#

import sys
import numpy as N
import front_end_modis_cloud_1km_dev as FEMODIS
import Scientific.IO.NetCDF as NetCDFIO
from Scientific.IO.NetCDF import NetCDFFile as Dataset
from numpy import arange, dtype


# Test if two 2D arrays of the same size have the same content
def test_equal(lhs, rhs):
    
    i = j = 0
    while j < lhs.shape[0]:
        while i < lhs.shape[1]:
            #print 'item = ', lhs[j][i]
            if lhs[j][i] != rhs[j][i]:
                return 0
            i = i + 1
        i = 0
        j = j + 1

    return 1

def test_modis():
        
    modis_file      = "MYD06_L2.A2010100.0755.051.2010108054555.hdf"
    print "****** Reading MODIS data from file: ", modis_file
    modis           = FEMODIS.front_end_modis_cloud_1km_dev(modis_file)
    tim=modis.get_time()
    lat=modis.get_latitude()
    lon=modis.get_longitude() 
    dat=modis.get_data()
    print dat.keys()
    cwp=dat['Cloud_Water_Path']
 
    # print lat, lon, lwp
    ncfile = Dataset('modis_1km.nc','w')
    ndim = len(lat)
    ncfile.createDimension('time',ndim)
    time = ncfile.createVariable('time',dtype('float32').char,('time', ))
    lats = ncfile.createVariable('latitude',dtype('float32').char,('time', ))
    lons = ncfile.createVariable('longitude',dtype('float32').char,('time', ))
    cwps = ncfile.createVariable('cloud_water_path',dtype('float32').char,('time', ))
    time[:] = N.cast['float32'](tim)
    lats[:] = N.cast['float32'](lat)
    lons[:] = N.cast['float32'](lon)
    cwps[:] = N.cast['float32'](cwp[1])
    ncfile.close()    

test_modis()

# Very grueling to work up good test data for any 3D, 4D and 5D cases.
# Consider extending this unittest here if time permits.  In the general case
# what should happen is that dimensions 1 and 2 get combined into 1 dim and the
# remaining dimensions remain intact.  The reordering takes place only along the
# combined dimension.




