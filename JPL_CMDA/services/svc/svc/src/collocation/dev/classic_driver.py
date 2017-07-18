#
# This driver co-locates src data to the target grid
# Currently, target data set is CloudSat (that is, we
# are doing a CloudSat centric co-location)
# Source data sets include:
# AMSR, CERES, AIRS, CALIPSO, and MLS
#
import os
import sys
import datetime
import pickle
import bisect
import logging

import file_list as FL
import util as UT

import front_end_cloudsat as FEC

import middle_end as MD
import back_end as BD

# Enable remote profiling via 'Heapy'.  Start the remote session
# first using % python -c "from guppy import hpy;hpy().monitor()"
# Then start this program and see the monitor section of:
#    http://guppy-pe.sourceforge.net/heapy_Use.html
# See also hp.heapu()
import guppy.heapy.RM
### from guppy import hpy;hp=hpy()
import time             # to use time.sleep(60) as a profiling aid (to pause)

if len(sys.argv) <= 2 or sys.argv[1] == '-h' or sys.argv[1] == '-help' or sys.argv[1] == '--help':
    print '****** Usage: python ' + sys.argv[0] + ' path_to_src_data_config_xml_file' + ' path_to_target_data_config_xml_file'
    sys.exit(2)
else:
    config_file = sys.argv[1]
    tgt_config_file = sys.argv[2]

# for CloudSat centric co-location
target_data = 'cloudsat'

# read configure info. from config_file
try:
    afl = FL.file_list(config_file) # afl is used for src data
except IOError:
    print '****** src data config file does not exist.'
    sys.exit(-1)

# read configure info. from tgt_config_file
try:
    afl1 = FL.file_list(tgt_config_file) # afl1 is used for target data
except IOError:
    print '****** target data config file does not exist.'
    sys.exit(-1)

# start the timer
start = datetime.datetime.now()

# re-order time if given wrong
if(afl.end_t < afl.start_t):
    tt = afl.start_t
    afl.start_t = afl.end_t
    afl.end_t = tt
    print '****** Warning: end time is earlier than start time in config file. Order reversed.'

print 'User specified start time:', afl.start_t, 'end time:', afl.end_t

# load the file list for target data (e.g., CloudSat)
list_file = afl.listdir + '/' + target_data + '_granules.list.pkl'
print 'list_file: ', list_file

try:
    afl1.load_lists(list_file)
except IOError:
    print '****** list file for target data does not exist.'
    sys.exit(-1)

# print afl1.dirNameList
# print afl1.granuleNumList

print 'afl.start_t: ', afl.start_t
### print 'afl1.endTimeList: ', afl1.endTimeList

# search for sub- file list that fall in time range
index1 = bisect.bisect_left(afl1.endTimeList, afl.start_t)
### print '*** right after bisect_left(), index1: ', index1
if index1 == len(afl1.endTimeList):
    print '****** Error: User specified time range outside the target data set time range!'
    sys.exit(-1)

t1 = afl1.startTimeList[index1]
f1 = afl1.dirNameList[index1]

print 'afl.end_t: ', afl.end_t
### print 'afl1.startTimeList: ', afl1.startTimeList

# note: bisect finds the 1st time that is > afl.end_t
index2 = bisect.bisect_right(afl1.startTimeList, afl.end_t) - 1
### print '*** right after bisect_right(), index2: ', index2
if index2 <= 0:
    print '****** Error: User specified time range outside the target data set time range!'
    sys.exit(-1)

if index2 >= len(afl1.startTimeList):
    index2 = len(afl1.startTimeList) - 1

t2 = afl1.startTimeList[index2]
f2 = afl1.dirNameList[index2]

if index2 < index1:
    print '****** Error: In user specified time range, no target data set exists!'
    sys.exit(-1)

print target_data+' (start) time range:', t1, t2
print target_data+' file range:', f1, f2

print 'User specified '+target_data+' granule number range:', afl1.granuleNumList[index1], afl1.granuleNumList[index2]

# find out what data set the source data is
src_data = UT.parse_data_type(afl.datarootdir)
print 'src_data: ', src_data

# load the file list for src data granules (afl.listdir is where all the list files reside)
list_file1 = afl.listdir + '/' + src_data + '_granules.list.pkl'
print 'list_file1: ', list_file1

