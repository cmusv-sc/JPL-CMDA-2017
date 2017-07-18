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




# ------------ sequential driver ----------------------------
def sdriver(gid, pid, src_data, target_data, afl, afl1, index1, index2):

    print '--------- inside sdriver(), gid: ', gid, ', pid: ', pid, ' ----------'
    print 'index1: ', index1, ', index2: ', index2

    start = datetime.datetime.now()

    # get front end dataset container (gblock 3/21/2011)
    dset_container = afl.dataset_container

    # Instantiate a middle end class
    midEnd = MD.middle_end()

    # Instantiate a back end class
    bakEnd = BD.back_end('netCDF')

    # keeps track of the indices from the previous loop
    pre_idx1 = -1 
    pre_idx2 = -1

    # Makes sure we only create the supported variables report
    # per run
    # (moved to pdriver.py)
    """
    catalog_created = 0
    """

    # save these values from last i iteration, just in case
    # in the current i loop, there is no need to read from
    # any j loop src granules
    num_time_steps0 = 0
    num_lat0 = 0
    num_lon0 = 0

    src_front_end = None

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
        
	elif target_data == 'mls-h2o':
            import front_end_mls_h2o
	    tgt_front_end = front_end_mls_h2o.front_end_mls_h2o(tgt_file)
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
	print 'idx1: ', idx1
	if idx1 == len(afl.endTimeList):
	    idx1 -= 1
	    print '****** Warning: search result indx1 is at the end of afl1.endTimeList'

	print 'idx1 (after shift): ', idx1
	### print 'len(afl.endTimeList): ', len(afl.endTimeList)
	### print 'max(afl.endTimeList): ', max(afl.endTimeList), ' min(afl.endTimeList): ', min(afl.endTimeList)

	tt1 = afl.startTimeList[idx1]
	ff1 = afl.dirNameList[idx1]

	# end time
	idx2 = bisect.bisect_right(afl.startTimeList, et1) - 1
	print 'idx2: ', idx2
	if idx2 == len(afl.startTimeList):
	    idx2 -= 1
	    print '****** Warning: search result indx2 is at the end of afl1.startTimeList'
	print 'idx2 (after shift): ', idx2

	tt2 = afl.startTimeList[idx2]
	ff2 = afl.dirNameList[idx2]

	# check tt2 and tt1. skip to the next i loop if
	# no src granule is found for the target granule
	if tt1 > tt2:
	    print '****** Warning: there is no source granule within the target time search range.'
	    print '       Skip to the next target granule.'
	    continue

	print 'st1: ', st1, ' et1: ', et1, 'idx1: ', idx1, ' idx2: ', idx2
	print 'src (start) time range:', tt1, tt2
	print 'src file range:', ff1, ff2

	# do not read any src file that's already read
	if idx1 <= pre_idx2:
	    idx1 = pre_idx2 + 1

	if idx1 > idx2:
	    print "****** No need to read src data from file because it's been already read."

	print 'idx1: ', idx1, ', idx2: ', idx2

        start_reading_src_time = datetime.datetime.now()
	# loop over src files
	for j in range(idx1, idx2+1):
	    print ''
	    # read in data and co-locate to target grid
	    print 'loop over src files j: ', j
	    print 'src file:', afl.dirNameList[j]
        
	    src_file = afl.dirNameList[j]
	    # Read src data
	    print "****** Reading src data from file: ", src_file

	    # initialize a front end (gblock, 3/22/2011)
	    src_front_end = dset_container.get_front_end (src_file)
	    print 'src_front_end: ', src_front_end
    
	    # Create a report of variables supported
	    # (moved to pdriver.py)
	    """
	    if catalog_created != 1:
		src_front_end.create_catalog()
		catalog_created = 1
	    """

	    midEnd.set_src_time(src_front_end.get_time())
	    print 'src Unix Time size = ', midEnd.get_src_time().size
	    print 'src Unix Time = ', midEnd.get_src_time()
	    print 'src Unix Time Range = ', min(midEnd.get_src_time()), max(midEnd.get_src_time())
        
