#
# This unittest is geared toward testing the reshaping functionality in
# select front ends.
#

import sys
import numpy as N
import front_end_airs as FEAIRS
import front_end_modis_cloud_5km as FEMODIS

# Test if two 2D arrays of the same size have the same content
def test_equal(lhs, rhs):
    
    i = j = 0
    while j < lhs.shape[0]:
        while i < lhs.shape[1]:
            #print 'item = ', lhs[j][i]
            if lhs[j][i] != rhs[j][i]:
                return 0
            i = i + 1
        i = 0
        j = j + 1

    return 1

def test_airs():
        
    airs_file   = "AIRS.2006.01.01.001.L2.RetStd.v5.0.14.0.G07291112013.hdf"
    print "****** Reading AIRS data from file: ", airs_file
    airs = FEAIRS.front_end_airs(airs_file)
        
    # Test 2D reshape and reorder.  A 1D array should result with the
    # elements reordered per the order specified below.
    #myname  = 'var2d1d'
    #myorder = [9, 0, 2, 4, 3, 6, 5, 7, 1, 8]
    #mydata  = N.array([[0.5, 0.2, 0.1, 0.3, 0.4],[1.5, 1.2, 1.1, 1.3, 1.4]])
    #print 'Testing 2d to 1d reshape and reorder'
    #print myname, ' is of shape ', mydata.shape
    #print mydata
    #mydata = airs.process_2d(myname, mydata, myorder)
    #print myname, ' is of shape ', mydata.shape
    #print 'order requested is ', myorder
    #print mydata

    # Test 3D reshape and reorder.  A 2D array should result with the
    # elements reordered per the order specified below.  The inner-most
    # elements should remain paired with one another.

    myname  = "contrived data"
    myorder = [9, 0, 2, 4, 3, 6, 5, 7, 1, 8]
    mydata  = N.array([[[0.5,0.55,0.56], [0.2,0.25,0.26], [0.1,0.15,0.16], [0.3,0.35,0.36], [0.4,0.45,0.46]],
                    [[1.5,1.55,1.56], [1.2,1.25,1.26], [1.1,1.15,1.16], [1.3,1.35,1.36], [1.4,1.45,1.46]]])

    print 'Testing AIRS 3d to 2d reshape and reorder'
    print 'AIRS data is originally of shape ', mydata.shape
    #print 'input data = ', mydata
    mydata = airs.process_3d(myname, mydata, myorder)
    print myname, ' is now of shape ', mydata.shape
    print 'order requested along axis 0 is ', myorder
    #print 'actual results = ', mydata

    myresult = N.array([[ 1.4, 1.45, 1.46],
                    [ 0.5,0.55,0.56],
                    [ 0.1,0.15,0.16],
                    [ 0.4,0.45,0.46],
                    [ 0.3,0.35,0.36],
                    [ 1.2,1.25,1.26],
                    [ 1.5,1.55,1.56],
                    [ 1.1,1.15,1.16],
                    [ 0.2,0.25,0.26],
                    [ 1.3,1.35,1.36]])
    #print 'desired results = ', myresult

    if test_equal(mydata, myresult):
        print 'AIRS PASSED'
    else:
        print 'AIRS FAILED'
    
def test_modis():
        
    modis_file      = "MYD06_L2.A2007054.1255.005.2007058012408.hdf"
    print "****** Reading MODIS data from file: ", modis_file
    modis           = FEMODIS.front_end_modis_cloud_5km(modis_file)

    myname  = "contrived data"
    myorder = [9, 0, 2, 4, 3, 6, 5, 7, 1, 8, 10, 11, 12, 13, 14]
    mydata  = N.array([[[0.5,0.55,0.56], [0.2,0.25,0.26], [0.1,0.15,0.16], [0.3,0.35,0.36], [0.4,0.45,0.46]],
                    [[1.5,1.55,1.56], [1.2,1.25,1.26], [1.1,1.15,1.16], [1.3,1.35,1.36], [1.4,1.45,1.46]]])

    print 'Testing MODIS 3d to 2d reshape and reorder'
    print 'MODIS data is originally of shape ', mydata.shape
    print 'input data = ', mydata
    include = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    mydata = modis.process_3d(myname, mydata, include, myorder)
    print myname, ' is now of shape ', mydata.shape
    print 'order requested along azis 0 is ', myorder
    print 'actual results = ', mydata
    
    myresult = N.array([[0.3, 1.3],
                        [0.5, 1.5],
                        [0.56, 1.56],
                        [0.25, 1.25],
                        [0.2, 1.2],
                        [0.1, 1.1],
                        [0.26, 1.26],
                        [0.15, 1.15],
                        [0.55, 1.55],
                        [0.16, 1.16],
                        [0.35, 1.35],
                        [0.36, 1.36],
                        [0.4, 1.4 ],
                        [0.45, 1.45],
                        [0.46, 1.46]])

    print 'desired results = ', myresult

    if test_equal(mydata, myresult):
        print 'MODIS PASSED'
    else:
        print 'MODIS FAILED'
            
test_airs()
test_modis()

# Very grueling to work up good test data for any 3D, 4D and 5D cases.
# Consider extending this unittest here if time permits.  In the general case
# what should happen is that dimensions 1 and 2 get combined into 1 dim and the
# remaining dimensions remain intact.  The reordering takes place only along the
# combined dimension.




