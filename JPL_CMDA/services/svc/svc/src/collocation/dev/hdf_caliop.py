
# This file is a temporary hack.  It is a copy of hdf.py to get around an issue
# with (what looks like) a malformed vdata called 'metadata' in the 05km alayer
# prouct.  It will probably hold true for other caliop products as well.  The hack
# is in the open() method

import numpy as N
from pyhdf.SD import SD
from pyhdf.HDF import HDF
from pyhdf.VS import VS
from pyhdf.error import HDF4Error
import time, types

#TAI = calendar.timegm((1993, 1, 1, 0, 0, 0))
TAI = 725846400

class HdfFile(object):
    """Class implementing HDF file access."""
    
    GEOLOC_FIELDS = ()
    
    def __init__(self, file):
        """Constructor."""
        self.file = file
        self.hdf = None
        self.vs = None
        self.vdinfo = None
        self.sd = None
        self.savedVarsDict = None
        self.open()
        
        # Permit data files without VData's
        if type(self.vdinfo) != type(None):
            self.vdList = [i[0] for i in self.vdinfo]
            #print self.vdList
        
        # Permit data files without SDS's
        if type(self.sd) != type(None):
            self.datasetList = self.sd.datasets().keys()
            #print self.datasetList

        self.levels   = {}
        self.geoDict  = self._getGeoDict()
        self.dataDict = self._getDataDict()
        self.close()
        
    # Always define in subclass
    def _getGeoDict(self): raise NotImplementedError("Not implemented.")
    # Always define in subclass, except for cloudsat
    def _getDataDict(self): return None

    def open(self):
        """Open for reading."""
        
        if self.hdf is None:
            self.hdf = HDF(self.file)
            self.vs = self.hdf.vstart()
            # Ignore exceptions telling us there are no VData's
            try:
                pass
                #self.vdinfo = self.vs.vdatainfo()
            except HDF4Error:
                pass
            # Ignore exceptions telling us there are no SDS's
            try:
                self.sd = SD(self.file)
            except HDF4Error:
                pass
    
    def close(self):
        """Close hdf file."""
        
        if hasattr(self, 'hdf') and self.hdf is not None:
            self.vs.end()
            self.hdf.close()
            self.sd.end()
            self.hdf = None
            self.vs = None
            self.vdinfo = None
            self.sd = None
    
    def getGeo(self): return self.geoDict
    
    def get(self, var):
        """Return variable array dict."""
        
        self.open()
        
        #get list of vars
        if isinstance(var, types.StringTypes): var = [var]
        elif isinstance(var, (types.ListType, types.TupleType)): pass
        elif var is None:
            # If we don't have any SDS's, go with the vdata's only
            # if we don't have any vdata's go with SDS's only
            try:
                var = self.vdList;
                try:
                    var.extend(self.datasetList)
                except AttributeError:
                    pass
            except AttributeError:
                var = self.datasetList                
        else: raise RuntimeError("Incorrect argument type for %s." % var)
        
        #create dict of (attrs, array) for each var
        a = {}
        for v in var:
            #handle SD types
            ds = None
            if v in self.datasetList:
                try:
                    ds = self.sd.select(v)
                    a[v] = (ds.attributes(), N.array(ds.get()))
                    continue
                except HDF4Error, e: pass
                finally:
                    if ds is not None: ds.endaccess()
            #handle VD types
            if v in self.vdList:
                vd = self.vs.attach(v)
                attrs = dict([(key, val[2]) for key, val in vd.attrinfo().items()])
                a[v] = (attrs, N.array(vd[:]))
                vd.detach()
            else: raise RuntimeError("Unknown variable name %s." % var)
        self.close()
        return a
    
    def getSavedVars(self, var, force=False):
        """Save variable array dict and return."""
        
        if self.savedVarsDict is None or force is True:
            self.savedVarsDict = self.get(var)
        return self.savedVarsDict

    def __del__(self): self.close()
