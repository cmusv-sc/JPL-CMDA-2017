import numpy as N
import array
import calendar
import datetime
import util as UT
from Scientific.IO.NetCDF import NetCDFFile
import types

class front_end_ecmwf_idaily_surface_ncar():
    """Class implementing ECMWF interim daily surface data
       It creates the data structure containing time, latitude, longitude and data.

       The data fields are organized as an unstructured grid for compatibility with the middle end
       It is indexed by the grid point number and time.

       There are fields for lat, long, land/sea mask that are indexed by grid point number.

       Latitude is in the range 90 to -90.  Longitude is in the range -180 to 180.
 
       ??The data field is converted to a proper value by applying "scale_factor" and "add_offset".
       ??linear conversion for UOM?  This is not present in the NCAR version of the file
       ?? The orig file used integer "counts" that needed to be converted back to floating point
       ?? this compressed the file size.
       
       The missing value of the data field is replaced with UT.NAN (=-999). 
    """

    def __init__(self, filename):

        self.filename = filename

        self.utime     = None
        self.latitude  = None
        self.longitude = None

        # geo location information
        self.geoinfo = {"lon":None, "lat":None}  # indexed by geoloc point no

        self.LfracName = "LSM_GDS4_SFC"   # land sea mask (land fraction) variable name (useful for debugging)

        # data variable names
        self.CdfLatSize  = 0
        self.CdfLonSize  = 0
        
        self.data   = {}
        self.levels = {}
        
        self.process_file ()
    # end __init__

    # get MidIdx from TimeIdx, LatIdx, LonIdx

    ############################################
    def get_src_uniform_grid_info(self):
        return (self.intime_size, self.CdfLatSize, self.CdfLonSize)
    
    def get_time(self):
        #print "front_end.get_time = ", min(self.utime), max(self.utime)
        return self.utime

    def get_latitude(self):
        #print "front_end.get_latitude = ",  min(self.latitude), max(self.latitude)
        return self.latitude

    def get_longitude(self):
        #print "front_end.get_longitude = ", min(self.longitude), max(self.longitude)
        return self.longitude

    def get_data(self):
        #print "front_end.get_data()"
        return self.data

    def get_levels(self):
        return self.levels

    # called by constructor to generate data structures
    def process_file(self):        
        print 'using NCAR daily surface front end - file = ' + self.filename
        ncfile = NetCDFFile(self.filename,'r')

        NameLen = len(self.filename)
        DateStrt = NameLen - 13
        FileDate = self.filename[DateStrt:DateStrt+10]
        #print '**** date - ', FileDate
        
        FileYr = int(FileDate[0:4])
        FileMo = int(FileDate[4:6])
        FileDa = int(FileDate[6:8])
        FileHr = int(FileDate[8:10])
        
        ctime = calendar.timegm((FileYr, FileMo, FileDa, FileHr, 0, 0))
        print 'date: ', FileYr, '/' , FileMo, '/' , FileDa, '/', FileHr, ', unix time: ', ctime

        # single time step
        self.intime_size = 1
        
        # Get the geolocation data
        CdfVarLat = ncfile.variables['g4_lat_0']
        CdfVarLon = ncfile.variables['g4_lon_1']

        CdfLatData = N.array(CdfVarLat.getValue())
        CdfLonData = N.array(CdfVarLon.getValue())

        self.CdfLatSize  = N.size(CdfVarLat)
        self.CdfLonSize  = N.size(CdfVarLon)
        
        # Here we have to 'expand out' lat, lon and time so that the
        # middle end is permitted to function as it does for irregular
        # grids.  This involves quite a bit of repititive values and
        # increased memory consumption.

        # calculate size of single dimension for (time,lat,lon)
        #self.grid_size = self.intime_size * self.CdfLatSize * self.CdfLonSize
        self.grid_size = self.CdfLatSize * self.CdfLonSize
        print "Number of time steps = ", self.intime_size
        print "Lat Size = ", self.CdfLatSize
        print "Lon Size = ", self.CdfLonSize
        print "grid size = ", self.grid_size

        mid_time = N.zeros(self.grid_size)
        mid_lat  = N.zeros(self.grid_size)
        mid_lon  = N.zeros(self.grid_size)

        # fill in the lat long values for each grid point (lon varies fastest in mid data)
        grid_pt = 0
        for j in range(0, self.CdfLatSize):
            lat_tk = CdfVarLat[j]
            for k in range(0, self.CdfLonSize):
                lon_tk = CdfVarLon[k]
		#if lon_tk>180:
		#	lon_tk = lon_tk-360.0 # make sure longitude is in (-180,180).

                mid_time[grid_pt] = ctime
                mid_lat[grid_pt]  = lat_tk
                mid_lon[grid_pt]  = lon_tk
                grid_pt += 1

        # convert long range to -180 to 180
        self.longitude = N.where(mid_lon > 180.0, mid_lon - 360.0, mid_lon)

        self.utime     = mid_time
        self.latitude  = mid_lat
        
        ##############################################
        # process data variables
        #
        # get info about dimensions and variables
        print '***********************'
        print 'processing data'
        CdfVarNameList = ncfile.variables.keys()

        #print 'types - ', dir(types)
        
        for CdfVarName in CdfVarNameList:
            # skip geoinfo vars
            if ((CdfVarName != 'g4_lon_1') and (CdfVarName != 'g4_lat_0')):
            # debug if (CdfVarName == self.LfracName):
                #print CdfVarName

                CdfVar = ncfile.variables[CdfVarName]

                # process attributes
                MidAttr = {}

                AttrNameList = dir(CdfVar)
                for AttrName in AttrNameList:
                    # remove extra attrs
                    if ((AttrName != 'assignValue') & (AttrName != 'getValue') & (AttrName != 'typecode')):
                        #print 'attr name ', AttrName
                        CdfAttr = getattr(CdfVar, AttrName)
                        AttrType = type(CdfAttr)

                        #print 'attribute - ', CdfVarName, ':', AttrName, ', type ', AttrType

                        # type is string or array
                        if (AttrType == types.StringType):
                            MidAttr[AttrName] = CdfAttr
                        else:
                            #print 'array', CdfVarName, ':', AttrName, ', type '#, AttrName.typecode
                            MidAttr[AttrName] = N.array(CdfAttr)

                # get CDF data (shape [long,lat])
                CdfData = N.array(CdfVar.getValue())

                # creat flat destination array
                MidData = N.array([])
                MidData.resize(self.grid_size)

                # copy to flat array
                # loop iteration must match geo info setup
                MidIndx = 0
                for LatIndx in range(0, self.CdfLatSize):
                    for LonIndx in range(0, self.CdfLonSize):
                        Val = CdfData[LatIndx,LonIndx]
                            
                        MidData[MidIndx] = Val
                        MidIndx += 1

                # print 'shape ', CdfVarName, MidData.shape, self.grid_size

                # insert into dictionary
                self.data[CdfVarName] = (MidAttr, MidData)

        ncfile.close()
    # end load_data

    ##################
    def create_catalog(self):

        variableNames = self.data.keys()
        
        file = open("ecmwf_idaily_surface_ncar_catalog.txt", 'w')
        line = 'Sensor/Model\tData Product\tVariable Name\tVariable Unit\n'
        file.write(line)
        for i in variableNames:
            attribute = self.data[i][0]
            #print attribute
            line = 'ECMWF\tERA Interim Daily Surface (NCAR)\t%s\t%s\n' %(attribute['long_name'], attribute['units'])
            file.write(line)

        file.close()
