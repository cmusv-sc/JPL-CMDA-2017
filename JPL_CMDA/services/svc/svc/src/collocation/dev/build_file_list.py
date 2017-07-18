import os
import sys
import datetime
import pickle
import bisect
import util as UT
import file_list as FL

config_file = ''

if len(sys.argv) == 1 or sys.argv[1] == '-h' or sys.argv[1] == '-help' or sys.argv[1] == '--help':
    print '****** Usage: python ' + sys.argv[0] + ' path_to_config_xml_file'
    sys.exit(2)
else:
    config_file = sys.argv[1]

try:
    afl = FL.file_list(config_file)
except IOError:
    print '****** Usage: python ' + sys.argv[0] + ' path_to_config_xml_file'
    sys.exit(-1)

dset_name = afl.dataset_name
dset_ctr = afl.dataset_container

datarootdir1 = afl.datarootdir
print 'datarootdir1: ', datarootdir1
if os.path.exists(datarootdir1) == False:
    print '****** ', datarootdir1, ' does not exist! Exiting ...'
    sys.exit(-1)

list_file = afl.listdir+'/'+ afl.dataset_name+'_granules.list.pkl'
print 'list_file: ', list_file

# gblock - 3/14/2011 removed incremental feature (screws up if contents in existing list changes)
# load existing lists for incremental build
#try:
#    afl.load_lists(list_file)
#except IOError:
#    print 'List file does not exist yet for read. Will create a new one.'
    

# recursively traverse from datarootdir1 down
for root, subdirs, files in os.walk(datarootdir1):
    for filename in files: # get all "real" files (i.e., non-dirs etc.)        
	#print 'filename: ', filename
        # filter out some names (product dependent)
        #print 'root = ', root
        #print 'dir_filter=', dset_ctr.dir_filter(root), root
        #print 'filename_filter=', dset_ctr.filename_filter(filename), filename
        if dset_ctr.dir_filter(root) and dset_ctr.filename_filter(filename):
            rf = os.path.join(root, filename)
            #print 'rf: ', rf
            # only insert when not yet exist, and maintain a sorted list
            if rf not in afl.dirNameSet:
                #print '----- insert -----: ', rf
                afl.insert_lists(rf, filename)

# serialize the list to list_file
afl.dump_lists(list_file)

# debug print
print 'debug print ...'
afl.debug_print(list_file)

