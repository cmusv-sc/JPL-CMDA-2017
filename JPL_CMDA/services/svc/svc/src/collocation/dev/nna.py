import numpy as N
#import bisect as B
import util as U
import distance as D
import sys
import datetime

# the index for query points when they are outside the grid
NOT_IN_GRID = -1

# ID placeholder when not a nearest neighbor
NOT_NN = -1

# 1 km is this many degrees at the equator
K2D = 360.0/(2*N.pi*U.R)

# When qry_range is large compared to the grid overlaid
# on target points, only search in C by C cells around
# each query point
C = 20


class nna():
    # This class implements the Nearest Neighbor Algorithm.


    def __init__(self, tgt_x, tgt_y, qry_x, qry_y, qry_idx1, qry_idx2, qry_range, cell_search_limit):
    # initialize the arrays
	# the x's and y's are lat's and lon's in degrees
	# qry_range is search radius in kms (anything farther is not NN)
	# only qry pts in the range [qry_idx1, qry_idx2] participate 

	# tgt_x, tgt_y for target points
	# qry_x, qry_y for query points
	self.qry_idx1 = qry_idx1
	self.qry_idx2 = qry_idx2
	self.n = len(tgt_x)
	self.m = self.qry_idx2 - self.qry_idx1 + 1
	if self.n != len(tgt_y) or self.m > len(qry_y) or self.m > len(qry_x):
	    print '****** Error: check the dimensions of your input arrays!'
	    sys.exit(-1)

        self.tgt_x = tgt_x
        self.tgt_y = tgt_y
        self.qry_x = qry_x
        self.qry_y = qry_y
	self.qry_range = float(qry_range)
	#-- print 'self.qry_range: ', self.qry_range

	C = cell_search_limit
	print '****** C: ', C

	# index of query point that is the NN of target point
        self.nn_idx = N.array([NOT_NN]*self.n)
	f = N.finfo(float)
	# distance between the target point and its NN in query points
        self.nn_dist = N.array([f.max]*self.n)

	# overlay k by k grid on target points
	self.k = int(N.ceil(N.sqrt(self.n)))
	#-- print 'self.k: ', self.k

	# grid
        self.grid_x = N.array([0.0]*(self.k+1))
        self.grid_y = N.array([0.0]*(self.k+1))

	# grid of lists for target point registration
	self.grid_regi = []
	for i in range(self.k):
	    self.grid_regi.append([])
	for i in range(self.k):
	    for j in range(self.k):
		self.grid_regi[i].append([])

	### self.grid_regi[0][1].append('ooo')
	### print self.grid_regi

	# to overlay a grid on the target points
	self.overlay_grid()

    # end of __init__()


    def overlay_grid(self):
    # overlay a k by k grid on target points
	f = N.finfo(float)
	self.max_x = f.min
	self.max_y = f.min
	self.min_x = f.max
	self.min_y = f.max
	### print 'max_x: ', self.max_x, ' max_y: ', self.max_y, ' min_x: ', self.min_x, ' min_y: ', self.min_y

	# find max and min x, y
	for nn in range(self.n):
	    if self.tgt_x[nn] > self.max_x:
		self.max_x = self.tgt_x[nn]
	    if self.tgt_y[nn] > self.max_y:
		self.max_y = self.tgt_y[nn]
	    if self.tgt_x[nn] < self.min_x:
		self.min_x = self.tgt_x[nn]
	    if self.tgt_y[nn] < self.min_y:
		self.min_y = self.tgt_y[nn]
	#-- print 'max_x: ', self.max_x, ' max_y: ', self.max_y, ' min_x: ', self.min_x, ' min_y: ', self.min_y

	# in the grid, add a layer of width qry_range surrounding all the target points
	# adjust lon degree span based on lat
	rR1 = N.cos(U.degree_to_radian(self.max_x))
	rR2 = N.cos(U.degree_to_radian(self.min_x))
	if rR1 < rR2:
	    rR = rR1
	else:
	    rR = rR2

	qry_lat_span = self.qry_range * K2D
	qry_lon_span = qry_lat_span / rR
	if qry_lon_span > 360.0:
	    print '****** Warning: large lon span ', qry_lon_span
	    print '       Possibly from high latitude target point!'

	self.min_x -= qry_lat_span
	self.max_x += qry_lat_span
	self.min_y -= qry_lon_span
	self.max_y += qry_lon_span
	#-- print 'after adjusting with qry_range, max_x: ', self.max_x, ' max_y: ', self.max_y, ' min_x: ', self.min_x, ' min_y: ', self.min_y

	# overlay a k by k grid
	dx = (self.max_x - self.min_x)/self.k
	dy = (self.max_y - self.min_y)/self.k
	#---print 'dx: ', dx, ' dy: ', dy

        self.grid_x[0] = self.min_x
        self.grid_y[0] = self.min_y
        self.grid_x[self.k] = self.max_x
        self.grid_y[self.k] = self.max_y

	for kk in range(1, self.k):
	    self.grid_x[kk] = self.grid_x[kk-1] + dx
	    self.grid_y[kk] = self.grid_y[kk-1] + dy

	### print 'self.grid_x: ', self.grid_x
	### print 'self.grid_y: ', self.grid_y
	### print ''

	# register each target point to a cell (ix, iy)
	for nn in range(self.n):
	    tgt_x = self.tgt_x[nn]
	    tgt_y = self.tgt_y[nn]

	    # O(log(n)) search
	    """
	    ix1 = B.bisect(self.grid_x, tgt_x) - 1
	    if ix1 == self.k:
		ix1 = self.k - 1
	    iy1 = B.bisect(self.grid_y, tgt_y) - 1
	    if iy1 == self.k:
		iy1 = self.k - 1
	    """

	    # O(n)
	    ### print 'self.grid_x: ', self.grid_x
	    ix = self.get_cell_num(self.grid_x, tgt_x)

	    ### print 'self.grid_y: ', self.grid_y
	    iy = self.get_cell_num(self.grid_y, tgt_y)

	    # all target points are in the grid, so no need to check
	    # if nn is outside the grid
	    self.grid_regi[ix][iy].append(nn)

	    """
	    if ix1 != ix or iy1 != iy:
		print '****** Warning: nn: ', nn, ' tgt_x: ', tgt_x, ' tgt_y: ', tgt_y
		print 'ix: ', ix, ' iy: ', iy
		print 'ix1: ', ix1, ' iy1: ', iy1
	    """


	    """
	    print '------ nn: ', nn, ' tgt_x: ', tgt_x, ' tgt_y: ', tgt_y
	    print 'ix: ', ix, ' iy: ', iy

	    print ''
	    """


	### print self.grid_regi
	"""
	for i in range(self.k):
	    for j in range(self.k):
		print 'grid (',i,', ',j,')',': ', 
		for k in range (len(self.grid_regi[i][j])):
		    print self.grid_regi[i][j][k],
		print ''
	"""

    # end of overlay_grid()


    def search_nn(self):
    # search for Nearest Neighbors

	cnt_dist = 0     # cnt how many dist calculations
	cnt_no_comp = 0  # cnt how many updates w/o dist calc

	print '*** in search_nn(), self.qry_idx1, self.qry_idx2+1: ', self.qry_idx1, self.qry_idx2+1

	elapsed_time1 = datetime.timedelta(0,0,0,0,0)
	elapsed_time2 = datetime.timedelta(0,0,0,0,0)

	# loop over query points, and find all target points
	# of which this query point can be NN
	for mm in range(self.qry_idx1, self.qry_idx2+1):
	    ### print ''
	    ### print '------- query point: mm= ', mm, ' ----------'
	    ### print 'x: ', self.qry_x[mm], ' y: ', self.qry_y[mm]
	    ### print 'self.qry_range: ', self.qry_range, ' K2D: ', K2D

	    # check if qry pt mm is outside the grid
	    # if yes, skip this qry point
	    imm = self.get_cell_num(self.grid_x, self.qry_x[mm])
	    jmm = self.get_cell_num(self.grid_y, self.qry_y[mm])
	    if imm == NOT_IN_GRID or jmm == NOT_IN_GRID:
		continue

	    # adjust lon degree span based on lat
	    rR = N.cos(U.degree_to_radian(self.qry_x[mm]))
	    if self.qry_range * K2D / rR > 360.0:
		print '****** Warning: large lon span ', self.qry_range * K2D / rR
		print '       Possibly from high latitude query point!'

	    # find Minimum Bounding Rectangular of query point's search range
	    mbr_x_min = self.qry_x[mm] - self.qry_range * K2D
	    if mbr_x_min < self.min_x:  # MBR cannot go out of the grid
		mbr_x_min = self.min_x
	    if mbr_x_min > self.max_x:
		mbr_x_min = self.max_x
	    mbr_x_max = self.qry_x[mm] + self.qry_range * K2D
	    if mbr_x_max > self.max_x:
		mbr_x_max = self.max_x
	    if mbr_x_max < self.min_x:
		mbr_x_max = self.min_x
	    mbr_y_min = self.qry_y[mm] - self.qry_range * K2D / rR
	    if mbr_y_min < self.min_y:
		mbr_y_min = self.min_y
	    if mbr_y_min > self.max_y:
		mbr_y_min = self.max_y
	    mbr_y_max = self.qry_y[mm] + self.qry_range * K2D / rR
	    if mbr_y_max > self.max_y:
		mbr_y_max = self.max_y
	    if mbr_y_max < self.min_y:
		mbr_y_max = self.min_y

	    # find grid cells that cover the MBR (O(log(n)))
	    """
	    imin3 = B.bisect(self.grid_x, mbr_x_min) - 1
	    if imin3 < 0:    # handle the boundary point
		imin3 = 0
	    if imin3 == self.k:    # handle the boundary point
		imin3 = self.k - 1
	    imax3 = B.bisect(self.grid_x, mbr_x_max) - 1
	    if imax3 == self.k:
		imax3 = self.k - 1
	    jmin3 = B.bisect(self.grid_y, mbr_y_min) - 1
	    if jmin3 < 0:
		jmin3 = 0
	    if jmin3 == self.k:
		jmin3 = self.k - 1
	    jmax3 = B.bisect(self.grid_y, mbr_y_max) - 1
	    if jmax3 == self.k:
		jmax3 = self.k - 1
	    """

	    # find grid cells that cover the MBR (O(1))
	    # if MBR outside the grid, the closest cell
	    # on the edge or corner of the grid is found
	    imin = self.get_cell_num(self.grid_x, mbr_x_min)
	    imax = self.get_cell_num(self.grid_x, mbr_x_max)
	    jmin = self.get_cell_num(self.grid_y, mbr_y_min)
	    jmax = self.get_cell_num(self.grid_y, mbr_y_max)
	    # no need to check boundary 'cause the MBR is guaranteed to be inside the grid

	    """
	    if imin3 != imin or imax3 != imax:
		### print 'self.grid_x: ', self.grid_x
		print '****** Warning: mm: ', mm, ' mbr_x_min: ', mbr_x_min, ' mbr_x_max: ', mbr_x_max
		print 'imin: ', imin, ' imax: ', imax
		print 'imin3: ', imin3, ' imax3: ', imax3

	    if jmin3 != jmin or jmax3 != jmax:
		print '****** Warning: mm: ', mm, ' mbr_y_min: ', mbr_y_min, ' mbr_y_max: ', mbr_y_max
		print 'jmin: ', jmin, ' jmax: ', jmax
		print 'jmin3: ', jmin3, ' jmax3: ', jmax3
	    """


	    """
	    if mm == 133706:
		print '------ for mm == ', mm
		print 'imin: ', imin, ' imax: ', imax, ' jmin: ', jmin, ' jmax: ', jmax
		print 'rR: ', rR
	    """

	    # choose C by C cells in the center from above
	    imin1 = imin; imax1 = imax
	    iex = int((imax - imin - C)/2)
	    if iex > 0:
		imin1 = imin + iex
		imax1 = imin + C

	    jmin1 = jmin; jmax1 = jmax
	    jex = int((jmax - jmin - C)/2)
	    if jex > 0:
		jmin1 = jmin + jex
		jmax1 = jmin + C

	    """
	    if mm == 133706:
		print '------ for mm == ', mm
		print 'imin1: ', imin1, ' imax1: ', imax1, ' jmin1: ', jmin1, ' jmax1: ', jmax1
	    """

	    # compare and update the NN of target points within C by C cells
	    start1 = datetime.datetime.now()
	    for ii in range(imin1, imax1+1):
		for jj in range(jmin1, jmax1+1):
		    len1 = len(self.grid_regi[ii][jj])
		    ### print 'ii: ', ii, ' jj: ', jj, ' len1: ', len1
		    # loop over all target points in this cell
		    for ll in range(len1):
			nn = self.grid_regi[ii][jj][ll]
			cnt_dist += 1
			d = D.get_Haversine_distance(self.tgt_x[nn], self.tgt_y[nn], \
			                             self.qry_x[mm], self.qry_y[mm])
                        """
			print 'nn: ', nn, self.tgt_x[nn], self.tgt_y[nn]
			print 'mm: ', mm, self.qry_x[mm], self.qry_y[mm]
			print 'd: ', d, ', self.qry_range: ', self.qry_range
                        """
			# this qry point is nearer than previous NN
			if d < self.qry_range and d < self.nn_dist[nn]:
			    self.nn_dist[nn] = d
			    self.nn_idx[nn] = mm
			    ### print 'nn: ', nn, ', self.nn_dist[nn]: ', self.nn_dist[nn], ', self.nn_idx[nn]: ', self.nn_idx[nn]

	    now1 = datetime.datetime.now()
	    elapsed_time1 += now1 - start1

	    # update (but not compare) the NN of target points outside C by C
	    # but inside grid cells that cover the MBR
	    start1 = datetime.datetime.now()
	    for ii in range(imin, imax+1):
		for jj in range(jmin, jmax+1):
		    # any cell outside of C by C
		    # if C chosen is large enough to cover the MBR, nothing will be done here
		    if ii < imin1 or ii > imax1 or jj < jmin1 or jj > jmax1:
			len1 = len(self.grid_regi[ii][jj])
			"""
			print '------ (no dist calc) mm == ', mm
			print 'imin: ', imin, ' imax: ', imax, ' jmin: ', jmin, ' jmax: ', jmax
			print 'imin1: ', imin1, ' imax1: ', imax1, ' jmin1: ', jmin1, ' jmax1: ', jmax1
			print 'ii: ', ii, ' jj: ', jj, ' len1: ', len1
			"""
			# loop over all target points in this cell
			for ll in range(len1):
			    nn = self.grid_regi[ii][jj][ll]
			    if self.nn_idx[nn] == NOT_NN: # this tgt pt hasn't got a NN yet
				cnt_no_comp += 1
				self.nn_idx[nn] = mm

	    now1 = datetime.datetime.now()
	    elapsed_time2 += now1 - start1

        # end of for mm

	print 'in search_nn, self.nn_idx: ', self.nn_idx
	print 'self.nn_dist: ', self.nn_dist
	print 'cnt dist calculation: ', cnt_dist, ' cnt in footprint but w/o dist calc: ', cnt_no_comp

	print 'elapsed_time1: ', elapsed_time1
	print '*** compare and update elapsed time: ', elapsed_time1.days, ' days, ', elapsed_time1.seconds, ' seconds'
	print 'elapsed_time2: ', elapsed_time2
	print '*** update only elapsed time: ', elapsed_time2.days, ' days, ', elapsed_time2.seconds, ' seconds'

	return (self.nn_idx, self.nn_dist)

    # end of search_nn()



    def get_cell_num(self, grid, coord):
    # grid: 1D array of coords of an evenly spaced 1D grid
    # coord: coord of a point in the 1D grid
    # output: the the cell number in which the point falls

	k = len(grid) - 1

	# when query point is outside to the left of the grid
	if coord < grid[0]:
	    ic = NOT_IN_GRID
	# when query point is outside to the right of the grid
	elif coord > grid[k]:
	    ic = NOT_IN_GRID
	else:
	    ### print 'coord: ', coord
	    ### print 'grid: ', grid
	    ic = int((coord - grid[0])/(grid[1] - grid[0]))
	    if ic == k: # point on the right end of the grid
		ic -= 1

	### print 'ic: ', ic

	return ic

    # end of get_cell_num()


