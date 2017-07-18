#
# abstract front end
# every front end must implement the methods contained in this class
#
# when constructed, this class will load one or more files related
# to a virtual dataset into this object
#
# the variables, attributes and data are used by the middle-end and back-end
# to generate teh collocation files
#
# most objects are output as an unstructured grid indexed by a datapoint number
# associate with a datapoint is a time value, latitude value, and a longitude value
# time values must be equal to or greater than the previous value
#
#
#

import datetime

class front_end_abstract():
    # required interfaces
    def __init__ (self, filename):
        # create front-end object containing data associated with filename
        pass

    # create catalog
    def create_catalog (self):
        pass

    # arrays are accessed by a datapoint index
    def get_time (self):
        # maps datapoint no to datetime value
        # returns long int array indexed by datapoint no
        pass

    def get_latitude (self):
        # maps datapoint no to latitude value
        # returns float array indexed by datapoint no
        pass

    def get_longitude (self):
        # maps datapoint no to longitude value
        # return float array indexed by datpoint no
        pass

    def get_data (self):
        # returns a dictionary of variables associated with the file
        #
        pass
    
    # get_levels
    def get_levels (self):
        # maps level index to float value
        # returns float array of level values, indexed by level index
        # returns {}, if dataset has no levels
        pass
    
    #
    # if dataset is based on rectilinear gridded datasets (time, lat, lon),
    #  the following methods must be supported:
    #
     
    def get_uniform_grid_info (self):
        # returns three element array with dimension sizes (time, lat, lon)
        pass





# end of abstract dataset container

    
