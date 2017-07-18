#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#if !defined(__APPLE__)
#include <malloc.h>
#endif

#include <math.h>
#include "mergein.h"

#ifndef NAN
#define NAN 0.0/0.0
#endif

int main() {

  int i;
  int latmin = -113, latmax = -111, lonmin = 81, lonmax = 83;
  printf("latmin: %d\n", latmin);
// print 'latmax: ', latmax
// print 'lonmin: ', lonmin
// print 'lonmax: ', lonmax

  double latinc = 1.0; 
  double loninc = 1.0; 
// print 'latinc: ', latinc
  printf("latinc: %f\n", latinc);
// print 'loninc: ', loninc

  double W = 0.001;
  double R = 0.8;
  double T0 = 1000.0;
// print 'time weight: ', W
// print 'search radius: ', R
// print 'time of interest: ', T0

// # input array
// # lat, lon, time, value
  int sz1 = 3;  // # num of query points
// qry_lat=N.array(range(sz1),dtype=N.float64)
  double *qry_lat;
  qry_lat = (double *)malloc(sz1*sizeof(double));

// qry_lon=N.array(range(sz1),dtype=N.float64)
  double *qry_lon;
  qry_lon = (double *)malloc(sz1*sizeof(double));

// qry_t=N.array(range(sz1),dtype=N.float64)
  double *qry_t;
  qry_t = (double *)malloc(sz1*sizeof(double));

// qry_val=N.array(range(sz1),dtype=N.float64)
  double *qry_val;
  qry_val = (double *)malloc(sz1*sizeof(double));


  for (i=0; i<sz1; i++)
    qry_t[i] = T0;

/*
  for (i=0; i<sz1/2; i++)
    qry_t[i] = T0 + 2*i;

  for (i=sz1/2; i<sz1; i++)
    qry_t[i] = T0 + 600 + 2*i;
*/

  for (i=0; i<sz1; i++)
    qry_val[i] = i + 500.0;

  qry_lat[0] = -113.5;
  for (i=1; i<sz1; i++)
    qry_lat[i] = qry_lat[i-1] + 0.5;

  qry_lon[0] = 81;
  for (i=1; i<sz1; i++)
    qry_lon[i] = qry_lon[i-1] + 0.6;

  // # memory for output lat, lon, value
  int nlat = (int)ceil((double) (latmax - latmin)/latinc) + 1;
  int nlon = (int)ceil((double) (lonmax - lonmin)/loninc) + 1;
  printf("nlat: %d\n", nlat);
  printf("nlon: %d\n", nlon);

  // # uniform grid

  double *grid_lat = (double*)malloc((nlat*nlon)*sizeof(double));
  double *grid_lon = (double*)malloc((nlat*nlon)*sizeof(double));
  double *value = (double*)malloc((nlat*nlon)*sizeof(double));

  // print 'nan: ', float('nan')

  for (i=0; i<nlat*nlon; i++)
    // value[i] = float('nan');
    value[i] = NAN;

  // print '***** before calling C'

  int rt1;
  int flag_nearest = 1;
  char *binary_xyz_file_name = "./tmp_xyz.bin";
  rt1 = mergein(qry_lat, qry_lon, qry_t, qry_val, sz1,
       latmin, latmax, lonmin, lonmax, latinc, loninc,
       R, grid_lat, grid_lon, T0, 
       value, nlat, nlon, flag_nearest, binary_xyz_file_name);
  // print 'rt1: ', rt1
  // print ''

  printf("grid point value: \n");
  for (i=0; i<nlat*nlon; i++)
    printf("%f\n", value[i]);

  free(qry_lat);
  free(qry_lon);
  free(qry_t);
  free(qry_val);
  free(grid_lat);
  free(grid_lon);
  free(value);

  return 0;
}
