# unnamed dataset container
#
# this container provides compatibility between the "old" technique of
#  using directory names and long lists of conditional logic
#  and the "new" technique of having a container class for each dataset
#
# changed filename filtering to return a string to be inserted in the filelist
#   instead of a boolean
#
import util
from dset_abstract import *

class dset_nemo(dset_abstract):    
    def filename_filter (self, filename):
        bFilt = util.filename_filter (self.dset_name, filename)
        ###print "dset_nemo.filename_filter - filter = ", bFilt, ", filename: ", filename
        return bFilt
    # end filename_filter

    def dir_filter (self, dirname):
        return util.dir_filter (self.dset_name, dirname)
    # end dir_filter

    def get_start_time (self, filename):
        return util.get_start_time (self.dset_name, filename)
    # end get_start_time

    def get_end_time (self, filename):
        return util.get_end_time (self.dset_name, filename)
    # end get_end_time

    def get_front_end (self, filename):
        print "dset_nemo.get_front_end - dset name = ", self.dset_name
	return util.get_front_end (self.dset_name, filename)
    # end get_front_end

    def is_uniform_grid (self):
        src_data = self.dset_name
        # this code used to be in sdriver.py
	ret_code =  src_data == 'ecmwf-idaily-plevels' or \
                    src_data == 'ecmwf-idaily-surface' or \
                    src_data == 'ecmwf-yotc-aos-0.25deg' or \
                    src_data == 'ecmwf-yotc-aos-1.5deg'  or \
                    src_data == 'ecmwf-yotc-oaml-0.25deg' or \
                    src_data == 'ecmwf-yotc-oapl-0.25deg' or \
                    src_data == 'ecmwf_era_interim_analysis_surface' or \
                    src_data == 'ecmwf_era_interim_analysis_level'
        
        print 'dset_nemo.is_uniform_grid: ', self.dset_name, ret_code
        return ret_code
    # end is_uniform_grid

    # map dset_name to util rootbasedir name
    # the current (old) system uses the directory name to select a dataset name
    # with the introduction of a dataset name in the config file (xml), the dataset name
    # can be explicitly defined.  However, many of the the utilities use the pre-defined directory name
    # to select a dataset specific action.
    # This method converts a dataset name back to it's predefined "directory" name so the compare works
    # in the utilities
    #def unmap_name (self):
# end of abstract dataset container

    
