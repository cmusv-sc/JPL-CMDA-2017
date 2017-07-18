import os
import sys
from datetime import datetime, date, time
import pickle
import bisect
import util as UT
import dataset_registry
from xml.dom.minidom import parse
from xml.dom import EMPTY_NAMESPACE
from xml.dom import Node

class file_list:
    config_file_name = ''
    datarootdir = ''
    listdir = ''
    uTimeList = []
    dirNameList = []
    dirNameSet = ()
    startTimeList = []
    endTimeList = []
    granuleNumList = [] # for data products that have granule numbers in bookkeeping


    def __init__(self, name):
	self.config_file_name = name
	try:
	    doc = parse(self.config_file_name)
	except IOError:
	    print '****** Could not find configure file!'
	    raise IOError

	# default value
	self.datarootdir = "/data1/sensors/atrain/cloudsat/CLDCLASS/R04"
	###self.datarootdir = "/data1/sensors/atrain/amsre.aqua"

	elems = doc.getElementsByTagName('data_root_dir')
	###print 'elems type: ', type(elems[0])
	###print 'elems: ', elems[0].childNodes
	if len(elems) > 0:
	    for c in elems[0].childNodes:
		if c.nodeType != Node.COMMENT_NODE and len(c.data) > 1:
		    ###print 'c: ', c.data
		    self.datarootdir = (c.data).encode('UTF-8').strip('\n').strip()
        else:
            print "***** warning in file_list.__init__ - missing data_root_dir in config file"
            print "      config filename: ", self.config_file_name
            print "      using : ", self.datarootdir

            print 'self.datarootdir: ', self.datarootdir
            
        # get front end name, if present in xml file
        # gblock 3/17/2011 - added front end name to xml file
        self.dataset_name = ''
        elems = doc.getElementsByTagName('dataset_name')
	if len(elems) > 0:
	    for c in elems[0].childNodes:
		if c.nodeType != Node.COMMENT_NODE and len(c.data) > 1:
		    ###print 'c: ', c.data
		    self.dataset_name = (c.data).encode('UTF-8').strip('\n').strip()

        # check for name defined by xml statement
        if (self.dataset_name == ''):
            self.dataset_name = UT.parse_data_type (self.datarootdir)

        print 'self.dataset_name: ', self.dataset_name

        # get container for dataset
        self.dataset_container = dataset_registry.get_dataset_container (self.dataset_name)

        self.dataset_container.set_datarootdir (self.datarootdir)
        
	# default value
	self.listdir = os.path.expanduser('~')

	elems = doc.getElementsByTagName('list_dir')
	if len(elems) > 0:
	    for c in elems[0].childNodes:
		if c.nodeType != Node.COMMENT_NODE and len(c.data) > 1:
		    self.listdir = (c.data).encode('UTF-8').strip('\n').strip()
        else:
            print "***** warning in file_list.__init__ - missing list_dir in config file"
            print "      config filename: ", self.config_file_name
            print "      using : ", self.listdir
	###print 'self.listdir: ', self.listdir

	# default value
	self.outputdir = os.path.expanduser('~')

	elems = doc.getElementsByTagName('output_dir')
	if len(elems) > 0:
	    for c in elems[0].childNodes:
		if c.nodeType != Node.COMMENT_NODE and len(c.data) > 1:
		    self.outputdir = (c.data).encode('UTF-8').strip('\n').strip()
        else:
            print "***** warning in file_list.__init__ - missing output_dir in config file"
            print "      config filename: ", self.config_file_name
            print "      using : ", self.outputdir

	print 'self.outputdir: ', self.outputdir

	# default value
	self.start_t = datetime.strptime('11/02/2006 03:15:25', "%m/%d/%Y %H:%M:%S") # TBD: use CloudSat start time

	elems = doc.getElementsByTagName('start_time')
	if len(elems) > 0:
	    for c in elems[0].childNodes:
		if c.nodeType != Node.COMMENT_NODE and len(c.data) > 1:
		    st = (c.data).encode('UTF-8').strip('\n').strip()
		    ###print 'st: ', st
		    ### self.start_t = datetime.strptime(st, "%m/%d/%Y %H:%M:%S%p")
		    self.start_t = datetime.strptime(st, "%m/%d/%Y %H:%M:%S")
        else:
            print "***** warning in file_list.__init__ - missing start_time in config file"
            print "      config filename: ", self.config_file_name
            print "      using : ", self.start_t
            
	# default value
	self.end_t = datetime.strptime('11/04/2006 07:35:20', "%m/%d/%Y %H:%M:%S") # TBD: use CloudSat end time

	elems = doc.getElementsByTagName('end_time')
	if len(elems) > 0:
	    for c in elems[0].childNodes:
		if c.nodeType != Node.COMMENT_NODE and len(c.data) > 1:
		    et = (c.data).encode('UTF-8').strip('\n').strip()
		    ###print 'et: ', et
		    self.end_t = datetime.strptime(et, "%m/%d/%Y %H:%M:%S")
        else:
            print "***** warning in file_list.__init__ - missing end_time in config file"
            print "      config filename: ", self.config_file_name
            print "      using : ", self.end_t
            
	# default value (2min)
	self.time_diff = '120'

	elems = doc.getElementsByTagName('time_diff')
	if len(elems) > 0:
	    for c in elems[0].childNodes:
		if c.nodeType != Node.COMMENT_NODE and len(c.data) > 1:
		    self.time_diff = (c.data).encode('UTF-8').strip('\n').strip()
		    ### print 'self.time_diff: ', self.time_diff
        else:
            print "***** warning in file_list.__init__ - missing time_diff in config file"
            print "      config filename: ", self.config_file_name
            print "      using : ", self.time_diff
            
	# default value (15min)
	self.time_search_range = '900'

	elems = doc.getElementsByTagName('time_search_range')
	if len(elems) > 0:
	    for c in elems[0].childNodes:
		if c.nodeType != Node.COMMENT_NODE and len(c.data) > 1:
		    self.time_search_range = (c.data).encode('UTF-8').strip('\n').strip()
        else:
            print "***** warning in file_list.__init__ - missing time_search_range in config file"
            print "      config filename: ", self.config_file_name
            print "      using : ", self.time_search_range
            
	print 'self.time_search_range: ', self.time_search_range

	# default value (20km)
	self.footprint_size = '20'

	elems = doc.getElementsByTagName('footprint_size')
	if len(elems) > 0:
	    for c in elems[0].childNodes:
		if c.nodeType != Node.COMMENT_NODE and len(c.data) > 1:
		    self.footprint_size = (c.data).encode('UTF-8').strip('\n').strip()
        else:
            print "***** warning in file_list.__init__ - missing footprit_size in config file"
            print "      config filename: ", self.config_file_name
            print "      using : ", self.footprint_size
            
	print 'self.footprint_size: ', self.footprint_size

	# default value (1.5)
	self.space_search_factor = '1.5'

	elems = doc.getElementsByTagName('space_search_factor')
	if len(elems) > 0:
	    for c in elems[0].childNodes:
		if c.nodeType != Node.COMMENT_NODE and len(c.data) > 1:
		    self.space_search_factor = (c.data).encode('UTF-8').strip('\n').strip()
        else:
            print "***** warning in file_list.__init__ - missing space_search_factor in config file"
            print "      config filename: ", self.config_file_name
            print "      using : ", self.space_search_factor
            
	print 'self.space_search_factor: ', self.space_search_factor

	# default value (40)
        self.cell_search_limit = '40'

	elems = doc.getElementsByTagName('cell_search_limit')
	if len(elems) > 0:
	    for c in elems[0].childNodes:
		if c.nodeType != Node.COMMENT_NODE and len(c.data) > 1:
		    self.cell_search_limit = (c.data).encode('UTF-8').strip('\n').strip()
        ###else:
            ###print "***** warning in file_list.__init__ - missing cell_search_limit in config file"
            ###print "      config filename: ", self.config_file_name
            ###print "      using : ", self.cell_search_limit
            
	print 'self.cell_search_limit: ', self.cell_search_limit

	# default value (-909090)
	self.invalid_data = '-909090'

	elems = doc.getElementsByTagName('invalid_data')
	if len(elems) > 0:
	    for c in elems[0].childNodes:
		if c.nodeType != Node.COMMENT_NODE and len(c.data) > 1:
		    self.invalid_data = (c.data).encode('UTF-8').strip('\n').strip()
	print 'self.invalid_data: ', self.invalid_data

	# default value ('None')
	self.missing_value = 'None'

	elems = doc.getElementsByTagName('missing_value')
	if len(elems) > 0:
	    for c in elems[0].childNodes:
		if c.nodeType != Node.COMMENT_NODE and len(c.data) > 1:
		    self.missing_value = (c.data).encode('UTF-8').strip('\n').strip()
	print 'self.missing_value: ', self.missing_value

	# default value (1)
	self.num_cores = '1'

	elems = doc.getElementsByTagName('num_cores')
	if len(elems) > 0:
	    for c in elems[0].childNodes:
		if c.nodeType != Node.COMMENT_NODE and len(c.data) > 1:
		    self.num_cores = (c.data).encode('UTF-8').strip('\n').strip()
	print 'self.num_cores: ', self.num_cores

	# default value (1)
	self.proc_size = '1'

	elems = doc.getElementsByTagName('proc_size')
	if len(elems) > 0:
	    for c in elems[0].childNodes:
		if c.nodeType != Node.COMMENT_NODE and len(c.data) > 1:
		    self.proc_size = (c.data).encode('UTF-8').strip('\n').strip()
	print 'self.proc_size: ', self.proc_size


	# set from list, for fast membership check
	self.dirNameSet  = set(self.dirNameList)


    def load_lists(self, list_file):
	try:
	    # try to open list_file for read
	    pkl_file = open(list_file, 'rb')
	    try:
		# de-serialize from list_file
		self.dirNameList = pickle.load(pkl_file)
		self.dirNameSet  = set(self.dirNameList) # need set for fast membership check
		self.startTimeList = pickle.load(pkl_file)
		self.endTimeList = pickle.load(pkl_file)
		#if(list_file.find('cloudsat') >= 0):
		#    self.granuleNumList = pickle.load(pkl_file)
		self.granuleNumList = pickle.load(pkl_file)
	    except EOFError: # error if list_file is empty
                print 'list file not there: %s'%list_file
		pass

	    pkl_file.close()
	except IOError: # error if list_file does not exist
	    raise IOError


    def insert_lists(self, full_file_name, file_name):
        #gblock start_time = UT.get_start_time(full_file_name, file_name)
        #gblock end_time   = UT.get_end_time(full_file_name, file_name)
        start_time = self.dataset_container.get_start_time(file_name)
        end_time = self.dataset_container.get_end_time(file_name)
        
        # Keep inserting start time (in unix time format) into a running list of
        # such start times.  The insertion point into this list determines the insertion
        # point for the other (parallel) lists that support cataloging.  These other
        # lists include a filename lists and lists for start times and end time in
        # datetime format
        itime = UT.datetime_to_unix_time(start_time)
        pos = bisect.bisect(self.uTimeList, itime)
        self.uTimeList.insert(pos, itime)

        # update the list of filenames in the same manner
        self.dirNameList.insert(pos, full_file_name)
        
        # update the list of start times in the same manner
        self.startTimeList.insert(pos, start_time)
        
        # update the list of end time in the same manner
        self.endTimeList.insert(pos, end_time)
        
        #  maintan set for fast membership check
        self.dirNameSet.add(full_file_name)        

        # Cloudsat has one more list
        #print full_file_name
        if(full_file_name.find('cloudsat') >= 0):
            self.granuleNumList.insert(pos, file_name[14:19]) # CloudSat granule number

        if(full_file_name.find('H2O') >= 0):
            self.granuleNumList.insert(pos, file_name[29:37]) # CloudSat granule number


    def dump_lists(self, list_file):
	# create list_file for write
	pkl_file = open(list_file, 'wb')
	pickle.dump(self.dirNameList, pkl_file)
	pickle.dump(self.startTimeList, pkl_file)
	pickle.dump(self.endTimeList, pkl_file)
	#if(list_file.find('cloudsat') >= 0):
	#    pickle.dump(self.granuleNumList, pkl_file)
	pickle.dump(self.granuleNumList, pkl_file)
	pkl_file.close()


    def debug_print(self, list_file):
	self.load_lists(list_file)

	for i in range(len(self.dirNameList)):
	    if(list_file.find('cloudsat') >= 0):
		print self.dirNameList[i], self.startTimeList[i], self.endTimeList[i], self.granuleNumList[i]
	    else:
		print self.dirNameList[i], self.startTimeList[i], self.endTimeList[i]

