import numpy as N
import os, sys, re, array, gzip
import calendar
import util as UT
from Scientific.IO.NetCDF import NetCDFFile
from hdf import HdfFile, TAI
from numpy import arange, dtype

class front_end_ecmwf_yotc_aos_0p25deg():
    """Class implementing ECMWF data reading.
       It creats the data structure containing time, latitude, longitude and data.
       The data consists of the attribute and data field.  
       The input time array is one dimension array representing the first dimension of the data field.
       The input latitude array is one dimension array representing the second dimension of the data field.
       The input longitude array is one dimension array representing the third dimension of the data field.
       The time, lat and lon arrays are expanded out so that there is one entry in each
          for each point on the grid.  We do this to treat data laid out on a regular grid the
          same as we treat irregularly gridded data - allowing us to use a generic middle end for both.
       The data field is one-dimensional array
       The missing value of the data field is replaced with UT.NAN (=-999). 
    """

    def __init__(self, filename):

        self.file = filename
        self.time = N.array([])
        self.latitude = N.array([])
        self.longitude = N.array([])
        
        self.levels = {}
        self.data   =  {}
        self.read_data()

    def get_time(self):
        return self.time

    def get_latitude(self):
        return self.latitude

    def get_longitude(self):
        return self.longitude
    
    def get_levels(self):
        return self.levels

    def get_data(self):
        return self.data
    
    def get_src_uniform_grid_info(self):
        return (self.intime_size, self.inlat_size, self.inlon_size)

    def read_data(self):

        # open a new netCDF file for reading.
        ncfile = NetCDFFile(self.file,'r')
        
        dimNames = ncfile.dimensions.keys()
        variableNames = ncfile.variables.keys()

        #print dimNames
        #print variableNames
        
        # Get the geolocation data
        intime         = ncfile.variables['initial_time0_hours']
        inlatitude     = ncfile.variables['g0_lat_1']
        inlongitude    = ncfile.variables['g0_lon_2']
                 
        self.intime_size = N.size(intime)    
        self.inlat_size  = N.size(inlatitude)
        self.inlon_size  = N.size(inlongitude)
 
        #print 'original time size = ', self.intime_size
        #print 'original latitude size = ', self.inlat_size
        #print 'original longitude size =', self.inlon_size
        
        # Here we have to 'expand out' lat, lon and time so that the
        # middle end is permitted to function as it does for irregular
        # grids.  This involves quite a bit of repititive values and
        # increased memory consumption.
        
        new_var_time = N.array([])
        new_var_lat  = N.array([])
        new_var_lon  = N.array([])
        
        coloc_param_size = self.intime_size * self.inlat_size * self.inlon_size
        
        new_var_time.resize(coloc_param_size)
        new_var_lat.resize(coloc_param_size)
        new_var_lon.resize(coloc_param_size)
        
        #print 'new time size = ', new_time_size
        #print 'new latitude size = ', new_lat_size
        #print 'new longitude size =', new_lon_size
                                
        # Now that we have both the original representation of the geolocation params
        # and a properly-sized location to put their expanded representations - do the
        # expansion
        i = j = k = m = 0
        for i in range(0, self.intime_size):
            # Convert hours since 01/01/1900 to unix time
            tk = UT.hours_since_19th_century_to_unix_time(intime[i])
            for j in range(0, self.inlat_size):
                lat_tk = inlatitude[j]
                for k in range(0, self.inlon_size):
                    lon_tk = inlongitude[k]
                    
                    new_var_time[m] = tk
                    new_var_lat[m]  = lat_tk
                    new_var_lon[m]  = lon_tk
                    
                    #print m, ": ", tk, ", ", lat_tk, ", ", lon_tk                   
                    
                    # Show leading edge of expanded colocation params
                    #if(m < 242):
                        #print m, ": ", tk, ", ", lat_tk, ", ", lon_tk

                    m += 1
        
        self.time       = new_var_time
        self.latitude   = new_var_lat
	### convert to (-180,180) so it's consistent with CloudSat
	### self.longitude  = new_var_lon
	self.longitude = N.where(new_var_lon > 180.0, new_var_lon - 360.0, new_var_lon)
                
        # End of colocation parameter expansion for regular grids
        
        #print 'new time size = ', N.size(self.time)
        #print 'new latitude size = ', N.size(self.latitude)
        #print 'new longitude size =', N.size(self.longitude)        

        for i in range(len(variableNames)):
          if(variableNames[i]!='initial_time0_encoded'
                and variableNames[i]!='initial_time0_hours'
                and variableNames[i]!='g0_lat_1' 
                and variableNames[i]!='g0_lon_2'):
              local_var = ncfile.variables[variableNames[i]]  
              # get data of the variable
              local_data = N.array(local_var.getValue())
              # get attributes of the variable
              attList = dir(local_var)
              attribute = {}
              for j in attList:
                  if(j!='assignValue' and j!='getValue' and j!='typecode'):
                    attValue = getattr(local_var, j)
                    attribute[j]=attValue
                    #print j, attValue
                   
              #print variableNames[i], "attribute = ", attribute

              #print 'local data dimension', local_data.shape
            
              # Fill in UT.NAN where data is the value defined by attribute '_FillValue'
              fill_value = N.where(local_data == attribute['_FillValue'])
              local_data[fill_value] = UT.NAN

              # remove unnecessary attribute since we already applied it
              del attribute['_FillValue']
              
              # Now we reshaped have to reshape to 1D for the middle end
              oneD_data = N.reshape(local_data, local_data.shape[0]*local_data.shape[1]*local_data.shape[2])
              
              # store (attribute, data) in the data dictionary
              self.data[variableNames[i]]=(attribute, oneD_data)
              
              #print "attribute         = ", attribute
              #print "data              = ", oneD_data
        
        ncfile.close()


    def create_catalog(self):

        variableNames = self.data.keys()

        print variableNames
        
        file = open("ecmwf_yotc_aos0.25deg_catalog.txt", 'w')
        line = 'Sensor/Model\tData Product\tVariable Name\tVariable Unit\n'
        file.write(line)
        for i in variableNames:
            attribute = self.data[i][0]
            print attribute
            line = 'ECMWF\t0.25 Degree YOTC Analysis, Operational Surface\t%s\t%s\n' %(attribute['long_name'], attribute['units'])
            file.write(line)

        file.close()



  