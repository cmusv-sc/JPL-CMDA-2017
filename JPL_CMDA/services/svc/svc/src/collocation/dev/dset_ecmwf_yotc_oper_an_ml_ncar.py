#
# dataset container for ECMWF YOTC Operational Analysis Model Data
#    from NCAR source
#

from dset_abstract import *
import datetime
from front_end_ecmwf_yotc_oper_an_ml_ncar_0 import front_end_ecmwf_yotc_oper_an_ml_ncar_0
from front_end_ecmwf_yotc_oper_an_ml_ncar_1 import front_end_ecmwf_yotc_oper_an_ml_ncar_1

#
# file suffix, dimensions for variables
#
# "yt_oper_an_ml_yyyymmdd00_0hh_0hh_133128_248128_400.nc"  lvl(91/92) lat(800)   lon(1600)  lyx -> dl
# "yt_oper_an_ml_yyyymmdd00_0hh_0hh_133128_248128_640.nc"  lvl(91/92) lat(1280)  lon(2560)  lyx -> dl
#
# "yt_oper_an_ml_yyyymmdd00_000_018_129128_152128_799.nc"  time(4) real(2) lat(800)  lon(800)  tayx -> da
# "yt_oper_an_ml_yyyymmdd00_000_018_129128_152128_1279.nc" time(4) real(2) lat(1280) lon(1280) tayx -> da
#
#* "yt_oper_an_ml_yyyymmdd00_000_018_130128_132128_799.nc"  time(4) lvl(91) real(2) lat(800)  lon(800)  tlayx -> da
#
#
# dimensional variables
#   parameter 133 to 248
#     level: lv_ISBL0
#     lon: g4_lon_2
#     lat: g4_lat_1
#
#     P0:reference pressure (scaler)
#
#     CC_GDS4_HYBL (128): Cloud Cover
#     CIWC_GDS4_HYBL (248): Cloud ice water content
#     CLWC_GDS4_HYBL (203): Cloud liquid water content
#     O3_GDS4_HYBL (203): Ozone mass mixing ratio
#     Q_GDS4_HYBL (133): Specific humidity
#
#
#   parameter 129 to 152
#     time: initial_time0_encoded (yyyymmddhh.hh_frac)
#     time: initial_time0_hours   (hours since 1800-01-01 00:00)
#     real/img: complex vector
#     g50_lat_2: latitude (missing variable)
#     g50_lon_3: longitude (missing variable)
#
#     LNSP_GDS50_HYBL (152): Log of surface pressure
#     Z_GDS50_HYBL (129) : Geopotential
#
#   parameter 130 to 132
#
#
#
# time: initial_time0_encoded (yyyymmddhh.hh_frac)
# time: initial_time0_hours   (hours since 1800-01-01 00:00)
#


class dset_ecmwf_yotc_oper_an_ml_ncar (dset_abstract):
    def filename_filter (self, filename):
        Suffix = ['133128_248128_400.nc', \
                  '133128_248128_640.nc', \
                  '129128_152128_799.nc', \
                  '129128_152128_1279.nc'] [self.dset_mode]
                  
        bFilt = (filename.find ("yt_oper_an_ml") >= 0) and \
                (filename.find (Suffix) >= 0)
        
        return bFilt

    def get_start_time (self, filename):
        # split into 6 hr and 24 hour datasets
        if ((self.dset_mode == 0) or (self.dset_mode == 1)):
            y   = filename[14:18]
            mon = filename[18:20]
            day = filename[20:22]
            h   = filename[26:28]
            m   = 0
            s   = 0
        else:
            y   = filename[14:18]
            mon = filename[18:20]
            day = filename[20:22]
            h   = 0
            m   = 0
            s   = 0
            
        #print 'dset_ecmwf_yotc_oper_an_ml_ncar.get_start_time ', filename, y, mon, day, h
        start_time = datetime.datetime(int(y),int(mon),int(day), int(h), m, s) - \
                     datetime.timedelta(hours=3)
            
        return start_time

    def get_end_time (self, filename):
        DeltaHr = [6, 6, 24, 24] [self.dset_mode]
        
        end_time = self.get_start_time (filename) + datetime.timedelta(hours=DeltaHr)
        #print "dset_ecmwf_yotc_oper_an_ml_ncar.get_end_time - end_time = ", end_time
        return end_time

    def get_front_end (self, filename):
        FE = [front_end_ecmwf_yotc_oper_an_ml_ncar_0(),
              front_end_ecmwf_yotc_oper_an_ml_ncar_0(),
              front_end_ecmwf_yotc_oper_an_ml_ncar_1(),
              front_end_ecmwf_yotc_oper_an_ml_ncar_1()] [self.dset_mode]
        print "datarootdir: ", self.datarootdir
        FE.set_datarootdir (self.datarootdir)
        FE.load_vfile (filename)
        
        return FE

    def is_uniform_grid (self):
        return True
    # end is_uniform_grid
# end class
    
