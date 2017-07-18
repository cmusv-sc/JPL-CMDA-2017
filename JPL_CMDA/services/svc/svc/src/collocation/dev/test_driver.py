import front_end_cloudsat as FEC
import front_end_airs as FEAIRS
import front_end_amsr as FEA
import middle_end as MD

# The front end reads a CloudSat HDF file and passes the geolocation informaiton
# to the middle end for collocation processing

# CloudSat file name
cs_file = "2007048000847_04291_CS_2B-CWC-RO_GRANULE_P_R04_E02.hdf"
# AIRS file name
airs_file = "AIRS.2008.01.03.001.L2.RetStd.v5.2.2.0.G08064123231.hdf"
# AMSR file name
am_file = "amsre_20070217v5.gz"

# Instantiate a middle end class
midEnd = MD.middle_end()




# Construct AIRS data structure in the front end and read in the data
print "****** Reading AIRS data from file: ", airs_file
ais = FEAIRS.front_end_airs(airs_file)

# Pass the AIRS grid info to the middle end grid data structure
# Get time info as an array
midEnd.set_target_time(ais.get_time())
print 'AIRS UTC Time = ', midEnd.get_target_time()
#print 'AIRS UTC Time Range = ', min(midEnd.get_target_time()), max(midEnd.get_target_time())
print 'AIRS UTC Time Size = ', midEnd.get_target_time().size
print ''

# Get latitude info as an array
midEnd.target_latitude = ais.get_latitude()
print 'AIRS Latitude = ', midEnd.target_latitude
#print 'AIRS Latitude Range = ', min(midEnd.target_latitude), max(midEnd.target_latitude)
print 'AIRS Latitude Size = ', midEnd.target_latitude.size
print ''

# Get longitude info as an array
midEnd.target_longitude = ais.get_longitude()
print 'AIRS Longitude = ', midEnd.target_longitude
#print 'AIRS Longitude Range = ', min(midEnd.target_longitude), max(midEnd.target_longitude)
print 'AIRS Longitude Size = ', midEnd.target_longitude.size

print "****** AIRS data acquired! ******"
print ''
print ''
print ''




# Construct CloudSat data structure in the front end and read in the data
print "****** Reading CloudSat data from file: ", cs_file
cs = FEC.front_end_cloudsat(cs_file)

# Pass the CloudSat grid info to the middle end grid data structure
# Get time info as an array
midEnd.set_target_time(cs.get_time())
print 'CloudSat UTC Time = ', midEnd.get_target_time()
print 'CloudSat UTC Time Range = ', min(midEnd.get_target_time()), max(midEnd.get_target_time())
print 'CloudSat UTC Time Size = ', midEnd.get_target_time().size
print ''

# Get latitude info as an array
midEnd.target_latitude = cs.get_latitude()
print 'CloudSat Latitude = ', midEnd.target_latitude
print 'CloudSat Latitude Range = ', min(midEnd.target_latitude), max(midEnd.target_latitude)
print 'CloudSat Latitude Size = ', midEnd.target_latitude.size
print ''

# Get longitude info as an array
midEnd.target_longitude = cs.get_longitude()
print 'CloudSat Longitude = ', midEnd.target_longitude
print 'CloudSat Longitude Range = ', min(midEnd.target_longitude), max(midEnd.target_longitude)
print 'CloudSat Longitude Size = ', midEnd.target_longitude.size

print "****** CloudSat data acquired! ******"
print ''
print ''
print ''




# Read AMSR instrument data
print "****** Reading AMSR data from file: ", am_file
ams = FEA.front_end_amsr(am_file)
midEnd.set_src_time(ams.get_time())
print 'AMSR Time size = ', midEnd.get_src_time().size
print 'AMSR Time = ', midEnd.get_src_time()

##### TBD: src grid SST data reside in front_end_amsr, pointed by middle_end src_data
##### target grid SST data reside in back_end_amsr, pointed by middle_end target_data
midEnd.set_src_data(ams.get_sst())
print 'AMSR SST size = ', midEnd.get_src_data().size
print 'AMSR SST = ', midEnd.get_src_data()
##### TBD: Now "allocate memory" in back_end_amsr to hold target grid SST
##### (a dictionary of SST, WSPD, ... arrays)
##### Point middle_end target_data to this memory
##### collocate SST data right here
##### now we can use the middle_end pointers src_data and target_data
##### for WSPD, VAPOR, etc. in a loop, and call collocation method

midEnd.set_src_data(ams.get_wspd())
print 'AMSR WSPD size = ', midEnd.get_src_data().size
print 'AMSR WSPD = ', midEnd.get_src_data()

midEnd.set_src_data(ams.get_vapor())
print 'AMSR VAPOR size = ', midEnd.get_src_data().size
print 'AMSR VAPOR = ', midEnd.get_src_data()

midEnd.set_src_data(ams.get_cloud())
print 'AMSR CLOUD size = ', midEnd.get_src_data().size
print 'AMSR CLOUD = ', midEnd.get_src_data()

midEnd.set_src_data(ams.get_rain())
print 'AMSR RAIN size = ', midEnd.get_src_data().size
print 'AMSR RAIN = ', midEnd.get_src_data()

print "****** AMSR data acquired! ******"

# Call middle end collocation method to generate target values

