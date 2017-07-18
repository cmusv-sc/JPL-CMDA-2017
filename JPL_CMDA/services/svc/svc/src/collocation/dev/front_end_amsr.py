#
#    OUTPUT #    amsr_data  (a 1440x720x6x2 array of data)
#    the 6 elements of amsr_data correspond to:
#    1:gmt_time     time of measurement in minute gmt
#    2:sst          sea surface temperature in deg Celcius
#    3:wspd         10m surface wind in m/s
#    4:vapor        columnar water vapor in mm
#    5:cloud        cloud liquid water in mm
#    6:rain         rain rate in mm/hr
#
#    Longitude  is 0.25*xdim+0.125    degrees east
#    Latitude   is 0.25*ydim-89.875

import numpy as N
import os, sys, re, array, gzip
import calendar
import util as UT

class front_end_amsr():
    """Class implementing AMSR data parsing."""

    def __decode_bytes(self, array,values,offset):
	num_lons = 1440
	n = 0
	for byte_val in values:        # Read time converting into a list of lists (matrix)
	    nlat = n / num_lons
	    nlon = n % num_lons
	    value = ord(byte_val)
            if   value == 251: array[nlat][nlon] = UT.NAN   # not processed
            elif value == 252: array[nlat][nlon] = UT.NAN   # ice>0%
            elif value == 253: array[nlat][nlon] = UT.NAN   # bad data
            elif value == 254: array[nlat][nlon] = UT.NAN   # no observation
            elif value == 255: array[nlat][nlon] = UT.NAN   # land
            else:              array[nlat][nlon] = value * array[nlat][nlon] + offset
	    n += 1

	return (array)