try:
    afl.load_lists(list_file1)
except IOError:
    print '****** list file for ' + src_data + ' does not exist.'
    sys.exit(-1)


# Instantiate a middle end class
midEnd = MD.middle_end()

# Instantiate a back end class
bakEnd = BD.back_end('netCDF')

# keeps track of the indices from the previous loop
pre_idx1 = 0
pre_idx2 = 0

# Makes sure we only create the supported variables report
# per run
catalog_created = 0

# loop over the sub- file list in target data set
for i in range(index1, index2+1):
    print ''
    print ''
    print ''
    print ''
    # for each file, read in data
    tgt_file = afl1.dirNameList[i]
    # Construct target data structure in the front end and read in the data
    print "****** Reading target data from file: ", tgt_file
    print 'granule num:', afl1.granuleNumList[i]
    print 'file start/end time:', afl1.startTimeList[i], afl1.endTimeList[i]
    if target_data == 'cloudsat':
	tgt_front_end = FEC.front_end_cloudsat(tgt_file)
    else:
	print '****** Error: '+target_data+' centric co-location is not supported at this moment !'
	sys.exit(-1)

    # Pass the target grid info to the middle end grid data structure
    # Get time info as an array
    midEnd.set_target_time(tgt_front_end.get_time())
    print 'target Unix Time = ', midEnd.get_target_time()
    print 'target Unix Time Range = ', min(midEnd.get_target_time()), max(midEnd.get_target_time())
    print 'target Unix Time Size = ', midEnd.get_target_time().size
    print ''

    # Get latitude info as an array
    midEnd.set_target_lat(tgt_front_end.get_latitude())
    print 'target Latitude = ', midEnd.get_target_lat()
    print 'target Latitude Range = ', min(midEnd.get_target_lat()), max(midEnd.get_target_lat())
    print 'target Latitude Size = ', midEnd.get_target_lat().size
    print ''

    # Get longitude info as an array
    midEnd.set_target_lon(tgt_front_end.get_longitude())
    print 'target Longitude = ', midEnd.get_target_lon()
    print 'target Longitude Range = ', min(midEnd.get_target_lon()), max(midEnd.get_target_lon())
    print 'target Longitude Size = ', midEnd.get_target_lon().size

    print "****** target data acquired! ******"
    print ''
    print ''


    # for each target granule, find time range
    st1 = afl1.startTimeList[i]
    et1 = afl1.endTimeList[i]
    ###print "****** src granule start time before adjustment:", st1
    # adjust start time (some 3min earlier becaue src is leading target)
    st1 -= datetime.timedelta(seconds=int(afl.time_diff))
    # adjust search range
    st1 -= datetime.timedelta(seconds=int(afl.time_search_range))
    print "****** target granule start time after adjustment:", st1
    # adjust end time (some 3min earlier becaue src is leading target)
    et1 -= datetime.timedelta(seconds=int(afl.time_diff))
    # adjust search range
    et1 += datetime.timedelta(seconds=int(afl.time_search_range))
    print "****** target granule end time after adjustment:", et1

    # search for src sub- file list that fall in time range
    idx1 = bisect.bisect_left(afl.endTimeList, st1)
    if idx1 == len(afl.endTimeList):
        idx1 -= 1
	print '****** Warning: search result indx1 is at the end of afl.endTimeList'

    ### print 'idx1: ', idx1
    ### print 'len(afl.endTimeList): ', len(afl.endTimeList)
    ### print 'max(afl.endTimeList): ', max(afl.endTimeList), ' min(afl.endTimeList): ', min(afl.endTimeList)

    tt1 = afl.startTimeList[idx1]
    ff1 = afl.dirNameList[idx1]

    # end time
    idx2 = bisect.bisect_right(afl.startTimeList, et1)
    if idx2 == len(afl.startTimeList):
        idx2 -= 1
	print '****** Warning: search result indx2 is at the end of afl.startTimeList'

    tt2 = afl.startTimeList[idx2]
    ff2 = afl.dirNameList[idx2]

    print 'st1: ', st1, ' et1: ', et1, 'idx1: ', idx1, ' idx2: ', idx2
    print 'src (start) time range:', tt1, tt2
    print 'src file range:', ff1, ff2

    # do not read any src file that's already read
    if idx1 <= pre_idx2:
        idx1 = pre_idx2 + 1

    if idx1 > idx2:
        print "****** No need to read src data from file because it's been already read."

    # loop over src files
    for j in range(idx1, idx2+1):
        print ''
        # read in data and co-locate to target grid
        print 'loop over src files j: ', j
        print 'src file:', afl.dirNameList[j]
        
        src_file = afl.dirNameList[j]
        # Read src data
        print "****** Reading src data from file: ", src_file

	# initialize a front end
	src_front_end = UT.get_front_end(src_data, src_file)
	### print 'src_front_end: ', src_front_end
    
        # Create a report of variables supported
        if catalog_created != 1:
            src_front_end.create_catalog()
            catalog_created = 1

        midEnd.set_src_time(src_front_end.get_time())
        print 'src Unix Time size = ', midEnd.get_src_time().size
        print 'src Unix Time = ', midEnd.get_src_time()
        print 'src Unix Time Range = ', min(midEnd.get_src_time()), max(midEnd.get_src_time())
        
        midEnd.set_src_lat(src_front_end.get_latitude())
        print 'src Latitude size = ', midEnd.get_src_lat().size
        print 'src Latitude Range = ', min(midEnd.get_src_lat()), max(midEnd.get_src_lat())
        print 'src Latitude = ', midEnd.get_src_lat()
    
        midEnd.set_src_lon(src_front_end.get_longitude())
        print 'src Longitude size = ', midEnd.get_src_lon().size
        print 'src Longitude Range = ', min(midEnd.get_src_lon()), max(midEnd.get_src_lon())
        print 'src Longitude = ', midEnd.get_src_lon()
        
        midEnd.set_src_data(src_front_end.get_data())
        
        print "****** src data acquired! ******"
    # end of for j loop (over src granules)

    # for model data, tell the middle end about the uniform grid info.
    # so time interpolation can be done
    if src_data == 'ecmwf-idaily' or src_data == 'ecmwf-yotc-aos-1.5deg' or src_data == 'ecmwf-yotc-aopl-1.5deg' or src_data == 'ecmwf-yotd-aoml-1.5deg':
	   (num_time_steps, num_lat, num_lon) = src_front_end.get_src_uniform_grid_info()
	   midEnd.set_src_uniform_grid_info(num_time_steps, num_lat, num_lon)

    ### midEnd.co_locate(config_file, tgt_config_file)
    midEnd.co_locate(afl, afl1)

    print '****** midEnd.good_cnt: ', midEnd.good_cnt
    print '****** success match rate (%): ', (100.0*midEnd.good_cnt)/midEnd.get_target_time().size

    # set target file name
    tgt_file_name = os.path.basename(tgt_file)
    dp = tgt_file_name.find('.')
    tf_name = tgt_file_name[0:dp]
    bakEnd.set_output_filename(afl.outputdir+'/'+src_data+'_'+tf_name+'.nc')

    # pass data to back end
    bakEnd.set_target_time(midEnd.get_target_time())
    bakEnd.set_target_lat(midEnd.get_target_lat())
    bakEnd.set_target_lon(midEnd.get_target_lon())
    bakEnd.set_target_data(midEnd.get_target_data())
    bakEnd.set_target_levels(src_front_end.get_levels())

    # write out to output file
    bakEnd.write_output()
    
    # To aid when remote profiling only
    ### hp.heapu()
    ### print '----------- now sleeping ...'
    ### time.sleep(600)

    pre_idx1 = idx1
    pre_idx2 = idx2

# end of for i loop (over target granules)

# stop the timer
now = datetime.datetime.now()
elapsed_days = (now - start).days
elapsed_secs = (now - start).seconds
print '*** elapsed time: ', elapsed_days, ' days, ', elapsed_secs, ' seconds'
















# FOOTER:
#
#  Indentation settings for Vim and Emacs.  Please do not modify.
# 
#  Local Variables:
#  c-basic-offset: 4
#  indent-tabs-mode: nil
#  End:
# 
#  vim: set sts=4 sw=4
#
