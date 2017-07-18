#
# abstract class for front ends processing uniformly gridded datasets
# using NetCDF formatted files as input
#
# when constructed, this class will load one or more related files
# into a single object for the middle end
#
# the variables, attributes and data are used by the middle-end and back-end
# to generate teh collocation files
#
# objects are output as an unstructured grid indexed by a datapoint number
# associated with a time value, latitude value, and a longitude value
# time values must be equal to or greater than the previous value
#

import numpy as N
import datetime

class front_end_abstract_uniform ():
    def __init__ (self):
        #print "entering front_end_abstract_uniform.__init__"
        
        self.TimeSize = 0
        self.LatSize  = 0
        self.LonSize  = 0

        self.GridSize = 0
        
        self.Time = None
        self.Lat  = None
        self.Lon  = None

        self.datarootdir = None

        self.Data   = {} # dictionary of variables and associated values
        self.Levels = {} # dictionary of dimensions and associated values
    # end __init__

    ############################################################
    #
    # exported mid_end and back_end interface methods
    #
    # load data from 1 or more related data files
    # called from dset.get_front_end
    def load_vfile (self, filename):
        print "front end must implement dataset specific load_vfile"
        pass
    
    # create catalog
    def create_catalog (self):
        print "front end must implement dataset specific create catalog"
        pass

    # set data root directory
    def set_datarootdir (self, datarootdir):
        print "front_end_abstract.set_datarootdir: ", datarootdir
        self.datarootdir = datarootdir

    def get_src_uniform_grid_info (self):
        # returns three element array with dimension sizes for (time, lat, lon)
        return (self.TimeSize, self.LatSize, self.LonSize)
    # end get_uniform_grid_info

    # time is a numeric array of unix datetime values indexed by datapoint no
    #      (flattened time, lon, lat)
    def get_time (self):
        print "front_end_abstract_uniform.get_time = ", min(self.Time), max(self.Time)
        return self.Time

    # latitude is numeric array of latitude values associate with each datapoint
    def get_latitude (self):
        print "front_end_abstract_uniform.get_latitude = ", min(self.Lat), max(self.Lat)
        return self.Lat

    # longitude is numeric array of longitude values associate with each datapoint
    def get_longitude (self):
        print "front_end_abstract_uniform.get_longitude = ", min(self.Lon), max(self.Lon)
        return self.Lon

    # this returns a dictionary of variables for the vfile
    #
    def get_data (self):
        #print "front_end_abstract_uniform.get_data"
        return self.Data

    #  this returns a dictionary of level names and
    #  its associated numeric array of level values
    def get_levels (self):
        #print "front_end_abstract_uniform.get_levels"
        return self.Levels
    # end get_levels

    #######################################################
    #
    # uniform grid helper methods
    #
    def int_create_catalog (self, cat_filename, ModelName, ProdName):
        variableNames = self.Data.keys()
        
        file = open(cat_filename, 'w')
        line = 'Sensor/Model\tData Product\tVariable Name\tVariable Unit\n'
        file.write(line)
        for i in variableNames:
            attribute = self.Data[i][0]
            #print attribute
            line = '%s\t%s\t%s\t%s\n' %(ModelName, ProdName, attribute['long_name'], attribute['units'])
            file.write(line)

        file.close()
    # end create catalog

    ########
    #
    # convert rectilinear (time, lat, lon) dimensions to array for middle end
    # update variables used by middle end
    #
    # middle end uses a "flattened" one dimensional array
    #
    # TimeData is 1D array of unix datetime values in ascending order
    # LatData  is 1D array of float values between -90 and 90 exclusive of polar singularities
    # LonData  is 1D array of float values between -180 and 180
    #
    def set_src_uniform_grid_info (self, TimeData, LatData, LonData):
        self.TimeSize = N.size(TimeData)
        self.LatSize  = N.size(LatData)
        self.LonSize  = N.size(LonData)

        self.GridSize = self.TimeSize * self.LatSize * self.LonSize
        
        midTime = N.zeros(self.GridSize)
        midLat  = N.zeros(self.GridSize)
        midLon  = N.zeros(self.GridSize)

        # fill in the lat long values for each grid point (lon varies fastest, then lat, then time)
        GridPt = 0
        for i in range(0, self.TimeSize):
            TimeTk = TimeData[i]
            for j in range(0, self.LatSize):
                LatTk = LatData[j]
                for k in range(0, self.LonSize):
                    LonTk = LonData[k]

                    if LonTk > 180.0:
                        LonTk = LonTk - 360.0

                    midTime[GridPt] = TimeTk
                    midLat [GridPt] = LatTk
                    midLon [GridPt] = LonTk
                    GridPt += 1
                # end for k
            # end for j
        # end for i
                    
        self.Time = midTime
        self.Lat  = midLat
        self.Lon  = midLon
    # end set_uniform_grid_info

    # attach completed variable to mid_end data object
    def attach_data (self, name, attr, data):
        self.Data[name] = (attr, data)
    
    # attach a named level and its associated mapping from level number
    # to a value for a particular level
    # the level value is a numeric array which is indexed by level no
    def attach_level (self, Name, Attr, Data):
        self.Levels[Name] = (Attr, Data)
    # end attach_level

    ###############################################################
    #
    # convert data arrays to middle end format
    #
    
    # convert single time step (lvl, lat, lon) array to (dpt, lvl) array
    def cvt_lyx_dl (self, InName, InData):
        InShape = InData.shape
        if (len(InShape) != 3):
            print "Error in front_end_abstract_uniform.cvt_lyx_dl - variable not 3D ", InName

        # reformat for middle end from 3D (lev, lat, lon) to 2D (grid, lev)
        InData = N.swapaxes(InData, 0, 1) # lyx -> ylx
        InData = N.swapaxes(InData, 1, 2) # ylx -> yxl
        dshape = InData.shape  
        MidData = N.reshape(InData, (dshape[0]*dshape[1], dshape[2])) # yxl -> dl
        
        return MidData
    # end cvt_lyx_dl

    # convert (time, lvl, lat, lon) array to (dpt, lvl) array
    def cvt_tlyx_dl (self, InName, InData):
        InShape = InData.shape

        if (len(InShape) != 4):
            print "Error in front_end_abstract_uniform.cvt_tlyx_dla - variable not 4D ", InName
            return None

        # reformat for middle end from 4D (time, lev, lat, lon) to 2D (grid, lev)
        InData = N.swapaxes(InData, 1, 2) # tlyx -> tylx
        InData = N.swapaxes(InData, 2, 3) # tylx -> tyxl
        dshape = InData.shape  
        MidData = N.reshape(InData, (dshape[0]*dshape[1]*dshape[2], dshape[3])) # tyxl -> dl

        return MidData
    # end cvt_tlyx_dla

    # convert (time, lvl, a, lat, lon) array to (dpt, lvl, a) array
    def cvt_tlayx_dla (self, InName, InData):
        InShape = InData.shape

        if (len(InShape) != 5):
            print "Error in front_end_abstract_uniform.cvt_tlaxy_dla - variable not 5D ", InName

        # reformat for middle end from 5D (time, lev, a, lat, lon) to 3D (grid, lev, a)
        InData = N.swapaxes(InData, 2, 3) # tlayx -> tlyax
        InData = N.swapaxes(InData, 3, 4) # tlyax -> tlyxa
        InData = N.swapaxes(InData, 1, 2) # tlyxa -> tylxa
        InData = N.swapaxes(InData, 2, 3) # tylxa -> tyxla
        
        dshape = InData.shape  
        MidData = N.reshape(InData, (dshape[0]*dshape[1]*dshape[2], dshape[3], dshape[4])) # tyxla -> dla

        return MidData
    # end cvt_tlayx_dla

    # convert (time, a, lat, lon) array to (dpt, a) array
    def cvt_tayx_da (self, InName, InData):
        InShape = InData.shape

        if (len(InShape) != 4):
            print "Error in front_end_abstract_uniform.cvt_taxy_da - variable not 4D ", InName

        # reformat for middle end from 5D (time, a, lat, lon) to 3D (grid, a)
        InData = N.swapaxes(InData, 1, 2) # tayx -> tyax
        InData = N.swapaxes(InData, 2, 3) # tyax -> tyxa
        
        dshape = InData.shape  
        MidData = N.reshape(InData, (dshape[0]*dshape[1]*dshape[2], dshape[3])) # tyxa -> da

        return MidData
    # end cvt_tayx_da
# end front_end_abstract_uniform class


# end of abstract front end

    
