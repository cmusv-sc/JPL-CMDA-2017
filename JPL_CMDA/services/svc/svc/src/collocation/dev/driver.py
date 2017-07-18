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

import sdriver

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

# initialize a front end
src_file = afl.dirNameList[0]
src_front_end = UT.get_front_end(src_data, src_file)
print 'src_front_end: ', src_front_end

# Create a report of variables supported
src_front_end.create_catalog()

# call the sequential driver (just a function call, no process spawning)
sdriver.sdriver(0, 0, src_data, target_data, afl, afl1, index1, index2)

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
