import sys
import numpy as N
from hdf5 import Hdf5File, TAI

INVALID_VALUE_FLAG = -999.99
TOL = 0.1

class front_end_mls_temp(Hdf5File):
    """Class implementing MLS Temperature data parsing."""
    
    GEOLOC_FIELDS = ('Time',
                     'Latitude',
                     'Longitude',
                     'Pressure' )
    
    # Set by _getGeoDict() and required by  _getDataDict()
    sortedArgs  = None
    
    def _getGeoDict(self):

        gDict = {'file': self.file}        
        for field in self.GEOLOC_FIELDS:
            
            datafield = self.findObject(self.hdf, field)
            
            if datafield == None:
                print 'Error: Could not find ', field
                sys.exit(-1)

            # Get the datafield's data into a numpy array
            carray = N.zeros(datafield.shape)
            datafield.read_direct(carray)
            gDict[field] = N.array(carray)

            # Map the colocation fields.  This requires the time field to be
            # first as the sort order derived from the time is required for
            # all other fields
            if field == 'Time':

                # Find the indexes of the time values that we will need to properly
                # rearrange time values in increasing order.  These indexes must not
                # select any items any that an invalid value flag values (i.e. "-999.99").
                # Such a list allows us to select items properly from all geolocation
                # fields as well as all data fields.
                
                # Filter out time elements with the 'invalid value' flag value (-999.99).
                # As this impacts the 'sortedArgs' list, the filtering of flag values for
                # all other geolocation params and all data params is automatic from this
                # point forward.  This assumes the pattern of flag values is consistent
                # across geolocation params and data params.  This is the case re MLS.
                includeList = []
                for i in range(0, gDict[field].shape[0]):
                    ### if gDict[field][i] > -999.9 or gDict[field][i] < -1000:
                    if abs(gDict[field][i] - INVALID_VALUE_FLAG) > TOL:
                        includeList.append(i)
                gDict[field] = N.take(gDict[field], includeList)
                
                # Get sort order for time
                self.sortedArgs = N.argsort(gDict[field])
                
                # Reorder time
                gDict[field] = N.take(gDict[field], self.sortedArgs)
                     
                # Convert from TAI time to UNIX time
                gDict[field] = gDict[field] + TAI
                   
            elif field == 'Latitude':
                # Reorder
                gDict[field] = N.take(gDict[field], self.sortedArgs)
                
            elif field == 'Longitude':
                # Reorder
                gDict[field] = N.take(gDict[field], self.sortedArgs)
		# convert longitude from (0, 360) to (-180, 180), consistent with CloudSat
		gDict[field] = N.where(gDict[field]>180.0, gDict[field]-360.0, gDict[field])

            elif field == 'Pressure':
                self.levels = {}
                attribute = {}
                attribute['units']="hPa"
                attribute['dimension1']="pressure"
                self.levels[field] = (attribute, N.array(gDict[field]))

            else:
                print 'MLS processing error: no such geolocation field ', field
                sys.exit(-1)
                
            #print field, ': LENGTH = ',gDict[field].shape[0]

        return gDict
    
    def _getDataDict(self):

        data_fields = ( 'Temperature',
                        'TemperaturePrecision',
                        'Convergence',
                        ### 'L2gpPrecision',
                        ### 'L2gpValue',
                        'Quality',
                        'Status')
        
        dDict = self.get(data_fields)
        
        # Reorder each data field as we reordered time (this includes
        # omitting flag values items via 'sortedArgs')
        for k, v in dDict.iteritems():
            carray = N.array(v[1])
            tshape = carray.shape
            dims  = len(tshape)
            
            #print k, ': LENGTH = ',tshape[0]
            
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
           if (i == 'Temperature' or i == 'TemperaturePrecision'):
                attribute = dDict[i][0]
                attribute['dimension1']='pressure'
                data = dDict[i][1]
                dDict[i] = (attribute, data)

    def get_time(self):
        return self.geoDict['Time']

    def get_latitude(self):
        return self.geoDict['Latitude']
    
    def get_longitude(self):
        return self.geoDict['Longitude']
    
    def get_levels(self):
        return self.levels

    def get_data(self):
        return self.dataDict
    
    def create_catalog(self):

        variableNames = self.dataDict.keys()

        #print variableNames
        
        file = open("mls_temperature_catalog.txt", 'w')
        line = 'Sensor/Model\tData Product\tVariable Name\tVariable Unit\n'
        file.write(line)
        for i in variableNames:
            attribute = self.dataDict[i][0]
            #print attribute
            line = 'MLS\tTemperature\t%s\t%s\n' %(i, attribute['Units'])
            file.write(line)

        file.close()


