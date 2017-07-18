import numpy as N
import file_list as FL
import datetime
import bisect
import util as UT
import sys
import nna

import struct

class middle_end:

    def __init__(self):
        self.src_time = N.array([])         # elapsed second since Unix time
        self.src_latitude = N.array([])     # in degree
        self.src_longitude = N.array([])    # in degree
        self.target_time = N.array([])      # elapsed second since Unix time
        self.target_latitude = N.array([])  # in degree
        self.target_longitude = N.array([]) # in degree

	self.file = None                    # for output of visualization data
	self.nn_idx = N.array([])
	self.invalid_data = -909090

	# data can be SST, WSPD, VAPOR, CLOUD, RAIN, etc. in physical meaning
	# but the middle end only takes it as "data"
	# self.src_data is a dictionary of tuples
        self.src_data = {}
	# where co-located data is, also a dictionary of tuples
        self.target_data = {}

	# for model data, e.g., ECMWF, that requires time interpolation
	self.time_interpolation = False
	# info. about the uniform grid of the model data
	self.num_time_step = 0
	self.num_lat = 0
	self.num_lon = 0
	self.grid_size = 0

    ### def co_locate(self, config_file, tgt_config_file):
    def co_locate(self, afl, afl1):

	start = datetime.datetime.now()

	print '****** in middle end co_locate() ... '

	# set for later use in a different func
	self.invalid_data = afl.invalid_data

	tgt_time_len = len(self.target_time)
	src_time_len = len(self.src_time)
	print 'tgt_time_len: ', tgt_time_len
	print 'src_time_len: ', src_time_len

	# to verify that the two time arrays are actually sorted
	for mm in range(tgt_time_len-1):
	    if self.target_time[mm] > self.target_time[mm+1]:
		print '********** self.target_time[] is NOT sorted !!!'
		sys.exit(-1)    
	print '********** self.target_time[] is sorted.'


	for mm in range(src_time_len-1):
	    if self.src_time[mm] > self.src_time[mm+1]:
		print '********** self.src_time[] is NOT sorted !!!'
		sys.exit(-1)    
	print '********** self.src_time[] is sorted.'

	# read configure info. from config_file
	"""
	try:
	    afl = FL.file_list(config_file)
	except IOError:
	    print '****** src data config file does not exist.'
	    sys.exit(-1)
	"""

	# read configure info. from tgt_config_file
	"""
	try:
	    afl1 = FL.file_list(tgt_config_file)
	except IOError:
	    print '****** target data config file does not exist.'
	    sys.exit(-1)
	"""

	# self.target_data is a dictionary of tuples, with 1st element
	# being attributes, and 2nd element being arrays, possibly 2-4D arrays
	# of data
	keys = self.src_data.keys()
	#-- print 'keys: ', keys
	### self.target_data = ['0']*len(keys)
	### self.target_data = {keys[0]: (0, 0)}
	for k in keys:
	    #-- print '--- k: ', k
	    ### self.target_data[k] = ('0', [])
	    ### print 'self.target_data[k]: ', self.target_data[k]

	    dim = len((self.src_data[k][1]).shape)
	    #-- print 'dim: ', dim
	    edim = [0]*dim
	    tot_d = 1
	    for dd in range(1, dim):
		edim[dd] = self.src_data[k][1].shape[dd]
		tot_d *= edim[dd]
		#-- print 'edim[',dd,']: ', edim[dd]
	    #-- print 'tot_d: ', tot_d
	    #-- print 'tgt_time_len: ', tgt_time_len

	    aa = N.array([float(afl.invalid_data)]*tgt_time_len*tot_d, N.float32)

	    if dim == 1:
		self.target_data[k] = (self.src_data[k][0], aa)
	    elif dim == 2:
		self.target_data[k] = (self.src_data[k][0], N.reshape(aa, (tgt_time_len, edim[1])))
	    elif dim == 3:
		self.target_data[k] = (self.src_data[k][0], N.reshape(aa, (tgt_time_len, edim[1], edim[2])))
	    elif dim == 4:
		self.target_data[k] = (self.src_data[k][0], N.reshape(aa, (tgt_time_len, edim[1], edim[2], edim[3])))
	# end for k in keys

	#-- print 'int(afl.time_diff): ', int(afl.time_diff)

	# get time search window for the current target granule

	# start time of this granule
	tt = self.target_time[0]
	#-- print '--- target time: ', tt
	tts = tt - int(afl.time_diff)
	tts -= int(afl.time_search_range)
	index1 = bisect.bisect_left(self.src_time, tts)
	# adjust index1 so it is with array bound
	if index1 == src_time_len:
	    index1 -= 1
	    print '****** Warning: search result index1 is at the end of self.src_time'
            print min(self.src_time), max(self.src_time), tts, min(self.target_time), max(self.target_time)

	# end time of this granule
	tt = self.target_time[tgt_time_len-1]
	tte = tt - int(afl.time_diff)
	tte += int(afl.time_search_range)
	index2 = bisect.bisect_left(self.src_time, tte)
	# adjust index2 so it is with array bound
	if index2 == src_time_len:
	    index2 -= 1
	    print '****** Warning: search result index2 is at the end of self.src_time'

	#-- print '--- index1: ', index1, ', index2: ', index2, ' diff: ', index2-index1+1
	"""
	#-- print '--- src_time1: ', self.src_time[index1], ', src_time2: ', self.src_time[index2], \
	' diff: ', self.src_time[index2] - self.src_time[index1]
	"""

	### spatial_search_range = float(afl.footprint_size)
	spatial_search_range = float(afl.space_search_factor) * (float(afl.footprint_size) + float(afl1.footprint_size))
	print '*** spatial_search_range: ', spatial_search_range

	cell_search_limit = int(afl.cell_search_limit)

	start1 = datetime.datetime.now()

	# instantiate a class of Nearest Neighbor Algorithm
	anna = nna.nna(self.target_latitude, self.target_longitude, self.src_latitude, self.src_longitude, \
		       index1, index2, spatial_search_range, cell_search_limit)

	now1 = datetime.datetime.now()
	elapsed_time = now1 - start1
	print 'elapsed_time: ', elapsed_time
	print '*** nna elapsed time: ', elapsed_time.days, ' days, ', elapsed_time.seconds, ' seconds'

	start1 = datetime.datetime.now()

	(nn_idx, dist) = anna.search_nn()

	now1 = datetime.datetime.now()
	elapsed_time = now1 - start1
	print 'elapsed_time: ', elapsed_time
	print '*** search_nn() elapsed time: ', elapsed_time.days, ' days, ', elapsed_time.seconds, ' seconds'

	self.nn_idx = nn_idx

	print 'len(self.nn_idx): ', len(self.nn_idx), ' len(dist): ', len(dist)
	print '1. self.nn_idx[]: ', self.nn_idx

	self.good_cnt = 0
	# loop over target points
	for i in range(tgt_time_len):  # i is the index of the target data point
	    # found nearest neighbor in src data and copy data from src to target point
	    jj = self.nn_idx[i]
	    if jj != nna.NOT_NN:  # jj is the index of the src data point that is the NN of target point
		self.good_cnt += 1
		#print ' ****** good data co-located! ******'
		### print '--- i: ', i, ' jj: ', jj, ' dist: ', dist[i]
		#print '--- i: ', i, ' dist: ', dist[i]
		# src jj is the nearest neighbor of target i
		keys = self.src_data.keys()
		# for model data such as ECMWF do time interpolation
		if self.time_interpolation == True:
		    # time interpolation
		    #-- print 'jj: ', jj
		    tgt_time = self.target_time[i]
		    #-- print 'tgt_time: ', tgt_time
		    # locate src time steps that span tgt_time
		    indx1 = bisect.bisect_left(self.src_time, tgt_time)
		    # adjust indx1 so it is with array bound
		    if indx1 == src_time_len:
			indx1 -= 1
			print '****** Warning: search result indx1 is at the end of self.src_time'
		    #-- print 'indx1: ', indx1

		    src_time1 = self.src_time[indx1-1]
		    src_time2 = self.src_time[indx1]
		    #-- print 'src_time1: ', src_time1, ', src_time2: ', src_time2

		    # find src index in relative to its own "page" 
		    # (all (lat,lon) points for one time step form a page)
		    offset = jj - (jj/self.grid_size)*self.grid_size
		    #-- print 'offset: ', offset
		    # points with the same offset share the same (lat, lon)
		    # so they are all NN of the target point
		    jj2 = indx1 + offset  # indx1 starts a src grid page
		    jj1 = jj2 - self.grid_size
		    #-- print 'jj1: ', jj1, ' jj2: ', jj2

		    # now loop over list of data arrays and get data after time interpolation
		    for k in keys:
			self.target_data[k][1][i] = UT.linear_interpolation(src_time1, self.src_data[k][1][jj1], \
			    src_time2, self.src_data[k][1][jj2], tgt_time)

		else:
		    # now loop over list of data arrays and get data
		    for k in keys:
			### print 'k: ', k, 'i: ', i
			### print 'self.src_data[k][1][jj]: ', self.src_data[k][1][jj]
			### print 'self.target_data[k]: ', self.target_data[k]
			self.target_data[k][1][i] = self.src_data[k][1][jj]
		# end if self.time_interpolation == True
	    # end if jj != nna.NOT_NN
	# end for i in range(len(self.nn_idx))

	print '****** self.good_cnt: ', self.good_cnt

	now = datetime.datetime.now()
	elapsed_time = now - start
	print '*** co_location elapsed time: ', elapsed_time.days, ' days, ', elapsed_time.seconds, ' seconds'

    # end of co_locate()


    def set_target_time(self, time):
	self.target_time = time

    def get_target_time(self):
	return self.target_time

    def set_src_time(self, time):
	self.src_time = N.concatenate((self.src_time, time), 0)

    def get_src_time(self):
	return self.src_time

    def set_src_lat(self, lat):
	self.src_latitude = N.concatenate((self.src_latitude, lat), 0)

    def get_src_lat(self):
	return self.src_latitude

    def set_src_lon(self, lon):
	self.src_longitude = N.concatenate((self.src_longitude, lon), 0)

    def get_src_lon(self):
	return self.src_longitude

    def set_src_data(self, data):
	#-- print '--- len(self.src_data.keys()): ', len(self.src_data.keys())
	if len(self.src_data.keys()) > 0:
	    for kk in self.src_data.keys():
		self.src_data[kk] = (self.src_data[kk][0], N.concatenate((self.src_data[kk][1], data[kk][1]), 0))
	else:
	    self.src_data = data

    def set_src_uniform_grid_info(self, num_time_step, num_lat, num_lon):
	self.time_interpolation = True
	# info. about the uniform grid of the model data
	self.num_time_step = num_time_step
	self.num_lat = num_lat
	self.num_lon = num_lon
	self.grid_size = self.num_lat * self.num_lon
	#-- print 'self.num_time_step: ', self.num_time_step, ' self.num_lat: ', self.num_lat, \
		#-- ' self.num_lon: ', self.num_lon, ' self.grid_size: ', self.grid_size

    def get_src_data(self):
	return self.src_data

    def set_target_lat(self, lat):
	self.target_latitude = lat

    def get_target_lat(self):
	return self.target_latitude

    def set_target_lon(self, lon):
	self.target_longitude = lon

    def get_target_lon(self):
	return self.target_longitude

    def get_target_data(self):
	return self.target_data

    def set_output_filename(self, file):
	self.file = file

    def get_invalid_data(self):
        return self.invalid_data

    def output_latlon(self):
	# format1 = 'i'
	# format2 = 'f3, f3'

	# open file for output
	output_file = open(self.file, 'w')

	# for visualization, write out lat/lon of target points
	# and their nearest neighbors in src data set
	tgt_time_len = len(self.target_time)
	output_file.write(str(tgt_time_len)+'\n')

	print '2. self.nn_idx[]: ', self.nn_idx
	for i in range(tgt_time_len):
	    jj = self.nn_idx[i]
	    ### print 'jj: ', jj
	    if jj != nna.NOT_NN:  
		output_file.write(str(self.target_latitude[i])+' '+str(self.target_longitude[i]) \
		    +' '+str(self.src_latitude[jj])+' '+str(self.src_longitude[jj])+'\n')
	    else:
		output_file.write(str(self.target_latitude[i])+' '+str(self.target_longitude[i]) \
		    +' '+str(self.invalid_data)+' '+str(self.invalid_data)+'\n')
	# end of for i

	# for visualization, write out lat/lon of all src points
	# that participated in the game of NN search
	src_time_len = len(self.src_time)
	output_file.write(str(src_time_len)+'\n')

	for i in range(src_time_len):
	    output_file.write(str(self.src_latitude[i])+' '+str(self.src_longitude[i])+'\n')
	# end of for i

	# close file
	output_file.close()

    # end of output_latlon()



    """
    def print_data(self):
	print 'size: ', len(self.src_data.keys())
	for elem in self.src_data:
	    print 'src data array: ', elem
    """



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


