import numpy as N
import os, sys, re, array, gzip
import calendar
import util as UT
from Scientific.IO.NetCDF import NetCDFFile as Dataset
from numpy import arange, dtype

class back_end():
    """Class implementing data write-out."""

# Define parameters giving the data and array dimensions
    def __init__(self, format):
	self.format = format
	self.vars = []
	self.fvars = []




    def set_output_filename(self, file):
	self.file = file

    def set_target_time(self, time):
        self.target_time = time
	### print 'in back_end, self.target_time = ', self.target_time

    def set_target_lat(self, lat):
        self.target_lat = lat

    def set_target_lon(self, lon):
        self.target_lon = lon

    def set_target_data(self, data):
        self.target_data = data

    def set_target_levels(self, levels):
        self.target_levels = levels

    def set_invalid_data(self, invalid_data):
        self.invalid_data = invalid_data 

    def write_output(self):
        local_dimension_directory={}
	if self.format == 'netCDF':
	    # open a new netCDF file for writing.
	    ncfile = Dataset(self.file,'w')

	    ndim = len(self.target_time)
	    #--print 'ndim: ', ndim
	    ncfile.createDimension('time', ndim)

	    # create variables
	    # first argument is name of variable, second is datatype, third is
	    # a tuple with the names of dimensions.
	    time = ncfile.createVariable('time',dtype('float64').char,('time', ))
	    lats = ncfile.createVariable('latitude',dtype('float64').char,('time', ))
	    lons = ncfile.createVariable('longitude',dtype('float64').char,('time', ))

	    time.units = 'second (since midnight of 1/1/1970)'
	    lats.units = 'degree'
	    lons.units = 'degree'

	    # create variables for levels
	    # first argument is name of variable, second is datatype, third is
	    # a tuple with the names of dimensions.
	    lkeys = self.target_levels.keys()
	    #--print 'lkeys: ', lkeys
	    if len(lkeys) > 0:
		self.lvars = [0]*len(lkeys)
	    kk = 0
	    for k in lkeys:
		#--print 'k: ', k
		kname = k.replace(' ', '_')
		#--print 'kk: ', kk, ', kname: ', kname

		atuple = self.target_levels[k]
		attribute = atuple[0]
		#--print 'attribute: ', attribute
		local_level = atuple[1]
		### print 'local_level: ', local_level
		#--print 'local_level.shape: ', local_level.shape

		lc = 'lc-' + str(kk)
		#--print 'lc: ', lc

                if attribute.has_key('dimension1'):
                       lc = attribute['dimension1']
                       if (local_dimension_directory.has_key(lc) == False):
                          ncfile.createDimension(lc, len(local_level))
                          local_dimension_directory[lc] = len(local_level) 
                else:
		       ncfile.createDimension(lc, len(local_level))

		self.lvars[kk] = ncfile.createVariable(kname, dtype('float64').char, (lc, ))

		if attribute.has_key('units'):
		    self.lvars[kk].units = attribute['units']
		#else:
		#    self.lvars[kk].units = ''

		if attribute.has_key('long_name'):
		    self.lvars[kk].long_name = attribute['long_name']
		kk += 1

	    # end of for k loop

	    # write data to variables for levels
	    for kk in range(len(lkeys)):
		### print 'kk: ', kk
		### print 'self.target_levels[lkeys[kk]][1].shape: ', self.target_levels[lkeys[kk]][1].shape
		### print 'len(self.target_levels[lkeys[kk]][1]): ', len(self.target_levels[lkeys[kk]][1])
		self.target_levels[lkeys[kk]][1].shape = (len(self.target_levels[lkeys[kk]][1]), )
		self.lvars[kk][:] = self.target_levels[lkeys[kk]][1]
	    # end of for kk loop

	    # create variables for data
	    # first argument is name of variable, second is datatype, third is
	    # a tuple with the names of dimensions.
	    keys = self.target_data.keys()
	    #--print 'keys: ', keys
	    self.vars = [0]*len(keys)
	    kk = 0
	    for k in keys:
		#--print 'k: ', k
		kname = k.replace(' ', '_')
		#--print 'kk: ', kk, ', kname: ', kname

		#--print 'attribute keys: ', self.target_data[k][0].keys()
		s = self.target_data[k][1].shape
		d2 = len(s)
		cc = 'cc-' + str(kk)
		#--print 'cc: ', cc
		if d2 == 1:
		    #--print '--- 1D data'
		    self.vars[kk] = ncfile.createVariable(kname, dtype('float64').char,('time', ))
		elif d2 == 2:
		    #--print '--- 2D data'
                    if self.target_data[k][0].has_key('dimension1'):
                       local_dimension = self.target_data[k][0]['dimension1']
                       cc = local_dimension
                       if (local_dimension_directory.has_key(local_dimension) == False):
                          #print 'local dimension =', local_dimension
                          ncfile.createDimension(local_dimension, s[1])
                          local_dimension_directory[local_dimension] = s[1]
                    else: 
		      ncfile.createDimension(cc, s[1])
		    self.vars[kk] = ncfile.createVariable(kname, dtype('float64').char,('time', cc))
		elif d2 == 3:
		    #--print '--- 3D data'
		    cc1 = cc+'1'
		    cc2 = cc+'2'
		    ncfile.createDimension(cc1, s[1])
		    ncfile.createDimension(cc2, s[2])
		    self.vars[kk] = ncfile.createVariable(kname, dtype('float64').char,('time', cc1, cc2))
		elif d2 == 4:
		    #--print '--- 4D data'
		    cc1 = cc+'1'
		    cc2 = cc+'2'
		    cc3 = cc+'3'
		    ncfile.createDimension(cc1, s[1])
		    ncfile.createDimension(cc2, s[2])
		    ncfile.createDimension(cc3, s[3])
		    self.vars[kk] = ncfile.createVariable(kname, dtype('float64').char,('time', cc1, cc2, cc3))

		if self.target_data[k][0].has_key('units'):
		    self.vars[kk].units = self.target_data[k][0]['units']
		#else:
		#    self.vars[kk].units = ''
		if self.target_data[k][0].has_key('long_name'):
		    self.vars[kk].long_name = self.target_data[k][0]['long_name']
		#else:
		#    self.vars[kk].long_name = ''


                # add missing_value in the variable attribute
                self.vars[kk].missing_value = UT.NAN

                # add invalid_data in the variable attribute from collocation
                self.vars[kk].collocation_invalid_value = self.invalid_data

		kk += 1

	    # end of for k loop

	    # write data to variables
	    self.target_time.shape = (ndim, )
	    self.target_lat.shape = (ndim, )
	    self.target_lon.shape = (ndim, )

	    time[:] = self.target_time
	    lats[:] = self.target_lat
	    lons[:] = self.target_lon

	    #--print 'in backend: self.target_data[keys[0]][1]: ', self.target_data[keys[0]][1]

	    # write data to variables for data
	    for kk in range(len(keys)):
		#--print 'kk: ', kk
		#--print 'self.target_data[keys[kk]][1].shape: ', self.target_data[keys[kk]][1].shape
		s3 = self.target_data[keys[kk]][1].shape
		d3 = len(s3)
		if d3 == 1:
		    self.target_data[keys[kk]][1].shape = (ndim, )
		elif d3 == 2:
		    self.target_data[keys[kk]][1].shape = (ndim, s3[1])
		elif d3 == 3:
		    self.target_data[keys[kk]][1].shape = (ndim, s3[1], s3[2])
		elif d3 == 4:
		    self.target_data[keys[kk]][1].shape = (ndim, s3[1], s3[2], s3[3])

		#--print 'self.target_data[keys[kk]][1].shape: ', self.target_data[keys[kk]][1].shape
		self.vars[kk][:] = self.target_data[keys[kk]][1]

	    # end of for kk loop

	    ncfile.close()


