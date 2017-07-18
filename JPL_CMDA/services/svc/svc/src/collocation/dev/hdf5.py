import sys
import numpy as N
import h5py as H5
#import h5py.filters as H5filters
H5filters = H5.filters
import time, types

#TAI = calendar.timegm((1993, 1, 1, 0, 0, 0))
TAI = 725846400

class Hdf5File(object):
    """Class implementing HDF5 file access."""
    
    GEOLOC_FIELDS = ()
    
    def __init__(self, file):
        """Constructor."""
        self.file      = file
        self.hdf       = None
        self.open()

        self.levels    = {}
        self.geoDict   = self._getGeoDict()
        self.dataDict  = self._getDataDict()
        self.close()
        return
        
    # Always define in subclass
    def _getGeoDict(self): raise NotImplementedError("Not implemented.")
    # Always define in subclass
    def _getDataDict(self): return None

    def open(self):

        if self.hdf is None:  # Intercept multiple attempt to open
            self.hdf = H5.File(self.file, 'r')

        return
    
    def close(self):

        if self.hdf != None:  # Intercept multiple attempts to close
            self.hdf.close()
            self.hdf = None
        return
    
    def getGeo(self): return self.geoDict
        
    def get(self, var):
        
        # Create dict of (attrs, array) for each var
        a = {}
        for v in var:
            datafield = self.findObject(self.hdf, v)
            if datafield == None:
                print 'Error: Could not find var ', v
                sys.exit(-1)

            # Get attributes and data
            # the following line doesn't work with the new h5py
            #attrs = dict([(key, val) for key, val in datafield.attrs.items()])            

            if 1:  # by btang
              attrs = {}
              keys = datafield.attrs.keys()
              for k in keys:
                if k=='DIMENSION_LIST': continue
                attrs[k] = datafield.attrs[k]

            carray = N.zeros(datafield.shape)
            datafield.read_direct(carray)
            a[v] = (attrs, carray)
            
            #print 'a[v][0] = ', a[v][0]  # Attributes
            #print 'a[v][1] = ', a[v][1]  # Data

        return a
    
    # Recursively look for params starting at item.  Item may be a
    # hdf5 "File" or a hdf5 "Group"
    def findObject(self, item, name):
        
        for k, v in item.iteritems():
            #print k, ': type(v) = ', type(v)
            if type(v) == H5.Group:
                #print 'Descending into group ', k, ' looking for', name
                param = self.findObject(v, name)
                if param != None:
                    return param
            else:
                #print 'Comparing ', k, ' and ', name
                if k == name:
                    return v
            
        return None

    def __del__(self): self.close()