#zzzz
            if j>idx1:
              temp1 = midEnd.src_time[1:] - midEnd.src_time[:-1]
              print 'src_time, Is it sortedsorted?'
              print temp1.min()
              print temp1.max()
              print midEnd.src_time.shape
              if temp1.min()<0.0:
                import numpy as np
                np.save('/home/bytang/projects/collocation/output/src_time_%02d.npy'%(j), \
                      midEnd.src_time)
	    midEnd.set_src_lat(src_front_end.get_latitude())
	    print 'src Latitude size = ', midEnd.get_src_lat().size
	    print 'src Latitude Range = ', min(midEnd.get_src_lat()), max(midEnd.get_src_lat())
	    print 'src Latitude = ', midEnd.get_src_lat()
    
	    midEnd.set_src_lon(src_front_end.get_longitude())
	    print 'src Longitude Range = ', min(midEnd.get_src_lon()), max(midEnd.get_src_lon())
	    print 'src Longitude size = ', midEnd.get_src_lon().size
	    print 'src Longitude = ', midEnd.get_src_lon()
        
	    start1 = datetime.datetime.now()

	    midEnd.set_src_data(src_front_end.get_data())
        
	    now1 = datetime.datetime.now()
	    elapsed_time = now1 - start1
	    print 'elapsed_time: ', elapsed_time
	    print '*** midEnd.set_src_data elapsed time: ', elapsed_time.days, ' days, ', elapsed_time.seconds, ' seconds'

	    print "****** src data acquired! ******"
	# end of for j loop (over src granules)

	# for model data, tell the middle end about the uniform grid info.
	# so time interpolation can be done
        #
        #   special note: complex "if" statment has been moved to dset_nemo.py
        #     new front ends should use new dset containers & register container in util.py
        #     see dset_ecmwf_idaily_surface_ncar.py for example
        #
      
        end_reading_src_time = datetime.datetime.now()
        elapsed_time = end_reading_src_time - start_reading_src_time
	print '*** src reading and assigning elapsed time: ', elapsed_time.days, ' days, ', elapsed_time.seconds, ' seconds'
        
 
        if dset_container.is_uniform_grid ():
	    print 'sdriver (dataset is on uniform grid) - src_front_end: ', src_front_end
            print 'using time interpolation for co-location'

	    if src_front_end == None:
		num_time_steps = num_time_steps0
		num_lat = num_lat0
		num_lon = num_lon0
	    else:
		(num_time_steps, num_lat, num_lon) = src_front_end.get_src_uniform_grid_info()
		# save the values for reuse possibly in the next i loop
		num_time_steps0 = num_time_steps
		num_lat0 = num_lat
		num_lon0 = num_lon

	    midEnd.set_src_uniform_grid_info(num_time_steps, num_lat, num_lon)

	start1 = datetime.datetime.now()
	midEnd.co_locate(afl, afl1)
	now1 = datetime.datetime.now()
	elapsed_time = now1 - start1
	print '*** midEnd.co_locate elapsed time: ', elapsed_time.days, ' days, ', elapsed_time.seconds, ' seconds'

	print '****** midEnd.good_cnt: ', midEnd.good_cnt
	print '****** success match rate (%): ', (100.0*midEnd.good_cnt)/midEnd.get_target_time().size, 'for target granule ', afl1.granuleNumList[i]

        if midEnd.good_cnt == 0:
           print 'No co-located data. Will not call the back-end. Skip to the next target granule.'
           continue

	start1 = datetime.datetime.now()
	# set target file name
	tgt_file_name = os.path.basename(tgt_file)
	dp = tgt_file_name.find('.')
	tf_name = tgt_file_name[0:dp]

	# for visualization of nearest neighbors and footprints
	# this is not essential to the product and can be commented out
	### midEnd.set_output_filename(afl.outputdir+'/'+'latlon_'+src_data+'_'+tf_name+'.txt')
	### midEnd.output_latlon()

	# pass data to back end
	bakEnd.set_target_time(midEnd.get_target_time())
	bakEnd.set_target_lat(midEnd.get_target_lat())
	bakEnd.set_target_lon(midEnd.get_target_lon())
	bakEnd.set_target_data(midEnd.get_target_data())
	bakEnd.set_invalid_data(midEnd.get_invalid_data())
	### print 'before set_target_levels(), src_front_end: ', src_front_end
	bakEnd.set_target_levels(src_front_end.get_levels())

	# write out to output file
	bakEnd.set_output_filename(afl.outputdir+'/'+src_data+'_'+tf_name+'.nc')
	bakEnd.write_output(afl)
    
	now1 = datetime.datetime.now()
	elapsed_time = now1 - start1
	print '*** backend elapsed time: ', elapsed_time.days, ' days, ', elapsed_time.seconds, ' seconds'

	# To aid when remote profiling only
	#time.sleep(60)

	pre_idx1 = idx1
	pre_idx2 = idx2

    # end of for i loop (over target granules)

    now = datetime.datetime.now()
    elapsed_time = now - start
    print '*** sdriver elapsed time: ', elapsed_time.days, ' days, ', elapsed_time.seconds, ' seconds'

    print '--------- exiting sdriver(), gid: ', gid, ', pid: ', pid, ' ----------'
# end of sdriver()













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
