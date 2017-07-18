# dataset container base class
#
# override filename_filter, get_start_time, get_end_time, and get front_end
#   when implementing a new dataset container class
#

import datetime
import front_end_abstract

class dset_abstract():
    def __init__ (self):
        self.dset_name = 'derived class name not set - check registry'
        self.dset_mode = 0
        self.datarootdir = None

    def get_name (self):
        return self.dset_name

    def set_name (self, dset_name):
        self.dset_name = dset_name

    def get_mode (self):
        return self.dset_mode

    def set_mode (self, dset_mode):
        self.dset_mode = dset_mode

    def set_datarootdir (self, datarootdir):
        print "dset_abstract.setdatarootdir:", datarootdir
        self.datarootdir = datarootdir

    # old interface used combination of dataroot directory and dataset name for access
    # so, the root dir needs to be memorized until "old" interfaces are cleaned up
    #def set_dataroot_dir (self, datarootdir):
    #    print dset_abstract.set_dataroot_dir
    #    self.datarootdir = datarootdir

    def filename_filter (self, filename):
        # true, if filename is to be included in filelist
        # default is to include nothing unless overridden
        print "error in dset_abstract.filename_filter - abstract interface not implemented"
        return False

    def dir_filter (self, dirname):
        #true, if directory is to be searched for files
        # default is to include everything unless overridden
        return True

    def get_start_time (self, filename):
        print "error in dset_abstract.get_start_time - abstract interface not implemented"
        return datetime.datetime(2010, 1, 1)

    def get_end_time (self, filename):
        print "error in dset_abstract.get_start_time - abstract interface not implemented"
        return datetime.datetime(2010, 1, 2)

    # load data from file into front end object (change to attach_file?)
    def get_front_end (self, filename):
        print "error in dset_abstract.get_front_end - abstract interface not implemented"
        return front_end_abstract (filename)

    def is_uniform_grid (self):
        # default is false unless overridden
        return False

# end of dataset container base class

    
