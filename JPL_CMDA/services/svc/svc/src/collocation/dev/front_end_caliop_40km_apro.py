import sys
import numpy as N
from hdf_caliop import HdfFile, TAI

class front_end_caliop_40km_apro(HdfFile):
    """Class implementing Caliop 40km Aerosol Profile data parsing."""

    GEOLOC_FIELDS = ('Profile_Time_Start', 'Profile_Time_Stop',
                     'Latitude_Start', 'Latitude_Stop',
                     'Longitude_Start', 'Longitude_Stop')
    
    # Set by _getGeoDict() and required by  _getDataDict()
    sortedArgs = None

    def _getGeoDict(self):
        
        time_start = time_stop = 0
        lat_start  = lat_stop  = 0
        lon_start  = lon_stop = 0
        
        # extract geo arrays
        gDict = {'file': self.file}
        for field in self.GEOLOC_FIELDS:

            ds = self.sd.select(field)
            gDict[field] = N.array(ds.get())
            ds.endaccess()
                        
            # The geolocation params are Nx1, which is technically 2D.
            # This makes them have 1 dimension of size N which is easier
            # to deal with.
            tShape = gDict[field].shape
            gDict[field] = gDict[field].reshape(tShape[0]*tShape[1])

            if field == 'Profile_Time_Start':
                time_start = gDict[field]
            if field == 'Profile_Time_Stop':
                time_stop = gDict[field]
            if field == 'Longitude_Start':
                lon_start = gDict[field]
            if field == 'Longitude_Stop':
                lon_stop = gDict[field]
            if field == 'Latitude_Start':
                lat_start = gDict[field]
            if field == 'Latitude_Stop':
                lat_stop = gDict[field]

        # Process Time
        avg_time = (time_start + time_stop) / 2
        avg_time = avg_time + TAI
        self.sortedArgs = N.argsort(avg_time)
        gDict['Time'] = N.take(avg_time, self.sortedArgs)
        
        # Process Longitude
        avg_lon = (lon_start + lon_stop) / 2
	### do not convert to (0, 360) as CloudSat is using (-180, 180)
        ### avg_lon = N.where(avg_lon < 0, avg_lon + 360, avg_lon)
        gDict['Longitude'] = N.take(avg_lon, self.sortedArgs)               

        # Process Latitude
        avg_lat = (lat_start + lat_stop) / 2
        gDict['Latitude'] = N.take(avg_lat, self.sortedArgs)

        return gDict
    
    def _getDataDict(self):
        
        # Fields were not selected by Frank as planned as of the date of this
        # writing.  We tried to support just about everything.  Of course the
        # geolocation fields are omitted here as they are supposed to be, but
        # we also omitted the vdata called 'metadata'.

        data_fields = ( 'Tropopause_Height',
                        'Tropopause_Temperature',
                        'Temperature',
                        'Pressure',
                        'Molecular_Number_Density',
                        'Relative_Humidity',
                        'Profile_QA_Flag',
                        'Surface_Elevation_Statistics',
                        'Samples_Averaged',
                        'Aerosol_Layer_Fraction',
                        'Atmospheric_Volume_Description',
                        'Total_Backscatter_Coefficient_532',
                        'Total_Backscatter_Coefficient_Uncertainty_532',
                        'Perpendicular_Backscatter_Coefficient_532',
                        'Perpendicular_Backscatter_Coefficient_Uncertainty_532',
                        'Particulate_Depolarization_Ratio_Profile_532',
                        'Particulate_Depolarization_Ratio_Uncertainty_532',
                        'Extinction_Coefficient_532',
                        'Extinction_Coefficient_Uncertainty_532',
                        'Aerosol_Multi_Scattering_Profile_532',
                        'Aerosol_Multi_Scattering_Uncertainty_532',
                        'Backscatter_Coefficient_1064',
                        'Backscatter_Coefficient_Uncertainty_1064',
                        'Extinction_Coefficient_1064',
                        'Extinction_Coefficient_Uncertainty_1064',
                        'Aerosol_Multiple_Scattering_Profile_1064',
                        'Aerosol_Multiple_Scattering_Uncertainty_1064')

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
            print k, ' has ', len(tshape), ' dimensions'
            
            # We are going to ignore any data fields that are not listed as
            # two dimensional.  The 2D ones actually includes 1D as well
            # as the 2nd dimension is listed as "1" in that case.
            if(dims != 2):
                print 'Skipping field ', k, ' of dimensionality ', dims
                continue
                         
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
        
        file = open("caliop40km_apro_catalog.txt", 'w')
        line = 'Sensor/Model\tData Product\tVariable Name\tVariable Unit\n'
        file.write(line)
        for i in variableNames:
            attribute = self.dataDict[i][0]
            #print attribute
            line = 'Caliop\t40Km Aerosol Profile\t%s\t%s\n' %(i, attribute['units'])
            file.write(line)

        file.close()


