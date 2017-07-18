import sys
import numpy as N
from hdf import HdfFile, TAI

class front_end_airs(HdfFile):
    """Class implementing AIRS StdRet data parsing."""
    
    GEOLOC_FIELDS = ('Time', 'Latitude', 'Longitude')
    
    def _getGeoDict(self):
        
        #extract geo arrays
        fieldDict = {'file': self.file}
        for field in self.GEOLOC_FIELDS:
            ds = self.sd.select(field)
            #print "attributes:", ds.attributes()
            #print "info:", ds.info()
            fieldDict[field] = N.array(ds.get())
            #print "shape:", fieldDict[field].shape
            #print fieldDict[field]
            ds.endaccess()
            
            # All the AIRS geolocation fields are 2D SDS's.  This makes
            # things fairly simple here.
            
            # The appropriate data in the HDF files are in 2D and
            # we need in 1D.  Reshape all 2D fields, skipping the rest.
            tShape = fieldDict[field].shape
            fieldDict[field] = fieldDict[field].reshape(tShape[0]*tShape[1])

            # We must rearrange all geolocation fields exactly as
            # we do when we sort time.  Get the new order and reorder.
            sortedArgs = N.argsort(fieldDict['Time'])
            fieldDict[field] = N.take(fieldDict[field], sortedArgs)
            #print "Reshaped and Reordered: ", field
            
            # Convert time to Unix time
            if field == 'Time':
                fieldDict[field] = fieldDict[field] + TAI
            elif field == 'Longitude':
		# do _not_ Convert longitude to range [0, 360]. Make it consistent with CloudSat (-180, 180)
                ### fieldDict[field] = N.where(fieldDict[field] < 0, fieldDict[field] + 360, fieldDict[field])
                fieldDict[field] = fieldDict[field]
            elif field == 'Latitude':
                fieldDict[field] = fieldDict[field]
            else:
                print 'AIRS processing error: no such geolocation field ', field
                sys.exit(-1)

        return fieldDict
    
    def _getDataDict(self):
        
        # Fields selected by Eric Fetzer August 10, 2009.  "match everything
        # in the AIRS Level 2 Standard Products".  This is what get(None) does
        # except you have to subtract out.  From that we have to delete
        # the geolocation fields.  We also have to delete data params where there
        # dimensions 1 and 2 are not exactly 45 and 30 respectively.

        dDict = self.get(None)
        
        # Pull out time and reshape and sort to get indexes that will
        # be needed to rearrange other data of varying dimensionality.
        # also pull out pressure arrays and store them in self.levels 
        self.levels = {}
        for k, v in dDict.iteritems():
            if k == 'Time':
                tarray = N.array(v[1])
                # we need in 1D
                tShape = tarray.shape
                tarray = tarray.reshape(tShape[0]*tShape[1])
                # We must rearrange all geolocation fields exactly as
                # we do when we sort time.  Get the new order and reorder.
                sortedArgs = N.argsort(tarray)
                #print 'Determined sort order for data fields'
                #print 'sorted args = ', sortedArgs
            elif k == 'pressStd':
                attribute = {}
                attribute['units']="mb"
                self.levels[k]=( attribute, N.array(v[1]) )
            elif k == 'pressH2O':
                attribute = {}
                attribute['units']="mb"
                self.levels[k]=( attribute, N.array(v[1]) )
              
        
        # Delete Geolocation params from the data dictionary we are building
        # as it is a 'data' dictionary
        del dDict['Time']
        del dDict['Latitude']
        del dDict['Longitude']
        
        # Shallow copy will not suffice as iteration on something we
        # are changing is not allowed.
        dDict_out = dDict.copy()

        # Process (shape/short) according to the dimensionality
        for k, v in dDict.iteritems():
            #print
            #print k, ' has ', len(v[0]), ' attributes'

            carray   = N.array(v[1])
            tshape  = carray.shape
            dims    = len(tshape)
            #print k, ' has ', len(tshape), ' dimensions'
            
            #  We are going to ignore any data whose first two dimensions are
            #  not 45 and 30
            if((dims < 2) or (tshape[0] != 45) or (tshape[1] != 30)):
                del dDict_out[k]
                continue;
            
            if dims == 2:
                dDict_out[k] = (v[0], self.process_2d(k, carray, sortedArgs))
            elif dims == 3:
                dDict_out[k] = (v[0], self.process_3d(k, carray, sortedArgs))
            elif dims == 4:
                dDict_out[k] = (v[0], self.process_4d(k, carray, sortedArgs))
            elif dims == 5:
                dDict_out[k] = (v[0], self.process_5d(k, carray, sortedArgs))
            else:
                print 'AIRS processing error: unanticipated dimensionality for ', k
                sys.exit(-1)
                    
        return dDict_out

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

    # The following process_[2-5]d methods could probably be generalized into one

    # Reshape, sort 2d data
    def process_2d(self, name, data, order):
        #print 'Processing 2d ', name
        
         # Reshape to 2D->1D and sort as dictated by 'order'
        twoDShape = data.shape
        oneDArray = data.reshape(twoDShape[0]*twoDShape[1])
        data = N.take(oneDArray, order, 0)
        
        return data
    
    # Reshape, sort 3d data
    def process_3d(self, name, data, order):
        #print 'Processing 3d ', name
        
        # Reshape 3D->2D and sort along one axis as dictated by 'order'
        threeDShape = data.shape
        twoDArray = data.reshape((threeDShape[0]*threeDShape[1], threeDShape[2]));
        data = N.take(twoDArray, order, 0)
        
        return data
    
    # Reshape, sort 4d data
    def process_4d(self, name, data, order):
        #print 'Processing 4d ', name
        
        # Reshape 4D->3D and sort along one axis as dictated by 'order'
        fourDShape = data.shape
        threeDArray = data.reshape((fourDShape[0]*fourDShape[1], fourDShape[2], fourDShape[3]))
        data = N.take(threeDArray, order, 0)
        return data
    
    # Reshape, sort 5d data
    def process_5d(self, name, data, order):
        #print 'Processing 5d ', name
        
        # Reshape 4D->3D and sort along one axis as dictated by 'order'
        fiveDShape = data.shape
        fourDArray = data.reshape((fiveDShape[0]*fiveDShape[1], fiveDShape[2], fiveDShape[3], fiveDShape[4]))
        data = N.take(fourDArray, order, 0)
        return data

    def create_catalog(self):

        variableNames = self.dataDict.keys()

        #print variableNames
        
        file = open("airs_catalog.txt", 'w')
        line = 'Sensor/Model\tData Product\tVariable Name\n'
        file.write(line)
        for i in variableNames:
            attribute = self.dataDict[i][0]
            #print 'Attribute = ', attribute
            line = 'AIRS\tLevel 2 Standard Retrieval Product\t%s\n' %(i)
            file.write(line)

        file.close()


