import sys
import numpy as N
from hdf import HdfFile, TAI

class front_end_ceres(HdfFile):
    """Class implementing Ceres L2 SSF (FM3) data parsing."""
    
    GEOLOC_FIELDS = ('Time of observation',
                     'Colatitude of CERES FOV at surface',
                     'Longitude of CERES FOV at surface')
    
    # Set by _getGeoDict() and required by  _getDataDict()
    sortedArgs = None

    def _getGeoDict(self):

        gDict = {'file': self.file}        
        for field in self.GEOLOC_FIELDS:
#            print "field:", field
            ds = self.sd.select(field)
            #print "attributes:", ds.attributes()
            #print "info:", ds.info()
            gDict[field] = N.array(ds.get())
            #print "shape:", gDict[field].shape
            #print gDict[field]
            ds.endaccess()
                        
            # Map the colocation fields.  This requires the time field to be
            # first as the sort order derived from the time is required for
            # all other fields
            if field == 'Time of observation': 
                # Get sort order for time.  This applies to all the other
                # fields (colocation and data fields) that come later as well.
                self.sortedArgs = N.argsort(gDict['Time of observation'])
                
                #print 'point1: self.sortedArgs = ', self.sortedArgs
                
                # Reorder time
                gDict[field] = N.take(gDict[field], self.sortedArgs)
                     
                # Convert Julian date to unix time
                # Unix time = (julian day -julian day unix epoch zero point) * number of seconds in a day
                gDict['Time'] = (gDict[field] - 2440587.5) * 86400.0

                #print "Julian Date: ", gDict[field][0]
                #print "Unix Time: ",   gDict['Time'][0]   
                                
            # Get the latitude information we have (colatitude) into the latitude
            # representation we need.
            elif field == 'Colatitude of CERES FOV at surface':
                # Reorder
                gDict[field] = N.take(gDict[field], self.sortedArgs)

                gDict['Latitude'] = 90 - gDict[field]
                
            elif field == 'Longitude of CERES FOV at surface':
                # Reorder
                gDict[field] = N.take(gDict[field], self.sortedArgs)
                
		# convert lon to (-180, 180), consistent with CloudSat
                gDict['Longitude'] = N.where(gDict[field] > 180, gDict[field] - 360, gDict[field])
                
            else:
                print 'CERES processing error: no such geolocation field ', field
                sys.exit(-1)

        return gDict
    
    def _getDataDict(self):

        # Fields selected by Duane Waliser July 27, 2009.  Three of which were
        # omitted as the CERES subsetting interface did not support them.
        data_fields = ( 'CERES viewing zenith at surface',
                        'CERES solar zenith at surface',
                        'CERES relative azimuth at surface',
                        'CERES viewing azimuth at surface wrt North',
                        'Altitude of surface above sea level',
                        'Surface type index',
                        'Surface type percent coverage',
                        'CERES SW ADM type for inversion process',
                        'CERES LW ADM type for inversion process',
                        'CERES TOT filtered radiance - upwards',
                        'CERES SW filtered radiance - upwards',
                        'CERES WN filtered radiance - upwards',
                        'Radiance and Mode flags',
                        'CERES SW radiance - upwards',
                        'CERES LW radiance - upwards',
                        'CERES WN radiance - upwards',
                        'CERES SW TOA flux - upwards',
                        'CERES LW TOA flux - upwards',
                        'CERES WN TOA flux - upwards',
                        'CERES downward SW surface flux - Model A',
                        'CERES downward LW surface flux - Model A',
                        'CERES downward WN surface flux - Model A',
                        'CERES net SW surface flux - Model A',
                        'CERES net LW surface flux - Model A',
                        'CERES downward SW surface flux - Model B',
                        'CERES downward LW surface flux - Model B',
                        'CERES net SW surface flux - Model B',
                        'CERES net LW surface flux - Model B',
                        'CERES broadband surface albedo',
                        'CERES LW surface emissivity',
                        'CERES WN surface emissivity')
        
        # Need to reconsider 'surface type*' params above as these are 2D
        # Look at these closely.
        
        dDict = self.get(data_fields)
        
        # Reorder each data field as we reordered time
        for k, v in dDict.iteritems():
		carray = N.array(v[1])
		tshape = carray.shape
		dims  = len(tshape)
            
		# Make 1D and 2D fields, should be all of them
		if(dims == 1) or (dims == 2):
			dDict[k] = (v[0], N.take(carray, self.sortedArgs, 0))
		else:
			print 'Error: skipping unanticipated field ', k

        self.create_dimension_name(dDict)

        return dDict

    def create_dimension_name(self, dDict):
        variableNames = dDict.keys()
        for i in variableNames:       
          if (i == 'Surface type index' or i == 'Surface type percent coverage'):
             attribute = dDict[i][0]
             attribute['dimension1']='surface_type'
             second_item = dDict[i][1]
             dDict[i]=(attribute, second_item)

    def get_time(self):
        return self.geoDict['Time']

    def get_latitude(self):
        return self.geoDict['Latitude']
    
    def get_longitude(self):
        return self.geoDict['Longitude']

    def get_data(self):
        return self.dataDict
    
    def get_levels(self):
        return self.levels
    
    def create_catalog(self):

        variableNames = self.dataDict.keys()

        #print variableNames
        
        file = open("ceres_catalog.txt", 'w')
        line = 'Sensor/Model\tData Product\tVariable Name\tVariable Unit\n'
        file.write(line)
        for i in variableNames:
            attribute = self.dataDict[i][0]
            #print attribute
            line = 'CERES FM3\tLevel 2 SSF\t%s\t%s\n' %(i, attribute['units'])
            file.write(line)

        file.close()


