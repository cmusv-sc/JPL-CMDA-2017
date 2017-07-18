import numpy as N
import congrid

import sys


class geomap:
    def __init__(self, Cell_Along_Swath_5km, Cell_Across_Swath_5km, Cell_Along_Swath_1km, Cell_Across_Swath_1km, out=sys.stdout):
	self.out = out

	self.Cell_Along_Swath_5km = Cell_Along_Swath_5km
	self.Cell_Across_Swath_5km = Cell_Across_Swath_5km
	self.Cell_Along_Swath_1km = Cell_Along_Swath_1km
	self.Cell_Across_Swath_1km = Cell_Across_Swath_1km



    def geomap_5kmto1km(self, geodata_5km):

	#print >> self.out, 'in geomap_5kmto1km() ...'
	#print >> self.out, 'geodata_5km: ', geodata_5km

	LowResDims = geodata_5km.shape
	#print >> self.out, 'LowResDims[0]: ', LowResDims[0], ', LowResDims[1]: ', LowResDims[1]
	ResolutionFactor = 5   # 5km res -> 1km res
	first_col_1km =	2      # first SDS pixel 5km has a coordinate (2,2) from 1km data
	first_row_1km =	2

	if self.Cell_Along_Swath_5km == 0:
	    self.Cell_Along_Swath_5km =	LowResDims[0]   # 406

	if self.Cell_Across_Swath_5km == 0:
	    self.Cell_Across_Swath_5km = LowResDims[1]   # 270

	if self.Cell_Along_Swath_1km == 0:
	    self.Cell_Along_Swath_1km =	Cell_Along_Swath_5km*5   # 2030

	if self.Cell_Across_Swath_1km == 0:
	    self.Cell_Across_Swath_1km = Cell_Across_Swath_5km*5 + 4   # 1354

	#print >> self.out, 'self.Cell_Along_Swath_5km: ', self.Cell_Along_Swath_5km
	#print >> self.out, 'self.Cell_Across_Swath_5km: ', self.Cell_Across_Swath_5km
	#print >> self.out, 'self.Cell_Along_Swath_1km: ', self.Cell_Along_Swath_1km
	#print >> self.out, 'self.Cell_Across_Swath_1km: ', self.Cell_Across_Swath_1km

	"""
	print >> self.out, 'a row: '
	for i  in range(self.Cell_Across_Swath_5km):
	    print >> self.out, geodata_5km[0, i]
	"""


	# two beginning columns
	begin_col_exp = 2 * geodata_5km[:, 0] - geodata_5km[:, 1]
	#print >> self.out, 'len(begin_col_exp): ', len(begin_col_exp)
	### print >> self.out, 'begin_col_exp: ', begin_col_exp

	# two end columns
	end_col_exp = 2 * geodata_5km[:, self.Cell_Across_Swath_5km-1] - geodata_5km[:, self.Cell_Across_Swath_5km-2]
	### print >> self.out, 'end_col_exp: ', end_col_exp

	end_col_exp_rest = 2 * end_col_exp - geodata_5km[:, self.Cell_Across_Swath_5km-1]
	### print >> self.out, 'end_col_exp_rest: ', end_col_exp_rest

	# a larger array for temp use
	exp_geodata_5km = N.array([0.0]*(self.Cell_Across_Swath_5km + 3)*self.Cell_Along_Swath_5km)
	exp_geodata_5km = exp_geodata_5km.reshape(self.Cell_Along_Swath_5km, (self.Cell_Across_Swath_5km + 3))
	### print >> self.out, 'exp_geodata_5km: ', exp_geodata_5km
	exp_geodata_5km[:, 0] = begin_col_exp
	exp_geodata_5km[:, 1:self.Cell_Across_Swath_5km+1] = geodata_5km
	### print >> self.out, '1. exp_geodata_5km: ', exp_geodata_5km

	exp_geodata_5km[:, self.Cell_Across_Swath_5km + 1] = end_col_exp
	exp_geodata_5km[:, self.Cell_Across_Swath_5km + 2] = end_col_exp_rest
	### print >> self.out, '2. exp_geodata_5km: ', exp_geodata_5km


	Internal_geodata_5km = exp_geodata_5km.copy()

	begin_row_exp =	2 * Internal_geodata_5km[0, :] - Internal_geodata_5km[1, :]
	end_row_exp = 2 * Internal_geodata_5km[self.Cell_Along_Swath_5km-1, :] - Internal_geodata_5km[self.Cell_Along_Swath_5km-2, :]

	exp_geodata_5km	= N.array([0.0]*((self.Cell_Across_Swath_5km + 3)*(self.Cell_Along_Swath_5km + 2)))
	exp_geodata_5km = exp_geodata_5km.reshape((self.Cell_Along_Swath_5km+2), (self.Cell_Across_Swath_5km + 3))
	exp_geodata_5km[0, :] =	begin_row_exp
	exp_geodata_5km[1:self.Cell_Along_Swath_5km+1, :] = Internal_geodata_5km
	exp_geodata_5km[self.Cell_Along_Swath_5km+1, :] = end_row_exp

	### print >> self.out, '3. exp_geodata_5km: ', exp_geodata_5km

	Internal_geodata_5km = exp_geodata_5km.copy()
	#print >> self.out, 'Internal_geodata_5km: ', Internal_geodata_5km
	dims5km = Internal_geodata_5km.shape
	#print >> self.out, 'Internal_geodata_5km.shape: ', dims5km

	Expand_cell_Along_Swath_1km = ( self.Cell_Along_Swath_5km + 1 ) * ResolutionFactor + 1
	Expand_Cell_Across_Swath_1km = ( self.Cell_Across_Swath_5km + 2 ) * ResolutionFactor + 1

	dims1km = N.array([0,0])

	dims1km[0] = Expand_cell_Along_Swath_1km
	dims1km[1] = Expand_Cell_Across_Swath_1km

	Expand_geodata_1km = congrid.congrid(Internal_geodata_5km, dims1km)

	geodata_1km = Expand_geodata_1km[(first_row_1km+1):self.Cell_Along_Swath_1km+first_row_1km, \
					    (first_col_1km+1):self.Cell_Across_Swath_1km+first_col_1km]
	#print >> self.out, 'geodata_1km: ', geodata_1km
	#print >> self.out, 'geodata_1km.shape: ', geodata_1km.shape

	return geodata_1km

    # end of geomap_5kmto1km()

