#
# dataset container for ECMWF ERA Interim Surface Data from NCAR source
#

from dset_abstract import *
import datetime
import front_end_ecmwf_idaily_surface_ncar

class dset_ecmwf_idaily_surface_ncar (dset_abstract):
    def set_dataroot_dir (self, datarootdir):
        self.dtarootdir = datarootdir

    def filename_filter (self, filename):
        return (filename.find ("ei.oper.an.sfc.regn128sc") >= 0) and \
               (filename.find (".nc") >= 0)

    def get_start_time (self, filename):
        y   = filename[25:29]
        mon = filename[29:31]
        day = filename[31:33]
        h   = filename[33:35]
        m   = 0
        s   = 0
        #print 'dset_ecmwf_idaily_surface_ncar.get_start_time ', filename, y, mon, day, h
        start_time = datetime.datetime(int(y),int(mon),int(day), int(h), m, s) - datetime.timedelta(hours=3)
        return start_time

    def get_end_time (self, filename):
        end_time = self.get_start_time (filename) + datetime.timedelta(hours=6)
        #print "dset_ecmwf_idaily_surface_ncar.get_end_time - end_time = ", end_time
        return end_time

    def get_front_end (self, filename):
        return front_end_ecmwf_idaily_surface_ncar.front_end_ecmwf_idaily_surface_ncar (filename)

    def is_uniform_grid (self):
        return True
    # end is_uniform_grid
# end class
