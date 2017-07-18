import sys
import numpy as N
from hdf_caliop import HdfFile, TAI

class front_end_caliop_05km_clay(HdfFile):
    """Class implementing Caliop 05km Cloud Layer data parsing."""

    GEOLOC_FIELDS = ('Profile_Time', 'Latitude', 'Longitude')
    
    # Set by _getGeoDict() and required by  _getDataDict()
    sortedArgs = None
    
    def _getGeoDict(self):
        
        # extract geo arrays
        gDict = {'file': self.file}
        for field in self.GEOLOC_FIELDS:            
            ds = self.sd.select(field)
            #print "attributes:", ds.attributes()
            #print "info:", ds.info()
            gDict[field] = N.array(ds.get())
            #print "shape:", fieldDict[field].shape
            #print fieldDict[field]
            ds.endaccess()
            
            # For Caliop 05km products, the geolocation fields have 3 cols.
            # This is a result of averaging.  Each 15 pulses from the instrument
            # are averaged and the geolocation fields provide information for the
            # 1st, 8th and 15th pulses.  These are cols 0, 2 and 1 respectively.
            # We stick with the middleth pulse (column 2) in our use of these
            # geolocation fields.
            
            size = gDict[field].size / 3
            gDict[field] = gDict[field][0:size, 2:3]  # All of column 2
            
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
            # Convert lon to [0,360] and reorder <-------- do not do it now
            elif field == 'Longitude':
                gDict[field] = N.take(gDict[field], self.sortedArgs)               
                # Convert Longitude to range [0, 360]
		### do not convert to (0, 360) as CloudSat is using (-180, 180)
                ### gDict[field] = N.where(gDict[field] < 0, gDict[field] + 360, gDict[field])
            # Reorder lat
            elif field == 'Latitude':
                gDict[field] = N.take(gDict[field], self.sortedArgs)
            else:
                print 'Caliop 05km CLayer processing error: no such geolocation field ', field
                sys.exit(-1)

        return gDict
    
    def _getDataDict(self):
        
        # Fields were not selected by Frank as planned as of the date of this
        # writing.  We tried to support just about everything.  Of course the
        # geolocation fields are omitted here as they are supposed to be, but
        # we also omitted Profile_ID and the vdata called just 'metadata'.

        # Profile_ID was omitted as the there is a loss of information entailed
        # in reordering that field.  'metadata' was omitted as it appears
        # malformed and pyhdf chokes on it (segment fault).  It is this pyhdf
        # issue that caused us to choose the way we load the data fields.  We
        # explicitly specify the desired fields below because using the self.get(None)
        # call instead (which loads all, which we follow by some filtering) will
        # cause that issue.
        data_fields = ( 'Day_Night_Flag',
                        'Off_Nadir_Angle',
                        'Solar_Zenith_Angle',
                        'Solar_Azimuth_Angle',
                        'Scattering_Angle',
                        'Spacecraft_Position',
                        'Parallel_Column_Reflectance_Uncertainty_532',
                        'Parallel_Column_Reflectance_RMS_Variation_532',
                        'Perpendicular_Column_Reflectance_532',
                        'Perpendicular_Column_Reflectance_Uncertainty_532',
                        'Perpendicular_Column_Reflectance_RMS_Variation_532',                        
                        'Column_Integrated_Attenuated_Backscatter_532',
                        'Column_IAB_Cumulative_Probability',
                        'Tropopause_Height',
                        'Tropopause_Temperature',
                        'IGBP_Surface_Type',
                        'NSIDC_Surface_Type',
                        'Lidar_Surface_Elevation',
                        'DEM_Surface_Elevation',
                        'Surface_Elevation_Detection_Frequency',
                        'Normalization_Constant_Uncertainty_532',
                        'FeatureFinderQC',
                        'Calibration_Altitude_532',
                        'FeatureFinderQC',
                        'Number_Layers_Found',
                        'Layer_Top_Altitude',
                        'Layer_Base_Altitude',
                        'Opacity_Flag',
                        'Horizontal_Averaging',
                        'Attenuated_Backscatter_Statistics_532',
                        'Integrated_Attenuated_Backscatter_532',
                        'Integrated_Attenuated_Backscatter_Uncertainty_532',
                        'Attenuated_Backscatter_Statistics_1064',
                        'Integrated_Attenuated_Backscatter_1064',
                        'Integrated_Attenuated_Backscatter_Uncertainty_1064',
                        'Volume_Depolarization_Ratio_Statistics',
                        'Integrated_Volume_Depolarization_Ratio',
                        'Integrated_Volume_Depolarization_Ratio_Uncertainty',
                        'Attenuated_Total_Color_Ratio_Statistics',
                        'Integrated_Attenuated_Total_Color_Ratio',
                        'Overlying_Integrated_Attenuated_Backscatter_532',
                        'Layer_IAB_QA_Factor',
                        'Feature_Classification_Flags',
                        'ExtinctionQC_532',
                        'CAD_Score',
                        'Measured_Two_Way_Transmittance_532',
                        'Measured_Two_Way_Transmittance_Uncertainty_532',
                        'Two_Way_Transmittance_Measurement_Region',
                        'Feature_Optical_Depth_532',
                        'Feature_Optical_Depth_Uncertainty_532',
                        'Initial_532_Lidar_Ratio',
                        'Final_532_Lidar_Ratio',
                        'Lidar_Ratio_532_Selection_Method',
                        'Layer_Effective_532_Multiple_Scattering_Factor',
                        'Integrated_Particulate_Depolarization_Ratio',
                        'Integrated_Particulate_Depolarization_Ratio_Uncertainty',
                        'Particulate_Depolarization_Ratio_Statistics',
                        'Midlayer_Temperature',
                        'Cirrus_Shape_Parameter',
                        'Cirrus_Shape_Parameter_Uncertainty',
                        'Cirrus_Shape_Parameter_Invalid_Points',
                        'Ice_Water_Path',
                        'Ice_Water_Path_Uncertainty')

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
            # two or three dimensional.  The 2D ones actually includes 1D as well
            # as the 2nd dimension is listed as "1" in that case.  This should never
            # happen for this caliop 05km clay dataset
            if(dims != 2) and (dims != 3):
                print 'Skipping field ', k, ' of dimensionality ', dims
                continue
                        
            # add dimension name for array with a common dimension size
            my_shape = dDict_out[k][1].shape
            if ( len(my_shape)==2 and my_shape[1] == 10):
               v[0]['dimension1']='vertical_layer'
            if ( len(my_shape)==2 and my_shape[1] == 60):
               v[0]['dimension1']='vertical_layer_and_statistics_parameter'
            if ( len(my_shape)==2 and my_shape[1] == 1):
               v[0]['dimension1']='dummy'
             
            # Sort any number of columns of the field.  Each column is reorder
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
        
        file = open("caliop05km_clay_catalog.txt", 'w')
        line = 'Sensor/Model\tData Product\tVariable Name\tVariable Unit\n'
        file.write(line)
        for i in variableNames:
            attribute = self.dataDict[i][0]
            #print attribute
            line = 'Caliop\t05Km Cloud Layer\t%s\t%s\n' %(i, attribute['units'])
            file.write(line)

        file.close()


