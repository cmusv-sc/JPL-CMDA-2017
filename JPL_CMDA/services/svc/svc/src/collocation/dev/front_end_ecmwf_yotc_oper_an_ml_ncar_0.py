import numpy as N
import calendar
import datetime
from front_end_abstract import front_end_abstract_uniform
from front_end_util import *


"""
   Class implementing ECMWF interim daily model level data from NCAR
   for parameters 060 to 203 on two different grids
   
   It creates the data structure containing time, latitude, longitude and data.

   The data fields are organized as an unstructured grid for compatibility with the middle end
   It is indexed by the grid point number and time.

   There are fields for lat, long, land/sea mask that are indexed by grid point number.

   Latitude is in the range 90 to -90.  Longitude is in the range -180 to 180.
"""

#
# "yt_oper_an_ml_yyyymmdd00_0hh_0hh_133128_248128_400.nc"  time(4) lvl(91/92) lat(800)  lon(1600)  lyx -> dl
# "yt_oper_an_ml_yyyymmdd00_0hh_0hh_133128_248128_640.nc"  time(4) lvl(xx/xx) lat(1280) lon(2560)  lyx -> dl
#

class front_end_ecmwf_yotc_oper_an_ml_ncar_0 (front_end_abstract_uniform):
    def load_vfile (self, filename):
        print "entering front_end_ecmwf_yotc_oper_an_pl_ncar_0.load_vfile - filename = ", filename
        
        ncfile = front_end_NetCDF_helper()
        ExcludeList = ['initial_time0_encoded', 'initial_time0_hours', \
                       'lv_HYBL0',  'lv_HYBL0_a',  'lv_HYBL0_b', \
                       'lv_HYBL_i1_a', 'lv_HYBL_i1_b', 'P0', \
                       'g4_lon_4', 'g4_lat_3']
        
        # process parameters 133 to 248
        ncfile.open (filename)
        ncfile.exclude (ExcludeList)

        self.load_geoinfo (ncfile, filename)
        self.load_levels  (ncfile)
        self.load_data_tlyx (ncfile)

        ncfile.close()
        
    def create_catalog (self):
        CatFilename = "ecmwf_yotc_oper_an_ml_133_248_ncar_catalog.txt"
        ModelName   = "ECMWF"
        ProdName    = "YOTC Operational Analysis Model Level, Parameters 133 to 248 (NCAR)"
        self.int_create_catalog (CatFilename, ModelName, ProdName)

    def load_geoinfo (self, ncfile, filename):
        # create time array
        NameStrt = filename.rfind("/")
        print "NameStrt:", NameStrt, filename[NameStrt:]
        DateStrt = filename.rindex("yt_oper_an_ml_", NameStrt) + 14

        #print "date start - ", DateStrt
            
        FileDate = filename[DateStrt:DateStrt+14]
        print '**** date - ', FileDate
        
        FileYr = int(FileDate[0:4])
        FileMo = int(FileDate[4:6])
        FileDa = int(FileDate[6:8])
        FileHr = int(FileDate[12:14])

        print "date:", FileYr, FileMo, FileDa, FileHr

        CdfTimeData = N.zeros (1)
        CdfTimeData[0] = calendar.timegm((FileYr, FileMo, FileDa, FileHr, 0, 0))

        print "time = ", CdfTimeData

        # read lat array
        CdfLatData = ncfile.read_data ('g4_lat_3')

        # read lon array
        CdfLonData = ncfile.read_data ('g4_lon_4')

        self.set_src_uniform_grid_info (CdfTimeData, CdfLatData, CdfLonData)
    # end load_geoinfo

    def load_levels (self, ncfile):
        # levels
        LvlName = 'lv_HYBL0'
        print "processing level:", LvlName

        #VarNameList = ncfile.get_varlist()
        #print "keys:", VarNameList.keys()
        
        # get attributes
        MidAttr = ncfile.read_attrs (LvlName)
            
        # add dimension name attribute for level data
        MidAttr['dimension1'] = 'isobaric_level'

        # level data is already 1D
        CdfData  = ncfile.read_data (LvlName)

        self.attach_level (LvlName, MidAttr, CdfData)

        # add other pressure-level related parameters 
        LvlNameList = ['lv_HYBL0_a', 'lv_HYBL0_b', 'lv_HYBL_i1_a', 'lv_HYBL_i1_b', 'P0']
        for level_name in LvlNameList:
          MidAttr = ncfile.read_attrs (level_name)
          CdfData = ncfile.read_data (level_name)
          self.attach_level (level_name, MidAttr, CdfData) 

        # print level names
        # print 'level keys=',  self.Levels.keys()

    # end load levels

    def load_data_tlyx (self, ncfile):
        ##############################################
        # process included data variables (all are dimensioned on (lvl, lat, lon)) 
        #
        print '***********************'
        print 'processing data'
        CdfVarNameList = ncfile.get_varlist()

        for CdfVarName in CdfVarNameList.keys():
            # skip excluded vars
            if CdfVarNameList[CdfVarName]:
                print 'processing ', CdfVarName
  
                # process attributes
                MidAttr = ncfile.read_attrs (CdfVarName)

                # add dimension name attribute for level data
                MidAttr['dimension1'] = 'isobaric_level'

                #print 'processing variable - ', CdfVarName, ', ', MidAttr['long_name']

                # get CDF data (shape [lvl,long,lat])
                CdfData  = ncfile.read_data (CdfVarName)

                # reformat for middle end (time, lvl, lat, lon) -> (dpt, lvl)
                MidData = self.cvt_lyx_dl (CdfVarName, CdfData)

                # insert into dictionary
                self.attach_data (CdfVarName, MidAttr, MidData)
            # if included var
        # for all vars
    # end load_data_tlyx
# end front_end_ecmwf_yotc_oper_an_ml_ncar_0
