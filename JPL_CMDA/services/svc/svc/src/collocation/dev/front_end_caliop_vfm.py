import sys
import numpy as N
from hdf_caliop import HdfFile, TAI

class front_end_caliop_vfm(HdfFile):
    """Class implementing Caliop Vertical Feature Mask data parsing."""

    GEOLOC_FIELDS = ('Profile_Time', 'Latitude', 'Longitude')
    
    # Set by _getGeoDict() and required by  _getDataDict()
    sortedArgs = None
    
    def _getGeoDict(self):
        
        # extract geo arrays
        gDict = {'file': self.file}
        for field in self.GEOLOC_FIELDS:            
            ds = self.sd.select(field)
            gDict[field] = N.array(ds.get())
            ds.endaccess()
            
            # One might think of the field as 2D now and you might be right.
            # But technically they are Nx1 which is two dimensions from some
            # perspectives.  Reshape to 1D.
            tShape = gDict[field].shape
            gDict[field] = gDict[field].reshape(tShape[0]*tShape[1])
            
            # We must rearrange all geolocation fields exactly as
            # we do when we sort time.  As a result, the time field
            # must always be encountered first.
            
            # Convert time from TAI time to Unix time, sort and record the sort order
            if field == 'Profile_Time':
                gDict['Time'] = gDict[field] + TAI

                self.sortedArgs = N.argsort(gDict['Time'])
                
                gDict['Time'] = N.take(gDict['Time'], self.sortedArgs)
            # Convert lon to [0,360] and reorder
            elif field == 'Longitude':
                gDict[field] = N.take(gDict[field], self.sortedArgs)               
                # Convert Longitude to range [0, 360]
		### do not convert because CloudSat uses (-180, 180)
                ### gDict[field] = N.where(gDict[field] < 0, gDict[field] + 360, gDict[field])
            # Reorder lat
            elif field == 'Latitude':
                gDict[field] = N.take(gDict[field], self.sortedArgs)
            else:
                print 'Caliop 05km ALayer processing error: no such geolocation field ', field
                sys.exit(-1)

        return gDict
    
    def _getDataDict(self):
        
        # Fields were not selected by Frank as planned as of the date of this
        # writing.  We tried to support just about everything.  Of course the
        # geolocation fields are omitted here as they are supposed to be, but
        # we also omitted the vdata called just 'metadata' (as it appears
        # malformed and pyhdf chokes on it).  It is this pyhdf issue that
        # caused us to choose the way we load the data fields below.  We
        # explicitly specify the desired fields below because using the
        # self.get(None) call instead.
        data_fields = ( 'Day_Night_Flag',
                        'Land_Water_Mask',
                        'Spacecraft_Position',
                        'Feature_Classification_Flags')

        dDict = self.get(data_fields)
        
        # Iterating on something we are changing is not allowed
        # so we make a deep copy
        dDict_out = dDict.copy()
        
        # Sort according to the dimensionality
        for k, v in dDict.iteritems():
            #print
            #print k, ' has ', len(v[0]), ' attributes'

            carray  = N.array(v[1])
            tshape  = carray.shape
            dims    = len(tshape)
            #print k, ' has ', len(tshape), ' dimensions'
            
            # We are going to ignore any data fields that are not listed as
            # two dimensional.  The 2D ones technically includes 1D ones as well
            # as the 2nd dimension is listed as "1" in that case.
            if(dims != 2):
                print 'Skipping field ', k, ' of dimensionality ', dims
                continue
                         
            # Sort any number of columns of the field.  Each column is reordered
            # in a manner identical to every other column.
            dDict_out[k] = (v[0], N.take(dDict[k][1], self.sortedArgs, 0))
            
            #print k, ' attributes = ', dDict_out[k][0]
            #print k, ' size       = ', len(dDict_out[k][1])
            #print k, ' content = '
            #print dDict_out[k][1]

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
    
    def create_catalog(self):

        variableNames = self.dataDict.keys()

        #print variableNames
        
        file = open("caliop_vfm_catalog.txt", 'w')
        line = 'Sensor/Model\tData Product\tVariable Name\tVariable Unit\n'
        file.write(line)
        for i in variableNames:
            attribute = self.dataDict[i][0]
            #print attribute
            line = 'Caliop\tVertical Feature Mask\t%s\t%s\n' %(i, attribute['units'])
            file.write(line)

        file.close()


