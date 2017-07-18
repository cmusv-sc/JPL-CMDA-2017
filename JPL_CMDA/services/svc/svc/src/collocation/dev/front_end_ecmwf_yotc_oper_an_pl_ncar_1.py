import numpy as N
import calendar
import datetime
from front_end_abstract import front_end_abstract_uniform
#from front_end_util import front_end_NetCDF_helper
from front_end_util import *


"""
   Class implementing ECMWF interim daily pressure level data from NCAR
   for parameters 129 to 157 on two different grids
   
   It creates the data structure containing time, latitude, longitude and data.

   The data fields are organized as an unstructured grid for compatibility with the middle end
   It is indexed by the grid point number and time.

   There are fields for lat, long, land/sea mask that are indexed by grid point number.

   Latitude is in the range 90 to -90.  Longitude is in the range -180 to 180.
"""

#
# "000_018_129128_157128_799.nc"  time(4) lvl(25) real(2) lat(800)  lon(800)  tlayx
# "000_018_129128_157128_1279.nc" time(4) lvl(25) real(2) lat(1280) lon(1280) tlayx
#

class front_end_ecmwf_yotc_oper_an_pl_ncar_1 (front_end_abstract_uniform):
    def load_vfile (self, filename):
        print "entering front_end_ecmwf_yotc_oper_an_pl_ncar_1.load_vfile - filename = ", filename
        
        ncfile = front_end_NetCDF_helper()
        ExcludeList = ['lv_ISBL1', 'initial_time0_encoded', 'initial_time0_hours']
        
        # process parameters 129 to 157
        ncfile.open (filename)
        ncfile.exclude (ExcludeList)

        self.load_geoinfo (ncfile, filename)
        self.load_levels  (ncfile)
        self.load_data_tlayx (ncfile)

        ncfile.close()
        
    def create_catalog (self):
        CatFilename = "ecmwf_yotc_oper_an_pl_129_157_ncar_catalog.txt"
        ModelName   = "ECMWF"
        ProdName    = "YOTC Operational Analysis Pressure Level, Parameters 129 to 157 (NCAR)"
        self.int_create_catalog (CatFilename, ModelName, ProdName)

    def load_geoinfo (self, ncfile, filename):
        # create time array
        NameStrt = filename.rfind("/")
        print "NameStrt:", NameStrt, filename[NameStrt:]
        DateStrt = filename.rindex("yt_oper_an_pl_", NameStrt) + 14

        #print "date start - ", DateStrt
            
        FileDate = filename[DateStrt:DateStrt+8]
        print '**** date - ', FileDate
        
        FileYr = int(FileDate[0:4])
        FileMo = int(FileDate[4:6])
        FileDa = int(FileDate[6:8])

        CdfTimeData = N.zeros (4)
        CdfTimeData[0] = calendar.timegm((FileYr, FileMo, FileDa,  0, 0, 0))
        CdfTimeData[1] = calendar.timegm((FileYr, FileMo, FileDa,  6, 0, 0))
        CdfTimeData[2] = calendar.timegm((FileYr, FileMo, FileDa, 12, 0, 0))
        CdfTimeData[3] = calendar.timegm((FileYr, FileMo, FileDa, 18, 0, 0))

        print "time = ", CdfTimeData

        # get the grid type
        GridStrt = filename.rfind("_")
        if (filename[GridStrt:] == "_799.nc"):
            GridType = 0
        else:
            GridType = 1

        print "Grid Type: ", GridType, ", ", filename[GridStrt:]

        geofile = front_end_NetCDF_helper()
        
        # open geoinfo file
        georootdir = self.datarootdir
        geosuffix = ["_799.nc", "_1279.nc"] [GridType]
        geofilename = georootdir + "/yt_oper_an_pl_geoinfo" + geosuffix
        
        geofile.open (geofilename)

        # read lat array
        CdfLatData = geofile.read_data ('g4_lat_2')

        # read lon array
        CdfLonData = geofile.read_data ('g4_lon_3')

        geofile.close ()

        self.set_src_uniform_grid_info (CdfTimeData, CdfLatData, CdfLonData)
    # end load_geoinfo

    def load_levels (self, ncfile):
        # levels
        LvlName = 'lv_ISBL1'
        print "processing level:", LvlName
        
        # get attributes
        MidAttr = ncfile.read_attrs (LvlName)
            
        # add dimension name attribute for level data
        MidAttr['dimension1'] = 'isobaric_level'

        # level data is already 1D
        CdfData  = ncfile.read_data (LvlName)

        self.attach_level (LvlName, MidAttr, CdfData)
    # end load levels

    def load_data_tlayx(self, ncfile):
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

                # reformat for middle end (time, lvl, a, lat, lon) -> (dpt, lvl, a)
                MidData = self.cvt_tlayx_dla (CdfVarName, CdfData)

                # insert into dictionary
                self.attach_data (CdfVarName, MidAttr, MidData)
            # if included var
        # for all vars
    # end load_data_tlyx
# end front_end_ecmwf_yotc_oper_an_pl_ncar_1
