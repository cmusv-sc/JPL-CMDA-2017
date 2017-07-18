#
# program to build geoinfo (lat/long) files for nc files lacking
# coordinate information
#
# files and directories are hard coded
#
import numpy as N
from Scientific.IO.NetCDF import NetCDFFile

from front_end_util import *

def load_geoinfo (SrcFilename, DstFilename, GridSize, LatName, LonName):
    # get lat/long values from 400/640 level files
    ncfile = front_end_NetCDF_helper()

    ncfile.open (SrcFilename)

    # read lat array
    SrcLatData = ncfile.read_data (LatName)
    #print SrcLatData

    # read lon array
    SrcLonData = ncfile.read_data (LonName)
    #print SrcLonData

    ncfile.close ()

    # create down-sampled long array    
    DstLonData = N.zeros (GridSize)

    # 
    for DstLonNo in range(0, GridSize):
        SrcLonNo = DstLonNo * 2

        # down-sampling strategy 1, use avarage
        #DstLonData[DstLonNo] = (SrcLonData[SrcLonNo] + SrcLonData[SrcLonNo+1])/2.0
        #print DstLonNo, SrcLonNo, DstLonData[DstLonNo], SrcLonData[SrcLonNo], SrcLonData[SrcLonNo+1]

        # start with 0 and skip alternate points
        DstLonData[DstLonNo] = SrcLonData[SrcLonNo]
        #print DstLonNo, SrcLonNo, DstLonData[DstLonNo], SrcLonData[SrcLonNo]

    # write NetCDF file
    # open output file
    dst_ncfile = NetCDFFile (DstFilename, 'w')

    # define dimensions
    dst_lat_dim = dst_ncfile.createDimension (LatName, GridSize)
    dst_lon_dim = dst_ncfile.createDimension (LonName, GridSize)

    # define variables
    dst_lat_var = dst_ncfile.createVariable (LatName, 'd', (LatName,))
    #dst_lat_var.setattr (
    # NetCDFFile.setattr (dst_lat_var, 'attrname', attr_val)
    
    dst_lon_var = dst_ncfile.createVariable (LonName, 'd', (LonName,))

    # write lat data
    dst_lat_var.assignValue(SrcLatData)

    # write lon data
    dst_lon_var.assignValue(DstLonData)

    # close output file
    dst_ncfile.close ()


########################################################################################
# generate yt_oper_an_pl_geoinfo_799.nc file
basedir = "/data3/ecmwf/yotc_oper_an_pl"
SrcFilename = basedir + "/2008/05/yt_oper_an_pl_2008050100_000_018_060128_203128_400.nc"
DstFilename = basedir + "/yt_oper_an_pl_geoinfo_799.nc"
load_geoinfo (SrcFilename, DstFilename, 800, 'g4_lat_2', 'g4_lon_3')

# generate yt_oper_an_pl_geoinfo_1289.nc file
SrcFilename = basedir + "/2010/02/yt_oper_an_pl_2010020100_000_018_060128_203128_640.nc"
DstFilename = basedir + "/yt_oper_an_pl_geoinfo_1279.nc"
load_geoinfo (SrcFilename, DstFilename, 1280, 'g4_lat_2', 'g4_lon_3')

# generate yt_oper_an_ml_geoinfo_799.nc file
basedir = "/data3/ecmwf/yotc_oper_an_ml"
SrcFilename = basedir + "/2008/05/yt_oper_an_ml_2008050100_000_000_133128_248128_400.nc"
DstFilename = basedir + "/yt_oper_an_ml_geoinfo_799.nc"
load_geoinfo (SrcFilename, DstFilename, 800, 'g4_lat_3', 'g4_lon_4')

# generate yt_oper_an_ml_geoinfo_1289.nc file
SrcFilename = basedir + "/2010/02/yt_oper_an_ml_2010020100_000_000_133128_248128_640.nc"
DstFilename = basedir + "/yt_oper_an_ml_geoinfo_1279.nc"
load_geoinfo (SrcFilename, DstFilename, 1280, 'g4_lat_3', 'g4_lon_4')
