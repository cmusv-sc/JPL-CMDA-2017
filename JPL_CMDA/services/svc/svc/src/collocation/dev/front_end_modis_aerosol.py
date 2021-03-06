import sys
import numpy as N
from hdf import HdfFile, TAI

TOL = 0.1

class front_end_modis_aerosol(HdfFile):
    """Class implementing MODIS Aerosol data parsing."""
    
    GEOLOC_FIELDS = ('Scan_Start_Time', 'Latitude', 'Longitude')
    
    # Set by _getGeoDict() and required by  _getDataDict()
    sortedArgs   = None
    basis_width  = 0
    basis_height = 0
    
    def _getGeoDict(self):
        
        self.includeList = []
        
        #extract geo arrays
        fieldDict = {'file': self.file}
        for field in self.GEOLOC_FIELDS:
            ds = self.sd.select(field)
            fill_value = ds.attributes().get('_FillValue')
            fieldDict[field] = N.array(ds.get())
            ds.endaccess()
            
            # All the MODIS geolocation fields are 2D SDS's.  This makes
            # things fairly simple here.
            
            # The appropriate data in the HDF files are in 2D and
            # we need in 1D.
            tShape = fieldDict[field].shape
            fieldDict[field] = fieldDict[field].reshape(tShape[0]*tShape[1])
        
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
                self.basis_width  = tShape[0];
                self.basis_height = tShape[1];
                
                fieldDict['Time'] = fieldDict[field] + TAI
            elif field == 'Longitude':
                fieldDict[field] = N.take(fieldDict[field], self.includeList)
                fieldDict[field] = N.take(fieldDict[field], self.sortedArgs)
		# do _not_ Convert longitude to range [0, 360]. Make it consistent with CloudSat (-180, 180)
                # fieldDict[field] = N.where(fieldDict[field] < 0, fieldDict[field] + 360, fieldDict[field])
            elif field == 'Latitude':
                fieldDict[field] = N.take(fieldDict[field], self.includeList)
                fieldDict[field] = N.take(fieldDict[field], self.sortedArgs)
            else:
                print 'MODIS processing error: no such geolocation field ', field
                sys.exit(-1)

        return fieldDict
    
    def _getDataDict(self):

        data_fields = ( 'Scattering_Angle',
                        'Optical_Depth_Land_And_Ocean',
                        'Aerosol_Type_Land',
                        'Corrected_Optical_Depth_Land',
                        'Mass_Concentration_Land',
                        'Angstrom_Exponent_Land',
                        'Cloud_Fraction_Land',
                        'STD_Reflectance_Land',
                        'Solution_Index_Ocean_Small',
                        'Solution_Index_Ocean_Large',
                        'Effective_Optical_Depth_Best_Ocean',
                        'Effective_Optical_Depth_Average_Ocean',
                        'Optical_Depth_Small_Best_Ocean',
                        'Optical_Depth_Small_Average_Ocean',
                        'Optical_Depth_Large_Best_Ocean',
                        'Optical_Depth_Large_Average_Ocean',
                        'Mass_Concentration_Ocean',
                        'Effective_Radius_Ocean',
                        'Cloud_Condensation_Nuclei_Ocean',
                        'Asymmetry_Factor_Best_Ocean',
                        'Asymmetry_Factor_Average_Ocean',
                        'Backscattering_Ratio_Average_Ocean',
                        'Angstrom_Exponent_1_Ocean',
                        'Angstrom_Exponent_2_Ocean',
                        'Optical_Depth_Ratio_Small_Ocean_0.55micron',
                        'Cloud_Fraction_Ocean',
                        'STD_Reflectance_Ocean',
                        'Cloud_Mask_QA',
                        'Optical_Depth_Small_Land',
                        'Optical_Depth_Ratio_Small_Land',
                        'Optical_Depth_Ratio_Small_Land_And_Ocean',
                        'Deep_Blue_Aerosol_Optical_Depth_550_Land',
                        'Deep_Blue_Aerosol_Optical_Depth_Land',
                        'Deep_Blue_Angstrom_Exponent_Land',
                        'Deep_Blue_Single_Scattering_Albedo_Land',
                        'Deep_Blue_Surface_Reflectance_Land',
                        'Backscattering_Ratio_Best_Ocean',
                        'Quality_Assurance_Land',
                        'Quality_Assurance_Ocean')
        
        dDict = self.get(data_fields)
        
        # Shallow copy will not suffice as iteration on something we
        # are changing is not allowed.
        dDict_out   = dDict.copy()

        # Process (shape/short) according to the dimensionality
        for k, v in dDict.iteritems():
            #print
            #print k, ' has ', len(v[0]), ' attributes'

            carray   = N.array(v[1])
            tshape  = carray.shape
            dims    = len(tshape)
                
            if((dims < 2) or (dims > 3)):
                print 'Error: invalid dim size for Modis'
                sys.exit(-1);
                
            # See http://modis-atmos.gsfc.nasa.gov/MOD06_L2/grids.html
            if((tshape[0] == 2030) or (tshape[1] == 2030)):
                del dDict_out[k]
#                print 'Skipping 1km resolution data param ', k, '.  Multi-resolution datasets not supported'
                continue
            if((tshape[0] == 2040) or (tshape[1] == 2040)):
                del dDict_out[k]
#                print 'Skipping 1km resolution data param ', k, '.  Multi-resolution datasets not supported'
                continue

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
            elif(dims == 3 and (k == 'Quality_Assurance_Land' or k == 'Quality_Assurance_Ocean')):
                if((tshape[0] != self.basis_width) or (tshape[1] != self.basis_height)):
                    print 'Wrong basis dimensions, looking for ', self.basis_width, ' and ', self.basis_height
                    print '   Deleting param ', k, ': cannot interpret based upon basis dimensions of ', tshape[0], ' and ', tshape[1]
                    del dDict_out[k]
                    continue
                else:
                    dDict_out[k] = (v[0], self.process_3d(k, carray, self.includeList, self.sortedArgs))
            elif(dims == 3):
                if((tshape[1] != self.basis_width) or (tshape[2] != self.basis_height)):
                    print 'Wrong basis dimensions, looking for ', self.basis_width, ' and ', self.basis_height
                    print '   Deleting param ', k, ': cannot interpret based upon basis dimensions of ', tshape[1], ' and ', tshape[2]
                    del dDict_out[k]
                    continue
                else:
                    dDict_out[k] = (v[0], self.process_3d_special(k, carray, self.includeList, self.sortedArgs))
            else:
                print 'MODIS processing error: unanticipated dimensionality for ', k
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

        twoDArray  = data.reshape((threeDShape[0], threeDShape[1]*threeDShape[2]))
        twoDArray  = twoDArray.transpose()
        twoDArray  = N.take(twoDArray, include, 0)
        data       = N.take(twoDArray, order, 0)

        return data

    def create_catalog(self):

        variableNames = self.dataDict.keys()

        #print variableNames
        
        file = open("modis_aerosol_catalog.txt", 'w')
        line = 'Sensor/Model\tData Product\tVariable Name\tVariable Units\n'
        file.write(line)
        for i in variableNames:
            attribute = self.dataDict[i][0]
            #print 'Attribute = ', attribute
            line = 'MODIS\tLevel 2 Aerosol Product\t%s\t%s\n' %(i, attribute['units'])
            file.write(line)

        file.close()


