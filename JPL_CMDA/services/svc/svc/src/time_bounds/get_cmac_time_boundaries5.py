# From an array of two element arrays,this function returns the smallest
# left hand term and the largest right hand term.	
def max_min(bigarray):
	min = '999999'
	max = '0'
	for array in bigarray:
		if(array[0] < min):
			min = array[0]
			
		if(array[1] > max):
			max = array[1]
				
	return [min, max]
	
# This function examines file "s" for a prefix given by varName, followed by an underscore,
# and an extension of "nc".  The two six digit year/month is extracted from the right end
# of the the file name with a hypen separating the dates.  If the file name is not in the 
# right format then [0. 0]is returned.
def getDates(s, varName):

	# Split off the string to the right of the last period
	# and verify it matches "nc".  If not return [0, 0].
	dot_split = s.split('.')
	#print(len(dot_split))
	if(len(dot_split) > 1):
		if(dot_split[len(dot_split)-1] != 'nc'):
			print("not a .nc file")
			return [0, 0]
		else:
			# If the extension matches,now extract the word before the first underscore
			# and verify it matches the variable name, if not return [0, 0]. 
			underscore_split = dot_split[0].split('_')
			if(len(underscore_split) > 1):
				#print(underscore_split[0], varName)
				if(underscore_split[0] != varName):
					print("no variable name match")
					return [0, 0]
			else:
				# Bad file name.
				print("no underscore present")
				return [0, 0]
				
			return [s[-16:-10], s[-9:-3]]
	else:
		print("not a .nc file")
		return [0, 0]


# Extracts the start and end year/month combinations for 
# possible multiple file for the same source data/variable combination.
# Note that the that setting the useBreakFiles to true will use the containing
# break directory files as required for the 3D case. 		
def getCmacTimeBoundaries(dataSource, varName, useBreakFiles):
	import os
	foundADate = False
	dateList = []
	
	if(useBreakFiles == True):
		subDir = ['/break']
	else:
		subDir = ['']
	
	#print("dataSource = %s varName = %s useBreakFiles = %s" % (dataSource, varName,useBreakFiles))
	dataPath = dataSource.lower()      
	### dataPath1 = '/export/data1/data/cmip5/' + dataPath
        dataPath1 = '/mnt/hgfs/cmacws/data1/data/cmip5/' + dataPath
	if(os.path.exists(dataPath1 + subDir[0])):  
		#print('path exists')
		for dir in subDir:
			#print("***********subDir=  %s" % (dir)) 
			fileList = os.listdir(dataPath1 + dir)
			for fName in fileList:
				#print("current file name= %s" % (fName))
				[date1, date2] = getDates(fName, varName)
				#print(date1, date2)
				#print('\n')
				if(date1 != 0 and date2 != 0):
					foundADate = True
					
					# Found a legitimate date in a file name; so it is returned.
					dateList.append( [date1, date2] )
					#print("dateList= ", dateList) 
					#print("Found one: %s" % (fName))
	else:
		#print("Path does not exist")
		return  [0, 0]
		
	# If search yields no file name, return [0,0]
	if foundADate == False:
		return [0, 0]
	else:
		#print("last dateList: %s" % (dateList))
		x = max_min(dateList)
		return x
		
if __name__ == '__main__':
	sources = ["argo/argo", "cccma/canam4", "cccma/canesm2", "csiro/mk3.6", "gfdl/cm3", "gfdl/cm3_hist", "gfdl/esm2g",
			   "giss/e2-h", "giss/e2-r", "ipsl/cm5a-lr", "miroc/miroc5", "nasa/airs", "nasa/amsre", "nasa/aviso",
			   "nasa/ceres", "nasa/gpcp", "nasa/grace", "nasa/mls", "nasa/modis", "nasa/quikscat", "nasa/trmm",
			   "ncar/cam5", "ncar/cam5-1-fv2", "ncc/noresm", "noaa/nodc", "ukmo/hadgem2-a", "ukmo/hadgem2-es"]
			   
	vars = ["pr", "cli", "clt", "lai", "rlds", "rldscs","rlus", "rlut", "rlutcs", "rsds", "rsdscs", "rsdt", "rsus", "rsuscs",
			"rsut", "rsutcs", "sfcWind", "ts", "uas", "vas", "clw", "hus", "ta", "tos", "zos", "ohc700", "ohc2000", "zo", "zl", "os", "ot"] 
			#["clivi", "clwvi", "z1", "z0", "cltStddev", "cltNobs", "sfcWindNobs", "sfcWindStderr", "uasNobs", "uasStderr", "vasNobs", "vasStderr",
			#"prw"]
        """
	print("start test")
	for source in sources:
		for var in vars:
			retDateList = getCmacTimeBoundaries(source, var, True)
			print(retDateList, source, var)
			print("\n")
	print("===============================================================================")
	print("===============================================================================")
	print("===============================================================================")
	for source in sources:
		for var in vars:
			retDateList = getCmacTimeBoundaries(source, var, False)
			print(retDateList, source, var)
			print("\n")			
	print("end test")
        """

        source = 'cccma/canam4'
        var = 'rlus'

        source = 'argo/argo'
        var = 'os'
        retDateList = getCmacTimeBoundaries(source, var, True)
        print(retDateList, source, var)



