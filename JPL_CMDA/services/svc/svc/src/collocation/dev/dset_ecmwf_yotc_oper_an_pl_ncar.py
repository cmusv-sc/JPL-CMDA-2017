#
# dataset container for ECMWF YOTC Operational Analysis Pressure Level Data
#    from NCAR source
#

#
# file suffix, dimensions for variables
#
# "000_018_060128_203128_400.nc"  time(4) lvl(25) lat(800)  lon(1600)  tlyx
# "000_018_060128_203128_640.nc"  time(4) lvl(25) lat(1280) lon(2560)  tlyx
#
# "000_018_129128_157128_799.nc"  time(4) lvl(25) real(2) lat(800)  lon(800)  tlayx
# "000_018_129128_157128_1279.nc" time(4) lvl(25) real(2) lat(1280) lon(1280) tlayx
#
# dimensional variables
# level: lv_ISBL1
# lon: g4_lon_3
# lat: g4_lat_2
# time: initial_time0_encoded (yyyymmddhh.hh_frac)
# time: initial_time0_hours   (hours since 1800-01-01 00:00)
#



import datetime
from dset_abstract import dset_abstract
from front_end_ecmwf_yotc_oper_an_pl_ncar_0 import front_end_ecmwf_yotc_oper_an_pl_ncar_0
from front_end_ecmwf_yotc_oper_an_pl_ncar_1 import front_end_ecmwf_yotc_oper_an_pl_ncar_1

class dset_ecmwf_yotc_oper_an_pl_ncar (dset_abstract):
    def filename_filter (self, filename):
        Suffix = ["000_018_060128_203128_400.nc", \
                  "000_018_060128_203128_640.nc", \
                  "000_018_129128_157128_799.nc", \
                  "000_018_129128_157128_1279.nc"] [self.dset_mode]
        bFilt = (filename.find ("yt_oper_an_pl_") >= 0) and (filename.find (Suffix) >= 0)
        #print "dset_ecmwf_yotc_oper_an_pl_ncar.filename_filter - filename ", filename, ", suffix", Suffix, bFilt
        return bFilt

    def get_start_time (self, filename):        
        y   = filename[14:18]
        mon = filename[18:20]
        day = filename[20:22]
        h   = 0
        m   = 0
        s   = 0
        #print 'dset_ecmwf_yotc_oper_an_pl_ncar.get_start_time ', filename, y, mon, day, h
        start_time = datetime.datetime(int(y),int(mon),int(day), int(h), m, s) - \
                     datetime.timedelta(hours=3)
        return start_time

    def get_end_time (self, filename):
        end_time = self.get_start_time (filename) + datetime.timedelta(hours=24)
        #print "dset_ecmwf_yotc_oper_an_pl_ncar.get_end_time - end_time = ", end_time
        return end_time

    def get_front_end (self, filename):
        FE =  [front_end_ecmwf_yotc_oper_an_pl_ncar_0 (), \
               front_end_ecmwf_yotc_oper_an_pl_ncar_0 (), \
               front_end_ecmwf_yotc_oper_an_pl_ncar_1 (), \
               front_end_ecmwf_yotc_oper_an_pl_ncar_1 ()] [self.dset_mode]
        if (self.datarootdir == None):
            self.datarootdir = "/data3/ecmwf/yotc_oper_an_pl"
            
        FE.set_datarootdir (self.datarootdir)
        FE.load_vfile (filename)
        return FE

    def is_uniform_grid (self):
        return True
    # end is_uniform_grid
# end class
    
