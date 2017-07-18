#
# front end utility module
#
import numpy as N
from Scientific.IO.NetCDF import NetCDFFile
#from datetime import datetime
import util
import types

#####################################################
#
# netcdf interface methods
#
class front_end_NetCDF_helper ():
    def __init__ (self):
        #print "entering front_end_NetCDF_helper.__init__"
        self.ncfile = None
        self.VarNameList = {}
    # end __init__

    def open (self, filename):
        self.ncfile = NetCDFFile(filename,'r')

        # initialize variable name list
        self.VarNameList =  {}
        for VarName in self.ncfile.variables.keys():
            self.VarNameList[VarName] = True
    # end open

    def close (self):
        self.ncfile.close()
        self.ncfile = None
    # end close

    def exclude (self, VarList):
        for VarName in VarList:
            self.VarNameList[VarName] = False
    # end exclude

    def get_varlist (self):
        return self.VarNameList
    # end get_varlist

    def read_data (self, VarName):
        CdfVar = self.ncfile.variables[VarName]  
        return N.array(CdfVar.getValue())
    # end read_data

    def read_attrs (self, VarName):
        CdfVar = self.ncfile.variables[VarName]
        
        MidAttr = {}
            
        AttrNameList = dir(CdfVar)
        for AttrName in AttrNameList:
            # remove extra attrs
            if ((AttrName != 'assignValue')
                and (AttrName != 'getValue')
                and (AttrName != 'typecode')):
                        
                #print 'attr name ', AttrName
                CdfAttr = getattr(CdfVar, AttrName)
                AttrType = type(CdfAttr)

                #print 'attribute - ', CdfVarName, ':', AttrName, ', type ', AttrType

                # type is string or array
                if (AttrType == types.StringType):
                    MidAttr[AttrName] = CdfAttr
                else:
                    #print 'array', CdfVarName, ':', AttrName, ', type '#, AttrName.typecode
                    MidAttr[AttrName] = N.array(CdfAttr)
                # end if array
            # end if not filtered attribute
        # end for all attributes
        
        return MidAttr
    # end read attr
# end of front_end_NetCDF_helper

#
# this will check all required front end interfaces
#
def validate_front_end (dset, rootdir, filename):

    # get start and end times
    short_start = filename.rfind ('/')+1
    short_name = filename[short_start:]
    #print short_start, short_name

    start_time_d = dset.get_start_time (short_name)
    end_time_d   = dset.get_end_time   (short_name)

    start_time_u = util.datetime_to_unix_time (start_time_d)
    end_time_u   = util.datetime_to_unix_time (end_time_d)

    # set root directory
    dset.set_datarootdir (rootdir)
    
    # get front end for dataset
    cs = dset.get_front_end (filename)

    # try all required interfaces
    cs.create_catalog()
    print "catalog created"

    grid_info = cs.get_src_uniform_grid_info()
    grid_size = grid_info[0] * grid_info[1] * grid_info[2]
    print "grid info = ", grid_info, grid_size
    last = grid_size-1

    # get temporal and spatial information
    time = cs.get_time()
    lat = cs.get_latitude()
    long = cs.get_longitude()

    # first dimension is always indexed spatial/temproral datapoint number
    DptCnt = time.shape[0]

    # validate time
    #print "time = ", time[0:9], time[last]

    prev_time = time[0]
    for TimeNo in range (0, DptCnt):
        cur_time = time[TimeNo]

        # check time between start and end times
        if (cur_time < start_time_u) or (cur_time > end_time_u):
            print "error in validate_front_end - current time out of range"
            print "indx: ", TimeNo, ", Val: ", cur_time
            print "start time: ", start_time_u, ", end time: ", end_time_u
        
        # check time same or incrasing
        if cur_time < prev_time:
            print "error in validate_front_end - current time decreasing"
            print "indx: ", TimeNo, ", cur time: ", cur_time, ", prev time:", prev_time

    # validate latitude
    #print "latitude = ", lat[0:9], lat[last]

    # first dimension must be same size as count of spatial/temporal datapoints
    if lat.shape[0] != DptCnt:
        print "error in dim 0 of latitude - size of dimension does not match spatial/temproral dim size"
        print "Lat size:", Lat.shape[0], ", Dpt size:", DptCnt

    for LatNo in range(0, DptCnt):
        if (lat[LatNo] <= -90.0) or (lat[LatNo] >= 90.0):
            print "**** Error in get_latitude - lat value out of range"
            print "indx: ", LatNo, ", val:", lat[LatNo]

    # validate longitude
    #print "longitude = ", long[0:9], long[last]

    # first dimension must be same size as count of spatial/temporal datapoints
    LonCnt = long.shape[0]
    if LonCnt != DptCnt:
        print "error in dim 0 of longitude - size of dimension does not match spatial/temproral dim size"
        print "Lon size:", LonCnt, ", Dpt size:", DptCnt

    for LongNo in range(0, DptCnt):
        if (long[LongNo] < -180.0) or (long[LongNo] > 180.0):
            print "**** Error in get_longitude - long value out of range"
            print "indx: ", LongNo, ", val:", long[LongNo]

    levels = cs.get_levels()
    for vname in levels.keys():
        print "level ", vname
    
        var = levels[vname]
        attr = var[0]
        data = var[1]

        for attrName in attr.keys():
            attrVal = attr[attrName]
            print '        attr[', attrName, '] =  ', str(attrVal) 
    
        print "data = ", data


    dataset = cs.get_data()
    #print dataset.keys()

    for vname in dataset.keys():
        var = dataset[vname]
        attr = var[0]
        data = var[1]
    
        print 'var ', vname, data.shape

        # first dimension must be same size as count of spatial/temporal datapoints
        if data.shape[0] != DptCnt:
            print "error in dim 0 of " + vname + \
                  " - size of dimension does not match spatial/temproral dim size"
            print "Dim 0 size:", data.shape[0], ", Dpt size:", DptCnt

        # test for level data (has dimension1 attribute)
        # if so, must match level shape

        # display attributes
        for attrName in attr.keys():
            attrVal = attr[attrName]
            print '        attr[', attrName, '] =  ', str(attrVal)
            # check for required attributes

        """
        # display summary according to shape
        rank = len(data.shape)
        if rank == 1:
            print "data = ", data[0:9], data[last]
        elif rank == 2:
            print "data = ", data[0:9,0], data[last,0]
        elif rank == 3:
            print "data = ", data[0:9,0,0], data[last,0,0]
        else:
            print "rank: ", rank
        """

        print "min:", N.min(data), "max:", N.max(data)
    # end for all vars
# end validate_front_end

# end of front end utility package

    
