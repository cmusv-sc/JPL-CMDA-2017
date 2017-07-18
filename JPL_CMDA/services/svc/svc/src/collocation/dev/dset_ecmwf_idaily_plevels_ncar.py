#
# dataset container for ECMWF ERA Pressure Level Data from NCAR Source
#

#
# file names, dimensions for variables
#
# "ei.oper.an.pl.regn128sc.yyyymmddhh.nc"  lvl(37) lat(256)  lon(512)  lyx
# "ei.oper.an.pl.regn128uv.yyyymmddhh.nc"  lvl(37) lat(256)  lon(512)  lyx
#
# dimensional variables
#
# level: lv_ISBL0
# lon: g4_lon_2
# lat: g4_lat_1
#

from dset_abstract import *
import datetime
from front_end_ecmwf_idaily_plevels_ncar import front_end_ecmwf_idaily_plevels_ncar

class dset_ecmwf_idaily_plevels_ncar (dset_abstract):
    def filename_filter (self, filename):
        bFilt = (filename.find ("ei.oper.an.pl.regn128sc") >= 0) and \
                (filename.find (".nc") >= 0)            
        return bFilt
    # end filename_filter

    def get_start_time (self, filename):
        y   = filename[24:28]
        mon = filename[28:30]
        day = filename[30:32]
        h   = filename[32:34]
        m   = 0
        s   = 0
        #print 'get_start_time - plevels -', filename, y, mon, day, h
        start_time = datetime.datetime(int(y),int(mon),int(day), int(h), m, s) - \
                     datetime.timedelta(hours=3)
        return start_time
    # end get_start_time

    def get_end_time (self, filename):
        end_time = self.get_start_time (filename) + datetime.timedelta(hours=6)
        return end_time
    # end get_end_time

    def get_front_end (self, filename):
        FE =  front_end_ecmwf_idaily_plevels_ncar ()
        FE.load_vfile (filename)
        return FE
    # end get_front_end

    def is_uniform_grid (self):
        return True
    # end is_uniform_grid
# end class dset_ecmwf_idaily_plevels_ncar

