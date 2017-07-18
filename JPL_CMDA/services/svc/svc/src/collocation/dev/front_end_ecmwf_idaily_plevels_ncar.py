import numpy as N
import calendar
from datetime import datetime
from front_end_abstract import front_end_abstract_uniform
#from front_end_util import front_end_NetCDF_helper
from front_end_util import *


"""
   Class implementing ECMWF interim daily pressure level data from NCAR
   It creates the data structure containing time, latitude, longitude and data.

   The data fields are organized as an unstructured grid for compatibility with the middle end
   It is indexed by the grid point number and time.

   There are fields for lat, long, land/sea mask that are indexed by grid point number.

   Latitude is in the range 90 to -90.  Longitude is in the range -180 to 180.
"""

class front_end_ecmwf_idaily_plevels_ncar (front_end_abstract_uniform):
    def load_vfile (self, filename):
        print "entering front_end_ecmwf_idaily_plevels_ncar.load_vfile - filename = ", filename
        ncfile = front_end_NetCDF_helper()
        
        # process sc file
        ncfile.open (filename)
        ncfile.exclude (['g4_lat_1', 'g4_lon_2', 'lv_ISBL0'])

        self.load_geoinfo (ncfile, filename)
        self.load_levels  (ncfile)
        self.load_data    (ncfile)

        ncfile.close()

        # build uv filename
        NameLen = len(filename)
        SubStrt = NameLen - 16
        SubEnd  = SubStrt + 2
        filename_uv = filename[0:SubStrt] + 'uv' + filename[SubEnd:NameLen]
        #print "*** uv file = ", filename_uv

        ncfile.open (filename_uv)
        ncfile.exclude (['g4_lat_1', 'g4_lon_2', 'lv_ISBL0'])
        self.load_data (ncfile)

        ncfile.close()
    # end load_vfile

    def create_catalog (self):
        CatFilename = "ecmwf_idaily_plevels_ncar_catalog.txt"
        ModelName   = "ECMWF"
        ProdName    = "ERA Interim Daily Pressure Level (NCAR)"
        self.int_create_catalog (CatFilename, ModelName, ProdName)
    # end create_catalog

    def load_geoinfo (self, ncfile, filename):
        NameLen = len(filename)
        DateStrt = NameLen - 13
        FileDate = filename[DateStrt:DateStrt+10]
        #print '**** date - ', FileDate
        
        FileYr = int(FileDate[0:4])
        FileMo = int(FileDate[4:6])
        FileDa = int(FileDate[6:8])
        FileHr = int(FileDate[8:10])
        
        ctime = calendar.timegm((FileYr, FileMo, FileDa, FileHr, 0, 0))
        CdfTimeData = N.array ([ctime])
        print 'date: ', FileYr, '/' , FileMo, '/' , FileDa, '/', FileHr, ', unix time: ', ctime

        CdfLatData  = ncfile.read_data('g4_lat_1')
        CdfLonData  = ncfile.read_data('g4_lon_2')

        self.set_src_uniform_grid_info (CdfTimeData, CdfLatData, CdfLonData)
    # end load_geoinfo

    def load_levels (self, ncfile):
        LvlList = ['lv_ISBL0']
        for CdfLvlName in LvlList:
            # level data is already 1D
            MidAttr = ncfile.read_attrs (CdfLvlName)

            # add dimension name attribute for level data
            MidAttr['dimension1'] = 'isobaric_level'

            CdfVarData = ncfile.read_data (CdfLvlName)

            self.attach_level (CdfLvlName, MidAttr, CdfVarData)
    # end load levels

    def load_data (self, ncfile):
        ##############################################
        # process included data variables (all are dimensioned on (lvl, lat, lon)) 
        #
        print '***********************'
        print 'processing source data'
        CdfVarNameList = ncfile.get_varlist()

        for CdfVarName in CdfVarNameList.keys():
            # skip excluded vars
            if CdfVarNameList[CdfVarName]:
                #print 'processing ', CdfVarName
  
                # process attributes
                MidAttr = ncfile.read_attrs (CdfVarName)

                # add dimension name attribute for level data
                MidAttr['dimension1'] = 'isobaric_level'

                #print 'processing variable - ', CdfVarName, ', ', MidAttr['long_name']

                # get CDF data (shape [lvl,long,lat])
                CdfData  = ncfile.read_data (CdfVarName)
		#print CdfData.shape

                MidData = self.cvt_lyx_dl (CdfVarName, CdfData)
                
                # reformat for middle end from 3D (lev, lat, lon) to 2D (grid, lev)
                #CdfData = N.swapaxes(CdfData, 0, 1) # swap lev with lat
                #CdfData = N.swapaxes(CdfData, 1, 2) # swap lev with lon
                #dshape = CdfData.shape  
                #MidData = N.reshape(CdfData, (dshape[0]*dshape[1], dshape[2]))

                # insert into dictionary
                self.attach_data (CdfVarName, MidAttr, MidData)
            # if included var
        # for all vars
    # end load_data
# end front_end_ecmwf_idaily_plevels_ncar
