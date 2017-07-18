'''
import os
os.chdir('/home/bytang/projects/collocation/dev')
execfile('/home/bytang/projects/collocation/dev/pdriver.py') 



'''
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

import dataset_registry

import front_end_cloudsat as FEC

import middle_end as MD
import back_end as BD

from sdriver import sdriver


# for Python 2.6
### from multiprocessing import Process, Lock
from multiprocessing import Process, Lock
# for Python 2.5
#from processing import Process, Lock
### from processing.sharedctypes import Value, Array


# Enable remote profiling via 'Heapy'.  Start the remote session
# first using % python -c "from guppy import hpy;hpy().monitor()"
# Then start this program and see the monitor section of:
#    http://guppy-pe.sourceforge.net/heapy_Use.html
# See also hp.heapu()
#import guppy.heapy.RM
#import time             # to use time.sleep(60) as a profiling aid (to pause)

#if __name__ == '__main__':
if 1:
    if 0:
      if len(sys.argv) <= 2 or sys.argv[1] == '-h' or sys.argv[1] == '-help' or \
                  sys.argv[1] == '--help':
          print '****** Usage: python ' + sys.argv[0] + ' path_to_src_data_config_xml_file' + \
                  ' path_to_target_data_config_xml_file'
          sys.exit(2)
      else:
          config_file = sys.argv[1]
          tgt_config_file = sys.argv[2]

    if 1:
        mainDir = '/home/bytang/projects/collocation'

        if 0:
          tgt_config_file = '%s/input/cloudsat_config.xml'%(mainDir)
          config_file = '%s/input/mls-h2o_config.xml'%(mainDir)
          target_data = 'cloudsat'

        if 1:
          tgt_config_file = '%s/input/mls-h2o_config.xml'%(mainDir)
          config_file = '%s/input/airs_config.xml'%(mainDir)
          target_data = 'mls-h2o'

        if 0:
          tgt_config_file = '%s/input/mls-h2o_config.xml'%(mainDir)
          config_file = '%s/input/cloudsat_config.xml'%(mainDir)
          target_data = 'mls-h2o'

          #tgt_config_file = '%s/input/cloudsat_config_.xml'%(mainDir)
          #config_file = '%s/input/mls_h2o_config_.xml'%(mainDir)
        #config_file = '%s/input/cloudsat_config.xml'%(mainDir)

 
    # for CloudSat centric co-location

    # read configure info. from src config_file
    try:
	afl = FL.file_list(config_file) # afl is used for src data
    except IOError:
	print '****** src data config file does not exist.'
	sys.exit(-1)

    # number of cores you would like to use
    num_cores = int(afl.num_cores)
    # number of target granules a process would handle
    proc_size = int(afl.proc_size)

    # find out what data set the source data is
    #src_data = UT.parse_data_type(afl.datarootdir)
    src_data = afl.dataset_name
    print 'src data set type: ', src_data

    dset_container = dataset_registry.get_dataset_container(src_data)

    # load the file list for src data
    list_file = afl.listdir + '/' + src_data + '_granules.list.pkl'
    print 'list_file: ', list_file

    try:
	afl.load_lists(list_file)
    except IOError:
	print '****** list file for src data does not exist.'
	sys.exit(-1)

    # read configure info. from target config_file
    try:
	afl1 = FL.file_list(tgt_config_file) # afl1 is used for target data
    except IOError:
	print '****** target data config file does not exist.'
	sys.exit(-1)

    # load the file list for target data (e.g., CloudSat)
    list_file1 = afl1.listdir + '/' + target_data + '_granules.list.pkl'
    print 'list_file1: ', list_file1

    try:
	afl1.load_lists(list_file1)
    except IOError:
	print '****** list file for target data does not exist.'
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

    # print afl1.dirNameList
    # print afl1.granuleNumList

    print 'afl.start_t: ', afl.start_t
    ### print 'afl1.endTimeList: ', afl1.endTimeList

    # search for sub- file list that fall in time range
    index1 = bisect.bisect_left(afl1.endTimeList, afl.start_t)
    print '*** right after bisect_left(), index1: ', index1
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

    print 'index1: ', index1, ', index2: ', index2
    print 'User specified '+target_data+' granule number range:', afl1.granuleNumList[index1], afl1.granuleNumList[index2]

    # initialize a front end
    src_file = afl.dirNameList[0]
    # gblock 3/22/2011 src_front_end = UT.get_front_end(src_data, src_file)
    src_front_end = dset_container.get_front_end(src_file)
    print 'src_front_end: ', src_front_end

    # Create a report of variables supported
    src_front_end.create_catalog()

    # algorithm to split the index range (index1, index2) into multiple smaller ranges
    # total num of target granules
    tot_granules = index2-index1+1
    # a group is a number of processes that will finish before the next group starts
    group_size = num_cores * proc_size
    num_groups = tot_granules/group_size
    if (tot_granules - num_groups*group_size) > 0:
	num_groups += 1

    # number of processes to be spawned to finish the task
    num_processes = tot_granules/proc_size
    if (tot_granules - num_processes*proc_size) > 0:
	num_processes += 1

    print 'num_cores: ', num_cores
    print 'proc_size: ', proc_size
    print 'group_size: ', group_size
    print 'tot_granules: ', tot_granules
    print 'num_groups: ', num_groups
    print 'num_processes: ', num_processes

    index_range = UT.index_distribution(index1, index2, num_processes)
    print 'index_range: '
    print index_range

    ### sys.exit(-1)

    i = 0
    for g in range(num_groups):
	print ''
	print ''
	print ''
	print ''
	print ''
	print ''
	print '------------- group: ', g, ' ------------'
	jobs = []
	pcnt = 0
	for s in range(num_cores):
	    if i < num_processes:
		# spawn sdriver() as a process
		p = Process(target=sdriver, args=(g, s, src_data, target_data, afl, \
			    afl1, index_range[i][0], index_range[i][1], ))
		p.start()
		print 'process started: ', pcnt
		pcnt += 1
		jobs.append(p)
		i += 1

	pcnt = 0
	for p in jobs:
	    p.join()
	    print 'process done: ', pcnt
	    pcnt += 1

    # end of for g loop

    # stop the timer
    now = datetime.datetime.now()
    elapsed_days = (now - start).days
    elapsed_secs = (now - start).seconds
    print '*** elapsed time: ', elapsed_days, ' days, ', elapsed_secs, ' seconds'

    ### elapsed_days = now.day - start.day
    ### elapsed_hours = now.hour - start.hour
    ### elapsed_minutes = now.minute - start.minute
    ### elapsed_seconds = now.second - start.second
    ### print '*** elapsed time: ', elapsed_days, ' days, ', elapsed_hours, ' hours, ', elapsed_minutes, ' minutes, ', elapsed_seconds, ' seconds'

# end of __main__













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
