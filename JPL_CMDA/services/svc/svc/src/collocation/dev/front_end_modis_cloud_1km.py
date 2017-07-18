import sys
import numpy as N
from hdf import HdfFile, TAI
import geomap_5kmto1km as GEOMAP
import time
import datetime

TOL = 0.1

class front_end_modis_cloud_1km(HdfFile):
    """Class implementing MODIS Cloud data parsing."""
    
    GEOLOC_FIELDS = ('Scan_Start_Time', 'Latitude', 'Longitude')
    
    # Set by _getGeoDict() and required by  _getDataDict()
    sortedArgs   = None
    includeList  = []
    basis_width  = 0
    basis_height = 0
    
    def _getGeoDict(self):
        
        self.includeList = []
                
        # Reconstruct 1km resolution geolocation parameters from 5km ones
        time5km = N.array(self.sd.select('Scan_Start_Time').get())
        lat5km  = N.array(self.sd.select('Latitude').get())
        lon5km  = N.array(self.sd.select('Longitude').get())
        [time1km, lat1km, lon1km] = self.reconstruct1km(time5km, lat5km, lon5km)
        
        # This is for evaluating whether the mapping from 5km to 1km was done right
#        print 'in lat  = ', lat5km[0][0], lat5km[0][1], lat5km[1][0], lat5km[1][1]
#        print 'in lon  = ', lon5km[0][0], lon5km[0][1], lon5km[1][0], lon5km[1][1]
#        print 'in time = ', time5km[0][0], time5km[0][1], time5km[1][0], time5km[1][1]
#        print
#        
#        i = 0
#        for j in range(0, 5):
#            print 'out lat line   = ', lat1km[j][i + 0], lat1km[j][i + 1], lat1km[j][i + 2], lat1km[j][i + 3], lat1km[j][i + 4]
#        print
#        i = 0
#        for j in range(0, 5):
#            print 'out lon line   = ', lon1km[j][i + 0], lon1km[j][i + 1], lon1km[j][i + 2], lon1km[j][i + 3], lon1km[j][i + 4]
#        print
#        i = 0
#        for j in range(0, 5):
#            print 'out time line  = ', time1km[j][i + 0], time1km[j][i + 1], time1km[j][i + 2], time1km[j][i + 3], time1km[j][i + 4]
        ###############################################################################
        
        
        # Process geo arrays
        fieldDict = {'file': self.file}
        for field in self.GEOLOC_FIELDS:
            ds = self.sd.select(field)
            fill_value = ds.attributes().get('_FillValue')
            fieldDict[field] = N.array(ds.get())
            ds.endaccess()
            
            if field == 'Scan_Start_Time':
                fieldDict[field] = N.array(time1km.reshape(time1km.shape[0]*time1km.shape[1]))
            elif field == 'Longitude':
                fieldDict[field] = N.array(lon1km.reshape(lon1km.shape[0]*lon1km.shape[1]))
            elif field == 'Latitude':
                fieldDict[field] = N.array(lat1km.reshape(lat1km.shape[0]*lat1km.shape[1]))

            # print field, ' has shape ', fieldDict[field].shape
                        
            # Convert time to Unix time
            if field == 'Scan_Start_Time':
                # Filter out any flag values entries in geolocation fields.
                # These had better occur in parallel location across these
                # fields (and it appears they do).  This impacts the data
                # field values used via the impact on 'sortedArgs'
                for i in range(0, fieldDict[field].shape[0]):
                    if abs(fieldDict[field][i] - fill_value) > TOL:
                        self.includeList.append(i)
                fieldDict[field] = N.take(fieldDict[field], self.includeList)
    
                # We must rearrange all geolocation fields exactly as
                # we do when we sort time.  Get the new order and reorder.
                self.sortedArgs = N.argsort(fieldDict[field])
                fieldDict[field] = N.take(fieldDict[field], self.sortedArgs)
                #print "Reshaped and Reordered: ", field
                
                #  We process data fields in a manner dependant upon the width and
                #  height of the time field.  For MODIS, the size of the time field
                #  varies.  It is different in each file.  These vars hold the
                #  size of the time field.
                self.basis_width  = time1km.shape[0];
                self.basis_height = time1km.shape[1];
                
                fieldDict['Time'] = fieldDict[field] + TAI
            elif field == 'Longitude':
                fieldDict[field] = N.take(fieldDict[field], self.includeList)
                fieldDict[field] = N.take(fieldDict[field], self.sortedArgs)
            elif field == 'Latitude':
                fieldDict[field] = N.take(fieldDict[field], self.includeList)
                fieldDict[field] = N.take(fieldDict[field], self.sortedArgs)
            else:
                print 'MODIS processing error: no such geolocation field ', field
                sys.exit(-1)

        return fieldDict
    
    def _getDataDict(self):

	start = datetime.datetime.now()

        data_fields = ( 'Cloud_Effective_Radius',
                        'Cloud_Optical_Thickness',
                        'Cloud_Effective_Radius_1621',
                        'Cloud_Optical_Thickness_1621',
                        'Effective_Radius_Difference',
                        'Cloud_Water_Path',
                        'Cloud_Water_Path_1621',
                        'Cloud_Effective_Radius_Uncertainty',
                        'Cloud_Optical_Thickness_Uncertainty',
                        'Cloud_Water_Path_Uncertainty',
                        'Cloud_Effective_Radius_Uncertainty_1621',
                        'Cloud_Optical_Thickness_Uncertainty_1621',
                        'Cloud_Water_Path_Uncertainty_1621',
                        'Cloud_Phase_Optical_Properties',
                        'Cloud_Multi_Layer_Flag',
                        'Cirrus_Reflectance',
                        'Cirrus_Reflectance_Flag',
                        'Cloud_Mask_1km',
                        'Quality_Assurance_1km')
        
        dDict = self.get(data_fields)
        
        # Shallow copy will not suffice as iteration on something we
        # are changing is not allowed.
        dDict_out   = dDict.copy()

        # Process (shape/short) according to the dimensionality
        for k, v in dDict.iteritems():
            #print
            #print k, ' has ', len(v[0]), ' attributes'

            carray   = N.array(v[1])

            #  Strip 4 useless columns from the data. Makes it match geolocation
            #  param sizes.  This is a side effect of the reconstruction of the
            #  1km colocation params from the 5km ones.
            dims = len(carray.shape)
            if(dims == 2):           
               carray = carray[0:carray.shape[0],0:carray.shape[1]-4]     
            elif(dims == 3 and k == 'Effective_Radius_Difference'):  # This param has a one-off shape to account for
               carray = carray[0:carray.shape[0],0:carray.shape[1],0:carray.shape[2]-4]
            elif(dims == 3):
               carray = carray[0:carray.shape[0],0:carray.shape[1]-4,0:carray.shape[2]]
            else:
                print 'Error: invalid dim size for Modis Cloud 1km'
                sys.exit(-1);
                
            tshape  = carray.shape

            #  We are going to ignore any data whose last two dimensions are
            #  not the same as the basis dimensions
            if(dims == 2):
                if((tshape[0] != self.basis_width) or (tshape[1] != self.basis_height)):
                    print 'Wrong basis dimensions, looking for ', self.basis_width, ' and ', self.basis_height
                    print '   Deleting param ', k, ': cannot interpret based upon basis dimensions of ', tshape[0], ' and ', tshape[1]
                    del dDict_out[k]
                    continue
                else:
                    dDict_out[k] = (v[0], self.process_2d(k, carray, self.includeList, self.sortedArgs)) 
            elif(dims == 3 and k == 'Effective_Radius_Difference'):
                if((tshape[1] != self.basis_width) or (tshape[2] != self.basis_height)):
                    print 'Wrong basis dimensions, looking for ', self.basis_width, ' and ', self.basis_height
                    print '   Deleting param ', k, ': cannot interpret based upon basis dimensions of ', tshape[1], ' and ', tshape[2]
                    del dDict_out[k]
                    continue
                else:
                    dDict_out[k] = (v[0], self.process_3d_special(k, carray, self.includeList, self.sortedArgs))
            elif(dims == 3):
                if((tshape[0] != self.basis_width) or (tshape[1] != self.basis_height)):
                    print 'Wrong basis dimensions, looking for ', self.basis_width, ' and ', self.basis_height
                    print '   Deleting param ', k, ': cannot interpret based upon basis dimensions of ', tshape[0], ' and ', tshape[1]
                    del dDict_out[k]
                    continue
                else:
                    dDict_out[k] = (v[0], self.process_3d(k, carray, self.includeList, self.sortedArgs))
            else:
                print 'MODIS processing error: unanticipated dimensionality for ', k
                sys.exit(-1)
                    
	now = datetime.datetime.now()
	elapsed_time = now - start
	print '*** _getDataDict elapsed time: ', elapsed_time.days, ' days, ', elapsed_time.seconds, ' seconds'

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

    # Reshape, sort 2d data
    def process_2d(self, name, data, include, order):
        #print 'Processing 2d ', name
        
         # Reshape to 2D->1D and sort as dictated by 'order'
        twoDShape = data.shape
        oneDArray = data.reshape(twoDShape[0]*twoDShape[1])
        oneDArray = N.take(oneDArray, include, 0)
        data      = N.take(oneDArray, order, 0)
        
        return data
    
    # Reshape, sort 3d data
    def process_3d(self, name, data, include, order):
        #print 'Processing 3d ', name
        
        # Reshape 3D->2D and sort along one axis as dictated by 'order'
        threeDShape = data.shape

        twoDArray  = data.reshape((threeDShape[0]*threeDShape[1], threeDShape[2]))
        twoDArray  = N.take(twoDArray, include, 0)
        data       = N.take(twoDArray, order, 0)

        return data
    
    # Reshape, sort 3d data
    def process_3d_special(self, name, data, include, order):
        #print 'Processing 3d ', name
        
        # Reshape 3D->2D and sort along one axis as dictated by 'order'
        threeDShape = data.shape

        # There appears to be an assumption in the middle end regarding which
        # dimensions do or do not get combined.  As the ordering of some dimensions
        # in MODIS are inconsistent with those assumptions, a side effect of this
        # is that we cannot simply reshape as shown on the reshape line below.
        # We must reshape and then transpose such that 1) The above-mentioned
        # middle end assumption is satisfied and 2) data ordering is modified
        # to match that assumption.
          
        twoDArray  = data.reshape((threeDShape[0], threeDShape[1]*threeDShape[2]))
        twoDArray  = twoDArray.transpose()
        twoDArray  = N.take(twoDArray, include, 0)
        data       = N.take(twoDArray, order, 0)

        return data
    
    def create_catalog(self):

        variableNames = self.dataDict.keys()

        #print variableNames
        
        file = open("modis_cloud_1km_catalog.txt", 'w')
        line = 'Sensor/Model\tData Product\tVariable Name\tVariable Units\n'
        file.write(line)
        for i in variableNames:
            attribute = self.dataDict[i][0]
            #print 'Attribute = ', attribute
            line = 'MODIS\tLevel 2 1km Cloud Product\t%s\t%s\n' %(i, attribute['units'])
            file.write(line)

        file.close()
        
    def reconstruct1km(self, intime, lat, lon):
        
        # Should check that all 3 inputs have same dimensions here.
        # If not, that would be an error
        
        latmap = GEOMAP.geomap(lat.shape[0],lat.shape[1],lat.shape[0]*5+1,lat.shape[1]*5+1)
        newlat = latmap.geomap_5kmto1km(lat)
        
        lonmap = GEOMAP.geomap(lon.shape[0],lon.shape[1],lon.shape[0]*5+1,lon.shape[1]*5+1)
        newlon = lonmap.geomap_5kmto1km(lon)
        
        newtime = self.reconstruct1km_time(intime)
        
        return [newtime, newlat, newlon]

    def reconstruct1km_time(self, intime):
        
        newtime = N.zeros([intime.shape[0] * 5,intime.shape[1] * 5])
        
        in_shape  = intime.shape

        # Each 5km pixel just gives rise to 5x5 1km pixels
        for i in range(0, in_shape[1]):
            for j in range(0, in_shape[0]):
                 for k in range(0, 5):
                    for l in range(0, 5):                        
                        newtime[j * 5 + l][i * 5 + k] = intime[j][i]
         
        return newtime