# Define parameters giving the data and array dimensions
    def __init__(self, file):
    	self.file = file;
    	self.fieldDict = {'file': self.file}
        self.levels   = {}
        self.dataDict = {}
        ### self.index_data_with_lat_lon = []    
    	num_lons = 1440
    	num_lats = 720
    	num_maps = 6
    	num_pass = 2
    	num_locs = num_lons*num_lats
    	datasize = num_locs*num_maps*num_pass
    
        # Read data from the binary file into the array variable 'byte_array'
    	if(re.search("\.gz",self.file)):         # If file is gzipped
    	    #print "****** Found .gz file"
    	    fileobj    = gzip.GzipFile(self.file, 'rb')  # Read directly the gz file
    	    byte_array = fileobj.read(datasize)        # Load data from file into array 'byte_array'
    	else:                                  # If file is unzipped
    	    fileobj    = open(self.file, mode='rb')      # Open data file to read in read binary mode
    	    byte_array.fromfile(fileobj, datasize)     # Load data from file into array 'byte_array'
    
    	fileobj.close()
    
        ####################################################################################
        # Extract the information from byte_array into separate arrays for each variable   #
        ####################################################################################
    
        ###print ""
        ###print "   ########### Extracting UTC Time in minutes ########### "
    
        # Define the list of lists (matrix) to save the time values for the first pass (day side)
        time_dat = [1.0]*num_lats
        for nlat in range(num_lats):
            time_dat[nlat] = [1.0]*num_lons
    
        # Calculate the offset and call the function to convert from byte to minutes
        lat_offset = 0
        self.__decode_bytes(time_dat,byte_array[lat_offset:lat_offset+num_locs],0)
        ta1 = N.reshape(N.array(time_dat), (num_locs,))

        # Define the list of lists (matrix) to save the time values for the second pass (night side)
        time_dat = [1.0]*num_lats
        for nlat in range(num_lats):
            time_dat[nlat] = [1.0]*num_lons

        # Calculate the offset and call the function to convert from byte to minutes
        lat_offset2 = lat_offset + num_locs*num_maps
        self.__decode_bytes(time_dat,byte_array[lat_offset2:lat_offset2+num_locs],0)
        ta2 = N.reshape(N.array(time_dat), (num_locs,))

        # concatenate the time arrayes from the two passes 
        ta = N.concatenate((ta1,ta2))
 
        cnt = 0
        valid = [1]*num_locs*num_pass
        for l in range(len(valid)):
            if ta[l] == UT.NAN:   # no valid data at this time
                valid[l] = 0
            else:   # valid time value
                cnt += 1
    
	### print 'num_locs: ', num_locs, ', cnt: ', cnt

        # copy valid time into array ta1
        ta1 = [6.0]*cnt    # convert to minutes
        ll = 0
        for l in range(len(valid)):
            if valid[l] == 1:
                ta1[ll] *= ta[l]
                ll += 1
    
        # sort data by time
        asat = N.argsort(ta1)


	"""
	print 'Time array in original form (in min): ', N.take(ta1, asat)
	for mmm in range(0, 380):
	    print 'Time in original form (in min)[',mmm,']: ', N.take(ta1, asat)[mmm]
	"""

	"""
	for mmm in range(142880, 142900):
	    print 'Time in original form (in min)[',mmm,']: ', N.take(ta1, asat)[mmm]
	"""


        # convert from UTC time to Unix time
        filename = UT.get_file_name_from_full_name(self.file)
        y = int(filename[6:10])
        mon = int(filename[10:12])
        day = int(filename[12:14])
        print 'date of AMSRE file = ', y, mon, day
        # returns Unix time when this granule starts
        diff = calendar.timegm((y, mon, day, 0, 0, 0))
        print "Unix time diff: ", diff
        self.fieldDict['TIME'] = N.take(ta1, asat)*60 + diff   # convert to seconds
        print 'second of AMSR[0]: ', self.fieldDict['TIME'][0]
        print 'second of AMSR[',cnt-1,']: ', self.fieldDict['TIME'][cnt-1]
        print 'date of AMSR[0]: ', UT.unix_time_to_date(self.fieldDict['TIME'][0])
        print 'date of AMSR[',cnt-1,']: ', UT.unix_time_to_date(self.fieldDict['TIME'][cnt-1])
    
        # Print out some results of reading the time
        ###print 'Time[0][0:5] =',time_dat[0][0:5]
        ###for i in range(273,278): print time_dat[i][:3],';','Time[',i,'][169:175] =',time_dat[i][169:175],';',time_dat[i][num_lons-3:]
        ###print 'Time[',num_lats-1,'][',num_lons-3,':] =',time_dat[num_lats-1][num_lons-3:]
    
        # Define the list of lists (matrix) to save the lat lon values
        lat_dat = [1.0]*num_lats
        for nlat in range(num_lats):
            lat_dat[nlat] = [1.0]*num_lons
    
        lon_dat = [1.0]*num_lats
        for nlat in range(num_lats):
            lon_dat[nlat] = [1.0]*num_lons
    
	# Longitude  is 0.25*xdim+0.125   degrees east
	# Latitude   is 0.25*ydim-89.875
        for nlat in range(num_lats):
            for nlon in range(num_lons):
                lat_dat[nlat][nlon] = 0.25*nlat-89.875
                lon_dat[nlat][nlon] = 0.25*nlon+0.125
		# convert lon to (-180, 180), consistent with CloudSat
		if lon_dat[nlat][nlon] > 180.0:
		    lon_dat[nlat][nlon] -= 360.0
    
        tlat = N.reshape(N.array(lat_dat), (num_locs,))
        tlon = N.reshape(N.array(lon_dat), (num_locs,))
        # make a double copy of the lat and lon for two passes
        tlat = N.concatenate((tlat,tlat))
        tlon = N.concatenate((tlon,tlon))
    
        # copy valid data into array tlat1 and tlon1
        tlat1 = [1.0]*cnt
        tlon1 = [1.0]*cnt
        ll = 0
        for l in range(len(valid)):
            if valid[l] == 1:
                tlat1[ll] = tlat[l]
                tlon1[ll] = tlon[l]
                ll += 1
    
        # reorder array based on time sort
        self.fieldDict['Latitude'] = N.take(tlat1, asat)
        self.fieldDict['Longitude'] = N.take(tlon1, asat)
    
        ###print ""
        ###print "   ########### Extracting the Sea Surface Temperature in Celsius ########### "
    
        # Define the list of lists (matrix) to save the sst values
        sst_dat = [0.15]*num_lats
        for nlat in range(num_lats):
            sst_dat[nlat] = [0.15]*num_lons
    
        # Calculate the new offset and call the function to convert from byte to Celsius
        lat_offset += num_locs
        self.__decode_bytes(sst_dat,byte_array[lat_offset:lat_offset+num_locs],-3.0)
        sa1 = N.reshape(N.array(sst_dat), (num_locs,))
    
        # Define the list of lists (matrix) to save the sst values
        sst_dat = [0.15]*num_lats
        for nlat in range(num_lats):
            sst_dat[nlat] = [0.15]*num_lons
    
        # Calculate the new offset and call the function to convert from byte to Celsius
        lat_offset2 = lat_offset + num_locs*num_maps
        self.__decode_bytes(sst_dat,byte_array[lat_offset2:lat_offset2+num_locs],-3.0)
        sa2 = N.reshape(N.array(sst_dat), (num_locs,))
         
        # Concatenate the two arrays from the two passes
        sa = N.concatenate((sa1,sa2))
    
        # Print out some results of reading the sst
        ###print 'SST[0][0:5] =',sst_dat[0][0:5]
        ###for i in range(273,278): print sst_dat[i][:3],';','SST[',i,'][169:175] =',sst_dat[i][169:175],sst_dat[i][num_lons-3:]
        ###print 'SST[',num_lats-1,'][',num_lons-3,':] =',sst_dat[num_lats-1][num_lons-3:]
    
    
        ###print ""
        ###print "   ########### Extracting the Wind Speed in m/sec ########### "
    
        # Define the list of lists (matrix) to save the wind speeds
        wspd_dat = [0.2]*num_lats
        for nlat in range(num_lats):
            wspd_dat[nlat] = [0.2]*num_lons
    
        # Calculate the new offset and call the function to convert from byte to wind speeds
        lat_offset += num_locs
        self.__decode_bytes(wspd_dat,byte_array[lat_offset:lat_offset+num_locs],0)
        wa1 = N.reshape(N.array(wspd_dat), (num_locs,))
    
        # Define the list of lists (matrix) to save the wind speeds
        wspd_dat = [0.2]*num_lats
        for nlat in range(num_lats):
            wspd_dat[nlat] = [0.2]*num_lons
    
        # Calculate the new offset and call the function to convert from byte to wind speeds
        lat_offset2 = lat_offset + num_locs*num_maps
        self.__decode_bytes(wspd_dat,byte_array[lat_offset2:lat_offset2+num_locs],0)
        wa2 = N.reshape(N.array(wspd_dat), (num_locs,))
    
        # Concatenate the two arrays from the two passes
        wa = N.concatenate((wa1,wa2))

        # Print out some results of reading the sst
        ###print 'WSPD[0][0:5] =',wspd_dat[0][0:5]
        ###for i in range(273,278): print 'WSPD[',i,'][169:175] =',wspd_dat[i][169:175]
        ###print 'WSPD[',num_lats-1,'][',num_lons-3,':] =',sst_dat[num_lats-1][num_lons-3:]
    
        ###print ""
        ###print "   ########### Extracting the Water Vapor column in mm ########### "
    
        # Define the list of lists (matrix) to save the Water vapor columns
        vapor_dat = [0.3]*num_lats
        for nlat in range(num_lats):
            vapor_dat[nlat] = [0.3]*num_lons
    
        # Calculate the new offset and call the function to convert from byte to WV columns
        lat_offset += num_locs
        self.__decode_bytes(vapor_dat,byte_array[lat_offset:lat_offset+num_locs],0)
        va1 = N.reshape(N.array(vapor_dat), (num_locs,))
    
        # Define the list of lists (matrix) to save the Water vapor columns
        vapor_dat = [0.3]*num_lats
        for nlat in range(num_lats):
            vapor_dat[nlat] = [0.3]*num_lons
    
        # Calculate the new offset and call the function to convert from byte to WV columns
        lat_offset2 = lat_offset + num_locs*num_maps
        self.__decode_bytes(vapor_dat,byte_array[lat_offset2:lat_offset2+num_locs],0)
        va2 = N.reshape(N.array(vapor_dat), (num_locs,))
    
        # Concatenate the two arrays from the two passes
        va = N.concatenate((va1,va2))

        # Print out some results of reading the sst
        ###print 'VAPOR[0][0:5] =',vapor_dat[0][0:5]
        ###for i in range(273,278): print 'VAPOR[',i,'][169:175] =',vapor_dat[i][169:175]
        ###print 'VAPOR[',num_lats-1,'][',num_lons-3,':] =',vapor_dat[num_lats-1][num_lons-3:]
    
        ###print ""
        ###print "   ########### Extracting the Cloud Liquid Water in mm ########### "
    
        # Define the list of lists (matrix) to save the Cloud Liqued Water columns
        cloud_dat = [0.01]*num_lats
        for nlat in range(num_lats):
            cloud_dat[nlat] = [0.01]*num_lons
    
        # Calculate the new offset and call the function to convert from byte to CLW
        lat_offset += num_locs
        self.__decode_bytes(cloud_dat,byte_array[lat_offset:lat_offset+num_locs],0)
        ca1 = N.reshape(N.array(cloud_dat), (num_locs,))
    
        # Define the list of lists (matrix) to save the Cloud Liqued Water columns
        cloud_dat = [0.01]*num_lats
        for nlat in range(num_lats):
            cloud_dat[nlat] = [0.01]*num_lons
    
        # Calculate the new offset and call the function to convert from byte to CLW
        lat_offset2 = lat_offset + num_locs*num_maps
        self.__decode_bytes(cloud_dat,byte_array[lat_offset2:lat_offset2+num_locs],0)
        ca2 = N.reshape(N.array(cloud_dat), (num_locs,))
    
        # Concatenate the two arrays from the two passes
        ca = N.concatenate((ca1,ca2))

        # Print out some results of reading the sst
        ###print 'CLOUD[0][0:5] =',cloud_dat[0][0:5]
        ###for i in range(273,278): print 'CLOUD[',i,'][169:175] =',cloud_dat[i][169:175]
        ###print 'CLOUD[',num_lats-1,'][',num_lons-3,':] =',cloud_dat[num_lats-1][num_lons-3:]
    
    
        ###print ""
        ###print "   ########### Extracting the Rain Rate in mm/hr ########### "
    
        # Define the list of lists (matrix) to save the Rain Rates
        rain_dat = [0.1]*num_lats
        for nlat in range(num_lats):
            rain_dat[nlat] = [0.1]*num_lons
    
        # Calculate the new offset and call the function to convert from byte to rain rates
        lat_offset += num_locs
        self.__decode_bytes(rain_dat,byte_array[lat_offset:lat_offset+num_locs],0)
        ra1 = N.reshape(N.array(rain_dat), (num_locs,))
  
        # Define the list of lists (matrix) to save the Rain Rates
        rain_dat = [0.1]*num_lats
        for nlat in range(num_lats):
            rain_dat[nlat] = [0.1]*num_lons
    
        # Calculate the new offset and call the function to convert from byte to rain rates
        lat_offset2 = lat_offset + num_locs*num_maps
        self.__decode_bytes(rain_dat,byte_array[lat_offset2:lat_offset2+num_locs],0)
        ra2 = N.reshape(N.array(rain_dat), (num_locs,))
  
        # Concatenate the two arrays from the two passes
        ra = N.concatenate((ra1,ra2))

        # select valid data from the list 
        sa1 = [1.0]*cnt
        wa1 = [1.0]*cnt
        va1 = [1.0]*cnt
        ca1 = [1.0]*cnt
        ra1 = [1.0]*cnt 
        ll = 0
        for l in range(len(valid)):
            if valid[l] == 1:
                sa1[ll] = sa[l]
                wa1[ll] = wa[l]
                va1[ll] = va[l]
                ca1[ll] = ca[l]
                ra1[ll] = ra[l]
                ll += 1

        # prepare the attribute dictionary   
        sa_attributes={'units': 'Celsius', 'long_name': 'sea surface temperature', 'missing_value': UT.NAN}
        wa_attributes={'units': 'meter/sec', 'long_name': '10m surface wind', 'missing_value': UT.NAN}
        va_attributes={'units': 'mm', 'long_name': 'columnar water vapor', 'missing_value': UT.NAN}
        ca_attributes={'units': 'mm', 'long_name': 'cloud liquid water', 'missing_value': UT.NAN}
        ra_attributes={'units': 'mm/hr', 'long_name': 'rain rate', 'missing_value': UT.NAN}
 
        # Here we create the dictionary for the data parameters
        # reorder array based on time sort and put it in the dictionary
        self.dataDict['SST'] = (sa_attributes, N.take(sa1, asat))
        self.dataDict['WSPD'] = (wa_attributes, N.take(wa1, asat))
        self.dataDict['VAPOR'] = (va_attributes, N.take(va1, asat))
        self.dataDict['CLOUD'] = (ca_attributes, N.take(ca1, asat))
        self.dataDict['RAIN'] = (ra_attributes, N.take(ra1, asat))

	# make an array that matches the lat-lon index to the data index
	# the data index should be the time-ordered index
	"""
        asa_asat = N.argsort(asat) # need to find the sorted argument for asat
        index_dat = [UT.NAN]*num_locs
        index_dat = N.array(index_dat)
        ll = 0
        for l in range(0, num_locs):
            if valid[l] == 1:
		index_dat[l]=asa_asat[ll]
                ll += 1
      
        self.index_dat_with_lat_lon = N.reshape(index_dat, (num_lats, num_lons))
	"""

	# O(n) instead of n*log(n) (sort)
	"""
        self.index_dat_with_lat_lon = [UT.NAN]*num_lats
        for nlat in range(num_lats):
            self.index_dat_with_lat_lon[nlat] = [UT.NAN]*num_lons

	for l in range(cnt):
	    lat2 = self.fieldDict['Latitude'][l]
	    lon2 = self.fieldDict['Longitude'][l]
            nlat2 = int((lat2+89.875)/0.25)
            nlon2 = int((lon2-0.125)/0.25)
	    self.index_dat_with_lat_lon[nlat2][nlon2] = l
	"""

        # Print out some results of reading the sst
        ###print 'RAIN[0][0:5] =',rain_dat[0][0:5]
        ###for i in range(273,278): print 'RAIN[',i,'][169:175] =',rain_dat[i][169:175]
        ###print 'RAIN[',num_lats-1,'][',num_lons-3,':] =',rain_dat[num_lats-1][num_lons-3:]

    def get_time(self):
        return self.fieldDict['TIME']

    def get_latitude(self):
        return self.fieldDict['Latitude']

    def get_longitude(self):
        return self.fieldDict['Longitude']
    
    def get_levels(self):
        return self.levels

    def get_data(self):
        return self.dataDict
 
    """
    def get_index_data(self):
	    return self.index_dat_with_lat_lon
    """

    def create_catalog(self):

        variableNames = self.dataDict.keys()

        #print variableNames
        
        file = open("amsr_catalog.txt", 'w')
        line = 'Sensor/Model\tData Product\tVariable Name\tVariable Unit\n'
        file.write(line)
        for i in variableNames:
            attribute = self.dataDict[i][0]
            #print attribute
            line = 'AMSR-E\tDaily EASE-Grid Brightness Temperature\t%s\t%s\n' %(attribute['long_name'], attribute['units'])
            file.write(line)

        file.close()

    """
    def test_index_data(self): 
        num_data = len(self.fieldDict['Latitude'])
        for i in range(num_data):
	    lat=self.fieldDict['Latitude'][i]
            lon=self.fieldDict['Longitude'][i]
            nlat = int((lat+89.875)/0.25)
            nlon = int((lon-0.125)/0.25)
	    index = self.index_dat_with_lat_lon[nlat][nlon]
            if index !=i:
	       print i, 'index for lat, lon (', lat, lon,')', index
    """

 
