import sys
import os
import os.path
import zipfile
import subprocess
import string

# python version is {mv}.{v}
# example: 2.6, mv==2, v==6
mv = int(sys.version[0])
v = int(sys.version[2])

print 'python version: ', mv, v

use_process = 1

# python 3.x or higher, assumed to have ZipFile.extract()
if mv >= 3:
    use_process = 0
# python 2.x
elif mv == 2:
    # python 2.6 or higher has ZipFile.extract()
    if v >= 6:
        use_process = 0

print 'use_process: ', use_process

# recursively traverse from here down
for root, subdirs, files in os.walk('.'):
    for filename in files: # get all "real" files (i.e., non-dirs etc.)
	zf = os.path.join(root, filename)
	l1 = len(filename)
	f1 = filename[0:l1-4]
	f2 = os.path.join(root, f1)
	### print '----- filename: ', filename, ',  f1: ', f2
	# if zf is zip and if it hasn't been unzipped
        if zipfile.is_zipfile(zf) is True and os.path.exists(f2) is False:
            # unzip the file zf
	    if use_process == 0:
		zipf = zipfile.ZipFile(zf)
		list1 = zipf.namelist()
		for e in list1:
		    print '----- unzipping: ', zf, ' to get: ', e
		    zipf.extract(e, root)
	    else:
		command = '/usr/bin/unzip ' + filename
		cmd = command.split(' ')
		cmdstring = string.join(cmd, ' ')
		### print 'cmdstring: ', cmdstring
		print '----- unzipping: ', zf
		proc=subprocess.Popen(cmd, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout_value, stderr_value = proc.communicate()
		### print 'stdout_value: ', stdout_value
		### print 'stderr_value: ', stderr_value



