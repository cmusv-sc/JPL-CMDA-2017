import numpy as N
from hdf import HdfFile, TAI
import util as UT

class front_end_cloudsat(HdfFile):
    """Class implementing CloudSat GEOPROF data parsing."""

    GEOLOC_FIELDS = ('Profile_time', 'UTC_start', 'TAI_start', 'Latitude',
                     'Longitude')

    def _getGeoDict(self):

        #extract geo arrays
        fieldDict = {'file': self.file}
        for field in self.GEOLOC_FIELDS:
            vd = self.vs.attach(field)
            #print dir(vd)
            #print vd.fieldinfo()
            data = N.array(vd[:])
            fieldDict[field] = data.reshape(len(data))
            #print fieldDict[field].shape
            #print fieldDict[field]
            if fieldDict[field].shape == (1,):
                fieldDict[field] = fieldDict[field][0]
            vd.detach()

            #get Unix timestamps and TAI-UTC leap seconds
            if field == 'TAI_start':
                fieldDict['TAI'] = fieldDict[field] + TAI
                fieldDict['UTC'] = int(fieldDict['TAI']/86400)*86400 + \
                                   fieldDict['UTC_start']
                fieldDict['TAI-UTC'] = fieldDict['TAI'] - fieldDict['UTC']
                fieldDict['Profile_UTC'] = fieldDict['Profile_time'] + \
                                           fieldDict['UTC']

	    # adjust longitude to (0, 360) range
	    # do _not_ adjust, leave it as before
	    """
	    if field == 'Longitude':
		for i in range(len(fieldDict['Longitude'])):
		    if fieldDict['Longitude'][i] < 0.0:
			fieldDict['Longitude'][i] += 360.0
	    """


	# Unix Time is TAI+TAI_start+UTC_star+Profile_time, which is fieldDict['Profile_UTC'] here
	fieldDict['Time'] = fieldDict['Profile_UTC']


	if False:
	    num_locs = len(fieldDict['Profile_time'])
	    print 'TAI: ', TAI
	    print 'unix time of CloudSat[0]: ', UT.unix_time_to_date(fieldDict['Time'][0])
	    print 'Profile_UTC of CloudSat[0]: ', UT.unix_time_to_date(fieldDict['Profile_UTC'][0])
	    print 'unix time of CloudSat[1]: ', UT.unix_time_to_date(fieldDict['Time'][1])
	    print 'Profile_UTC of CloudSat[1]: ', UT.unix_time_to_date(fieldDict['Profile_UTC'][1])
	    print 'unix time of CloudSat[',num_locs-2,']: ', UT.unix_time_to_date(fieldDict['Time'][num_locs-2])
	    print 'Profile_UTC of CloudSat[',num_locs-2,']: ', UT.unix_time_to_date(fieldDict['Profile_UTC'][num_locs-2])
	    print 'unix time of CloudSat[',num_locs-1,']: ', UT.unix_time_to_date(fieldDict['Time'][num_locs-1])
	    print 'Profile_UTC of CloudSat[',num_locs-1,']: ', UT.unix_time_to_date(fieldDict['Profile_UTC'][num_locs-1])
	    print 'Time: ', fieldDict['Time']


        return fieldDict

    def get_time(self):
	return self.geoDict['Time']

    def get_latitude(self):
	return self.geoDict['Latitude']

    def get_longitude(self):
	return self.geoDict['Longitude']

    # zzzz
    def create_catalog(self):

        variableNames = self.dataDict.keys()

        #print variableNames
        
        file = open("cloudsat_catalog.txt", 'w')
        line = 'Sensor/Model\tData Product\tVariable Name\n'
        file.write(line)
        for i in variableNames:
            attribute = self.dataDict[i][0]
            #print 'Attribute = ', attribute
            line = 'cloudsat\tLevel 2 Standard Retrieval Product\t%s\n' %(i)
            file.write(line)

        file.close()


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

