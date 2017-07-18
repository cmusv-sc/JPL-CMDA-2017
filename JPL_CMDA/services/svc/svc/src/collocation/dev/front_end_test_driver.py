import dataset_registry
import sys
from front_end_util import validate_front_end


###################
# define candidate test source files
test_src  = {}
test_root = {}

def register (dset_name, rootdir, file_name):
    if dset_name in test_src.keys():
        print "error in front_end_test_driver - source file for front end already exists"
        print "front end: " + dset_name
        print "existing file: " + test_src[dset_name]
        print "current file: " + file_name
    else:
        test_src [dset_name] = rootdir + '/' + file_name
        test_root[dset_name] = rootdir
        
# end register

###################
# ecmwf daily surface
register ('ecmwf_idaily_surface_ncar', \
          '/data3/ecmwf/era_interim_analysis_surface', \
          '2008/ei.oper.an.sfc.regn128sc.2008050100.nc')

###################
# ecmwf daily pressure levels
register ('ecmwf_idaily_plevels_ncar', \
          '/data3/ecmwf/era_interim_analysis_level', \
          '2008/05/ei.oper.an.pl.regn128sc.2008050100.nc')

###################
# yotc operational analysis pressure levels, 5/1/2008 to 1/25/2010, parameters 060 to 203
register ('ecmwf_yotc_oper_an_pl_ncar_0', \
          '/data3/ecmwf/yotc_oper_an_pl', \
          '2008/05/yt_oper_an_pl_2008050100_000_018_060128_203128_400.nc')

# yotc operational analysis pressure levels, 1/27/2010 to 4/30/2010, parameters 060 to 203
register ('ecmwf_yotc_oper_an_pl_ncar_1', \
          '/data3/ecmwf/yotc_oper_an_pl', \
          '2010/02/yt_oper_an_pl_2010020100_000_018_060128_203128_640.nc')

# yotc operational analysis pressure levels, 5/1/2008 to 1/25/2010, parameters 129 to 157
register ('ecmwf_yotc_oper_an_pl_ncar_2',
          '/data3/ecmwf/yotc_oper_an_pl', \
          '2008/05/yt_oper_an_pl_2008050100_000_018_129128_157128_799.nc')

# yotc operational analysis pressure levels,  1/27/2010 to 4/30/2010, parameters 129 to 157
register ('ecmwf_yotc_oper_an_pl_ncar_3',
          '/data3/ecmwf/yotc_oper_an_pl', \
          '2010/02/yt_oper_an_pl_2010020100_000_018_129128_157128_1279.nc')

##################
# yotc operational analysis on model levels, 5/1/2008 to 1/25/2010, parameters 133 to 248
register ('ecmwf_yotc_oper_an_ml_ncar_0', \
          '/data3/ecmwf/yotc_oper_an_ml', \
          '2008/05/yt_oper_an_ml_2008050100_000_000_133128_248128_400.nc')

# yotc operational analysis on model levels, 1/27/2010 to 4/30/2010, parameters 133 to 248
register ('ecmwf_yotc_oper_an_ml_ncar_1', \
          '/data3/ecmwf/yotc_oper_an_ml', \
          '2010/02/yt_oper_an_ml_2010020100_006_006_133128_248128_640.nc')

# yotc operational analysis on model levels, 5/1/2008 to 1/25/2010, parameters 129 to 152
register ('ecmwf_yotc_oper_an_ml_ncar_2', \
          '/data3/ecmwf/yotc_oper_an_ml', \
          '2008/05/yt_oper_an_ml_2008050100_000_018_129128_152128_799.nc')

register ('ecmwf_yotc_oper_an_ml_ncar_3', \
          '/data3/ecmwf/yotc_oper_an_ml', \
          '2010/02/yt_oper_an_ml_2010020100_000_018_129128_152128_1279.nc')

######################################################################
#
# test program
#

if __name__ == '__main__':
    if len(sys.argv) <= 1:
	print '****** Usage: python ' + sys.argv[0] + ' dataset_name'
	sys.exit(2)

    dset_name = sys.argv[1]

    if dset_name not in test_src.keys():
        print '****** error in front_end_test_driver - unknown front end name: ' + dset_name
	sys.exit(2)

    filename = test_src[dset_name]
    print "testing front end " + dset_name + " using file " + filename
    
    dset = dataset_registry.get_dataset_container (dset_name)

    validate_front_end (dset, test_root[dset_name], filename)


