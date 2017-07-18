from ctypes import *
import numpy

# load the shared library
ms=CDLL('./_c_nna.so')
# input array
a=numpy.array(range(10),dtype=float)
# output array
b=numpy.array(range(10),dtype=float)
print 'a before calling: ', a
print 'b before calling: ', b

rt1 = ms.search_nn(a.ctypes.data_as(c_void_p), b.ctypes.data_as(c_void_p), 
       a.ctypes.data_as(c_void_p), b.ctypes.data_as(c_void_p), int(1), int(5),
       float(2.0), int(1))
print 'rt1: ', rt1

print 'a after calling: ', a
print 'b after calling: ', b
