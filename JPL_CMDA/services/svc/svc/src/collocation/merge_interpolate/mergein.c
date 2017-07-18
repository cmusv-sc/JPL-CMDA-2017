#include<stdlib.h>
#include<stdio.h>
#include<float.h>
#include<math.h>
#include<time.h>

#define DEBUG -1

#if !defined(__APPLE__)
#include <malloc.h>
#endif

#ifndef NAN
#define NAN 0.0/0.0
#endif

#include"distance.h"

// NN: near neighbor

// the index for query points when they are outside the grid
#define NOT_IN_GRID -1

// ID placeholder when not a nearest neighbor
#define NOT_NN -1

// 1 km is this many degrees at the equator
#define K2D 360.0/(2*pi*R)

// time difference between two paths (~90 mins)
#define gap 5400.0

// The grid overlayed on the target points
// assumes 1 point per cell on average. If
// MAX number of points fall in one cell,
// it means the target points are extreamly
// unevenly distributed in space, which should
// not be the case. 
#define MAX 40

#define degree_to_radian(degree)  (degree*pi/180.0)

// array of pts to MAX integers
#define LIST_EMPTY -1
typedef int LIST[MAX];
typedef double DIST[MAX];
typedef double TIME[MAX];
LIST *lst;
DIST *dst;
TIME *tim;
int *len;

// a MODIS pixel within the search radius
// of a user defined grid point
typedef struct {
  double dist;  // distance to the grid point
  double time;  // time when value of the pixel was acquired
  double val;   // value of the pixel
} pixel; 

// comp function for qsort
int comp(const void *a, const void *b) {
  double t1, t2;
  t1 = ((pixel *)a)->time;
  t2 = ((pixel *)b)->time;

  if (t1 == t2)
    return 0;
  else {
    if (t1 < t2)
      return -1;
    else
      return 1;
  }
}

// register a query point to a grid point
void en_list(int ix, int iy, int k, int id, double d, double t)
{
  int l;
  int pos;

  pos = iy*k+ix;

  if(len[pos]>=MAX) {
    // printf("****** List Full. Trying to replace a NN with larger distance.\n");
    for(l=0; l<MAX; l++) {
      if(dst[pos][l] > d) {
        (lst[pos])[l] = id;
        (dst[pos])[l] = d;
        break;
      }
    }
  }
  (lst[pos])[len[pos]] = id;
  (dst[pos])[len[pos]] = d;
  (tim[pos])[len[pos]] = t;
  len[pos]++;
}

// return id of a query point registered to a grid point
int list_id(int ix, int iy, int k, int index)
{
  int pos;

  pos = iy*k+ix;

  if(len[pos] == 0 || index >= len[pos]) {
    // printf("****** Empty list.\n");
    return LIST_EMPTY;
  }
  return (int)((lst[pos])[index]);
}

// return distance of a query point registered to a grid point
double list_dst(int ix, int iy, int k, int index)
{
  int pos;

  pos = iy*k+ix;

  if(len[pos] == 0 || index >= len[pos]) {
    // printf("****** Empty list.\n");
    return LIST_EMPTY;
  }
  return (double)((dst[pos])[index]);
}

// return time of a query point registered to a grid point
double list_tim(int ix, int iy, int k, int index)
{
  int pos;

  pos = iy*k+ix;

  if(len[pos] == 0 || index >= len[pos]) {
    // printf("****** Empty list.\n");
    return LIST_EMPTY;
  }
  return (double)((tim[pos])[index]);
}

// return the length of the list associated with a grid point
int list_len(int ix, int iy, int k)
{
  return (len[iy*k+ix]);
}

// debug print
void print_list(int ix, int iy, int k)
{
  int i;
  int pos;

  pos = iy*k + ix;

  printf ("list(%d, %d): ", ix, iy);
  for (i=0; i<len[pos]; i++) {
    printf (", %d", (int)(lst[pos])[i]);
  }
  printf("       ");
  for (i=0; i<len[pos]; i++) {
    printf (", %f", (double)(dst[pos])[i]);
    printf (", %f", (double)(tim[pos])[i]);
  }
  printf ("\n");
}



int get_cell_num(int k, double *grid, double coord) {
    // k: the length of array grid
    // grid: 1D array of coords of an evenly spaced 1D grid
    // coord: coord of a point in the 1D grid
    // output: the the cell number in which the point falls

	int ic;

	/*
	printf("coord: %f\n", coord);
	printf("grid[0]: %f\n", grid[0]);
	printf("grid[1]: %f\n", grid[1]);
	printf("grid[k-1]: %f\n", grid[k-1]);
	*/

	// when query point is outside of the grid
	if (coord < grid[0] || coord > grid[k-1])
	    ic = NOT_IN_GRID;
	else {
	    ic = (int)((coord - grid[0])/(grid[1] - grid[0]));
	    // printf("ic: %d\n", ic);
	    if (ic == k-1) // point on the right end of the grid
		ic -= 1;
	}

	// printf("k-1: %d\n", k-1);
	// printf("ic: %d\n", ic);

	return ic;
}


// calculate weighted average (algorithm similar to GMT's nearneighbor)
double nearneighbor_averaging(pixel *p, int cluster_num, int cluster_cnt, double r0) {
  int l;
  int has_value;
  double r, d, wd, sum_wd, v1;

  // printf("cluster: %d has %d pixels\n", cluster_num, cluster_cnt);

  sum_wd = 0.0;
  v1 = 0.0;
  has_value = 0;
  // loop over pixels of a cluster
  for (l=0; l<cluster_cnt; l++) {
    if (!isnan(p[l].val)) {
      has_value = 1;
      r = p[l].dist;
      # if DEBUG == 1
      printf("r: %f\n", r);
      #endif
      // r0 is the search radius in degree
      // calculate weighting function for values (from GMT nearneighbor)
      // w(r) = 1/(1+d^2), where
      // d = 3 * r / search_radius, r is the distance
      d = 3*r/r0;
      // printf("d: %f\n", d);
      // distance weight
      wd = 1.0/(1.0+d*d);
      # if DEBUG == 1
      // printf("wd: %f\n", wd);
      #endif
      v1 += wd * p[l].val;
      // used to normalize weights
      sum_wd += wd;
    }
  }  // for pixels within a cluster

  if (has_value == 1) {
    # if DEBUG == 1
    // printf("sum_wd: %f\n", sum_wd);
    #endif
    v1 /= sum_wd;
    return v1;
  }
  else
    return NAN;
}

/*
	        mm = list_id(lt, ln, nlat, l);
                time1 = list_tim(lt, ln, nlat, l);
	        printf("time1: %f, t0: %f\n", time1, t0);
	        // printf("lt: %d, ln: %d, l: %d, mm: %d\n", lt, ln, l, mm);
                if (!isnan(val[mm])) {
	          // printf("w: %f, val[mm]: %f\n", w, val[mm]);
	          v1 += wd * wt * val[mm];
                  // used to normalize weights
                  sum_wd += wd;
                  sum_wt += wt;
                }
                if (sum_wd != 0.0) {
                }
*/


/*
     function that implements merge interpolation
     input: 
          (1) four 1-d arrays: lat, lon, time, value, and their size nqry
          (2) user input uniform grid
               xmin, xmax, ymin, ymax (user input window)
               xinc, yinc (grid spacing)
          (3) search radius in degree
          (4) time of interest (t0)
          (5) memory for grid points and their values
          (6) nearest neighbor: flag to choose from nearest neighbor or distance-weighted
              average and time interpolation
      
     output: 
          (1) grd file (optional)
               lat, lon, value
          (2) arrays holding lat, lon, value of the grid
*/

int mergein(double *lat, double *lon, double *time, double *val, int nqry, 
            double latmin, double latmax, double lonmin, double lonmax, double latinc, double loninc,
            double r0, double *grid_lat, double *grid_lon, double t0, double *value, 
            int nlat, int nlon, int flag_nearest, char *xyz_file_name)
{
	int lt, ln;
	int l, i, j;
	double r, wd, wt, v1, v2, v, d;
        double sum_wd, sum_wt;
        double time1;
	double rr0, l0;
        int lst_len;
        int num_clusters = 1;

	printf("----------- in mergein(): \n");

/*
	printf("t0: %f\n", t0);
	printf("r0: %f\n", r0);

	for(l=0; l<nqry; l++) {
	  printf("mlat: %f\n", lat[l]);
	}

	for(l=0; l<nqry; l++) {
	  printf("mlon: %f\n", lon[l]);
	}

	for(l=0; l<nqry; l++) {
	  printf("mtime: %f\n", time[l]);
	}

	for(l=0; l<nqry; l++) {
	  printf("mval: %f\n", val[l]);
	}
*/
        # if DEBUG == 1
	for(l=0; l<nlat*nlon; l++) {
	  printf("value: %f\n", value[l]);
	}
        #endif


	// create user input uniform grid in 1D
	// this is only for for 1D cell number calculation
	double *grid_1d_lat, *grid_1d_lon;

	grid_1d_lat = (double *)malloc(nlat*sizeof(double));
	grid_1d_lon = (double *)malloc(nlon*sizeof(double));

	// uniform grid storage uses lat major
        // boundary where lat == latmin and lat == latmax
	for (ln=0; ln<nlon; ln++) {
          grid_lat[ln*nlat + 0] = latmin;
          grid_lat[ln*nlat + nlat-1] = latmax;
	  // printf("grid_lat: %f\n", grid_lat[0      + ln*nlat]);
	  // printf("grid_lat: %f\n", grid_lat[nlat-1 + ln*nlat]);
	}

	for (ln=0; ln<nlon; ln++) {
	  for (lt=1; lt<nlat-1; lt++) {
	    grid_lat[ln*nlat + lt] = grid_lat[ln*nlat + lt-1] + latinc;
	    // printf("grid_lat: %f\n", grid_lat[lt + ln*nlat]);
	  }
	}

	// printf("\n");

	// uniform grid storage uses lat major
        // boundary where lon == lonmin and lon == lonmax
	for (lt=0; lt<nlat; lt++) {
          grid_lon[0*nlat        + lt] = lonmin;
          grid_lon[(nlon-1)*nlat + lt] = lonmax;
	  // printf("grid_lon: %f\n", grid_lon[lt + 0*nlat       ]);
	  // printf("grid_lon: %f\n", grid_lon[lt + (nlon-1)*nlat]);
	}

	for (lt=0; lt<nlat; lt++) {
	  for (ln=1; ln<nlon-1; ln++) {
	    grid_lon[ln*nlat + lt] = grid_lon[(ln-1)*nlat + lt] + loninc;
	    // printf("grid_lon: %f\n", grid_lon[lt + ln*nlat]);
	  }
	}

	// create 1d grid for cell number calculation
	// printf("(grid_1d_lat)\n");
	for (lt=0; lt<nlat; lt++) {
	  grid_1d_lat[lt] = grid_lat[lt];
	  // printf("1d lat: %f\n", grid_1d_lat[lt]);
	}

	// printf("(grid_1d_lon)\n");
	for (ln=0; ln<nlon; ln++) {
	  grid_1d_lon[ln] = grid_lon[ln*nlat];
	  // printf("1d lon: %f\n", grid_1d_lon[ln]);
	}

	// printf("\n");
	// printf("\n");
	// printf("\n");

	// printf("latmin: %f\n", latmin);
	// printf("latmax: %f\n", latmax);
	// printf("lonmin: %f\n", lonmin);
	// printf("lonmax: %f\n", lonmax);

	// debug print of the grid
	/*
	printf("(grid_lat, grid_lon)\n");

	for (ln=0; ln<nlon; ln++) {
	  for (lt=0; lt<nlat; lt++) {
	    printf("%f, %f\n", grid_lat[ln*nlat + lt], grid_lon[ln*nlat + lt]);
	  }
	  printf("\n");
	}
	*/

	// printf("DBL_MAX: %f\n", DBL_MAX);
	printf("MAX: %d\n", MAX);

	// memory for registration of query points to grid points
	lst = (LIST *)malloc(nlat*nlon*sizeof(LIST)); 
	dst = (DIST *)malloc(nlat*nlon*sizeof(DIST)); 
	tim = (TIME *)malloc(nlat*nlon*sizeof(TIME)); 
	len = (int *)malloc(nlat*nlon*sizeof(int));
	for (i=0; i<nlat; i++)
	  for (j=0; j<nlon; j++) {
	    for (l=0; l<MAX; l++) {
	      (lst[j*nlat + i])[l] = 0;
	      (dst[j*nlat + i])[l] = DBL_MAX;
	      (tim[j*nlat + i])[l] = -1.0;
	    }
	    len[j*nlat + i] = 0;
	    // print_list(i, j, nlat);
	  }

	// printf("nqry: %d\n", nqry);
	// printf ("qry_range: %f\n", r0);

	// loop over query points, and find all grid points
	// of which a query point can be NN
	int mm;
	// printf ("------- query point: mm: lat, lon, value\n");
	for (mm=0; mm<nqry; mm++) {
	   // printf ("------- query point: mm=%d ----------\n", mm);
	   // printf ("lat: %f, lon: %f\n", lat[mm], lon[mm]);

	   // check if qry pt mm is outside the grid
	   // if yes, skip this qry point
	   if (lat[mm] < latmin || lat[mm] > latmax || lon[mm] < lonmin || lon[mm] > lonmax) {
	     // printf("This query point is outside the grid! Skipping it ...\n");
	     // printf ("lat: %f, lon: %f\n", lat[mm], lon[mm]);
	     continue;
	   }

	   // printf ("%d: %f, %f, %f\n", mm, lat[mm], lon[mm], val[mm]*0.95*6.2);
	   // printf ("...lat: %f, ...lon: %f, val: %f\n", lat[mm], lon[mm], val[mm]*0.95*6.2);

	   // compute cell number in which this query point
	   int imm = get_cell_num(nlat, grid_1d_lat, lat[mm]);
	   int jmm = get_cell_num(nlon, grid_1d_lon, lon[mm]);

	   // printf ("imm: %d, jmm: %d\n", imm, jmm);

	   // check if qry pt mm is outside the grid
	   // if yes, skip this qry point
	   /*
	   if (imm == NOT_IN_GRID || jmm == NOT_IN_GRID) {
	     printf("This query point is outside the grid! Skipping it ...\n");
	     continue;
	   }
	   */

	   // find Minimum Bounding Rectangular of query point's search range
           // r0 is the search radius in degree
	   double mbr_lat_min = lat[mm] - r0;
	   if (mbr_lat_min < latmin)  // MBR cannot go out of the grid
	      mbr_lat_min = latmin;
	   if (mbr_lat_min > latmax)
	      mbr_lat_min = latmax;

	   double mbr_lat_max = lat[mm] + r0;
	   if (mbr_lat_max > latmax)
	      mbr_lat_max = latmax;
	   if (mbr_lat_max < latmin)
	      mbr_lat_max = latmin;

	   double mbr_lon_min = lon[mm] - r0;
	   if (mbr_lon_min < lonmin)
	      mbr_lon_min = lonmin;
	   if (mbr_lon_min > lonmax)
	      mbr_lon_min = lonmax;

	   double mbr_lon_max = lon[mm] + r0;
	   if (mbr_lon_max > lonmax)
	      mbr_lon_max = lonmax;
	   if (mbr_lon_max < lonmin)
	      mbr_lon_max = lonmin;

	   // find grid cells that cover the MBR (O(1))
	   // if MBR outside the grid, the closest cell
	   // on the edge or corner of the grid is found
	   int imin = get_cell_num(nlat, grid_1d_lat, mbr_lat_min);
	   int imax = get_cell_num(nlat, grid_1d_lat, mbr_lat_max);
	   int jmin = get_cell_num(nlon, grid_1d_lon, mbr_lon_min);
	   int jmax = get_cell_num(nlon, grid_1d_lon, mbr_lon_max);

	   // include the grid point on the right
	   if (imax < nlat-1)
	     imax += 1;
	   if (jmax < nlon-1)
	     jmax += 1;

	   /*
	   printf ("imin: %d, jmin: %d\n", imin, jmin);
	   printf ("imax: %d, jmax: %d\n", imax, jmax);
	   printf ("total grid points involved: %d\n", (imax-imin+1)*(jmax-jmin+1));
	   */

	   // loop over grid points of the cells,
           // add to the NN list of grid points within MBR
	   // caching only MAX number of NNs
           for (lt=imin; lt<=imax; lt++) {
             for (ln=jmin; ln<=jmax; ln++) {
               // printf ("###### lt: %d, ln: %d\n", lt, ln);
               // r = get_4D_distance(grid_lat[ln*nlat+lt], grid_lon[ln*nlat+lt], 
                    // lat[mm], lon[mm], t0, time[mm], C0);
               r = get_Haversine_distance(grid_lat[ln*nlat+lt], grid_lon[ln*nlat+lt], lat[mm], lon[mm]);
               r = r * K2D;  // convert from kilometer to degree

               // printf ("mm: %d, qry_x: %f, qry_y: %f\n", mm, qry_x[mm], qry_y[mm]);
               // printf ("r: %f, r0: %f\n", r, r0);
	       if (r <= r0)
	         en_list(lt, ln, nlat, mm, r, time[mm]);
             } // for ln
           } // for lt

	} // for mm

	// printf ("------- end of query points\n");

	// debug print
/*
	for (i=0; i<nlat; i++)
	  for (j=0; j<nlon; j++) {
	    print_list(i, j, nlat);
	  }
*/

        printf ("flag_nearest: %d\n", flag_nearest);


	// loop over grid points and
	// calculate the value associated to
	// each point
	// printf("-------- loop over grid points to compute interpolated value\n");
        for (lt=0; lt<nlat; lt++) {
          for (ln=0; ln<nlon; ln++) {
            // printf("for grid point (%d, %d)\n", lt, ln);
	    v1 = 0.0;
	    rr0 = DBL_MAX;  // initial value of radius
	    l0 = -1;

            // if no pixels are found around this grid point,
            // move on to the next grid point
            lst_len = list_len(lt, ln, nlat);
            if (lst_len <= 0) continue;

            // printf ("lst_len: %d\n", lst_len);

            // if we only need the nearest neighbor
            if (flag_nearest == 1) {

              // loop over all candidates of the NN of this grid point
              for (l=0; l<lst_len; l++) {
	        r = list_dst(lt, ln, nlat, l);
                // printf ("r: %f, r0: %f\n", r, r0);

	        if (r < rr0) {
	          rr0 = r;
	          mm = list_id(lt, ln, nlat, l);
	          v1 = val[mm];
	          l0 = l;
	        }
              }

              if (l0 != -1) {
	        value[ln*nlat + lt] = v1;
              }
            } else {  // if distance-weighted average and then time interpolation

              // make 1D array of structure for clustering
              // one cluster is all the pixels that belong to one MODIS path
              pixel *p;
              int *cluster_cnt;
              p = (pixel *)malloc(lst_len * sizeof(pixel));
              cluster_cnt = (int *)malloc(lst_len * sizeof(int)); // max num of clusters
              for (l=0; l<lst_len; l++) {
	        cluster_cnt[l] = -1;  // initial value
              }

              // fill up the 1D array of structure
              for (l=0; l<lst_len; l++) {
                mm = list_id(lt, ln, nlat, l);
                p[l].time = list_tim(lt, ln, nlat, l);
                p[l].val = val[mm];
	        p[l].dist = list_dst(lt, ln, nlat, l);
	        // printf("-- time: %f\n", p[l].time);
	        // printf("-- val: %f\n", p[l].val);
	        // printf("-- dist: %f\n", p[l].dist);
              }

              // qsort the 1D array of pixels by time
              qsort(p, lst_len, sizeof(pixel), comp);

              num_clusters = 1;  // default: pixels all belong to 1 cluster
              int c_cnt = 0;   // keep track of count for each cluster
	      // printf("------------\n");
              c_cnt = 0;
              // search for time gap (>90 mins), which means different paths
              for (l=0; l<lst_len-1; l++) {
                c_cnt ++;
                # if DEBUG == 1
	        // printf("time: %f\n", p[l].time);
	        // printf("val: %f\n", p[l].val);
	        // printf("dist: %f\n", p[l].dist);
                #endif
                // found time gap
                if ((p[l+1].time - p[l].time) > gap) {
                  cluster_cnt[num_clusters-1] = c_cnt; // this cluster cnt
                  num_clusters ++;
                  c_cnt = 0;   // reset for next cluster
                  // printf("****** found gap > 90 mins\n");
                }
              }
              // take care of the last pixel
              c_cnt ++;
              cluster_cnt[num_clusters-1] = c_cnt; // last cluster cnt
              # if DEBUG == 1
	      // printf("time: %f\n", p[lst_len-1].time);
	      // printf("val: %f\n", p[lst_len-1].val);
	      // printf("dist: %f\n", p[lst_len-1].dist);
              #endif

	      // printf("num_clusters: %d\n", num_clusters);
              for (l=0; l<num_clusters; l++) {
	        // printf("cluster: %d has %d pixels\n", l, cluster_cnt[l]);
              }
	      // printf("------------\n\n");

              // figure out which cluster(s) is (are) useful
              // find the closest (in time) 2 clusters (or, 2 paths) 
              // for a user given time, if they span the user given time, 
              // do time interpolation, otherwise, take the closest

              // average time of each cluster
              double *average_t;
              average_t = (double *) malloc(num_clusters * sizeof(double));

              int cnt1 = -1;
              // loop over clusters, and get average time for each
              int c;
              for (c=0; c<num_clusters; c++) {
                average_t[c] = 0.0;
                // loop over pixels in a cluster
                for (l=0; l<cluster_cnt[c]; l++) {
                  cnt1 ++;
                  average_t[c] += p[cnt1].time;
                }
                average_t[c] /= cluster_cnt[c];
              }

              // find the closest (in time) 2 clusters (or, 2 paths)
              // (can only find 1 if there is only one cluster)
              int cl0 = -1, cl1 = -1;
              double dt0 = DBL_MAX, dt1 = DBL_MAX;

              // find the closest
              for (c=0; c<num_clusters; c++) {
                if (dt0 > abs(t0 - average_t[c])) {
                  dt0 = abs(t0 - average_t[c]);
                  cl0 = c;
                }
              }

              // find the 2nd closest if any
              if (num_clusters >= 2 ) {
                for (c=0; c<num_clusters; c++) {
                  if (c != cl0 && dt1 > abs(t0 - average_t[c])) {
                    dt1 = abs(t0 - average_t[c]);
                    cl1 = c;
                  }
                }
              }

              // printf("cl0: %d, cl1: %d\n", cl0, cl1);

              // determine if t0 is in the middle of the 2 clusters
              if (num_clusters >= 2 && t0 > average_t[cl0] && t0 < average_t[cl1]) {
                # if DEBUG == 1
                // printf("t0 in between cl0 and cl1. t0: %f, t[cl0]: %f, t[cl1]: %f\n", t0, average_t[cl0], average_t[cl1]);
                #endif
                v1 = nearneighbor_averaging(p, cl0, cluster_cnt[cl0], r0);
                v2 = nearneighbor_averaging(p, cl1, cluster_cnt[cl1], r0);
                wt = (t0-average_t[cl0])/(average_t[cl1]-average_t[cl0]);
                // printf("v1: %f, v2: %f, wt: %f\n", v1, v2, wt);
                if (!isnan(v1) && !isnan(v2)) {
                  v = (1-wt) * v1 + wt * v2;
                }
                else if (!isnan(v1) && isnan(v2)) {
                  v = v1;
                }
                else if (isnan(v1) && !isnan(v2)) {
                  v = v2;
                }
                else {
                  v = NAN;
                }
              } else if (num_clusters >= 2 && t0 > average_t[cl1] && t0 < average_t[cl0]) {
                # if DEBUG == 1
                // printf("t0 in between cl1 and cl0. t0: %f, t[cl1]: %f, t[cl0]: %f\n", t0, average_t[cl1], average_t[cl0]);
                #endif
                v1 = nearneighbor_averaging(p, cl1, cluster_cnt[cl1], r0);
                v2 = nearneighbor_averaging(p, cl0, cluster_cnt[cl0], r0);
                wt = (t0-average_t[cl1])/(average_t[cl0]-average_t[cl1]);
                // printf("v1: %f, v2: %f, wt: %f\n", v1, v2, wt);
                if (!isnan(v1) && !isnan(v2)) {
                  v = (1-wt) * v1 + wt * v2;
                }
                else if (!isnan(v1) && isnan(v2)) {
                  v = v1;
                }
                else if (isnan(v1) && !isnan(v2)) {
                  v = v2;
                }
                else {
                  v = NAN;
                }
              } else {  // num_clusters can be 1 or more
                # if DEBUG == 1
                // printf("t0 closest to cl0. t0: %f, t[cl0]\n", t0, average_t[cl0]);
                #endif
                v = nearneighbor_averaging(p, cl0, cluster_cnt[cl0], r0);
              }
              // printf("v: %f\n", v);

              free(p);
              free(cluster_cnt);
              free(average_t);

	      value[ln*nlat + lt] = v;
	    }  // distance-time-weighted average
	  }  // for ln
	}  // for lt

	free(grid_1d_lat);
	free(grid_1d_lon);
	free(lst);
	free(dst);
	free(tim);
	free(len);

        // write out in binary
        clock_t begin = clock();

        // FILE *output_file_bin = fopen("/tmp/output.bin", "wb");
        printf("xyz_file_name: %s\n", xyz_file_name);
        FILE *output_file_bin = fopen(xyz_file_name, "wb");
        if (output_file_bin == NULL) {
          printf("****** Error: binary file open for write failed!\n");
          printf("------- end of mergein() ----\n");

	  return 0;
        }

        for (lt=0; lt<nlat; lt++) {
          for (ln=0; ln<nlon; ln++) {
            if (value[ln*nlat + lt] != NAN) {
              fwrite(&grid_lon[ln*nlat + lt], sizeof(double), 1, output_file_bin);
              fwrite(&grid_lat[ln*nlat + lt], sizeof(double), 1, output_file_bin);
              fwrite(&value[ln*nlat + lt], sizeof(double), 1, output_file_bin);
            }
	  }  // for ln
	}  // for lt

        clock_t end = clock();
        printf("Elapsed time for binary output: %f seconds\n", (double)(end - begin) / CLOCKS_PER_SEC);

        fclose(output_file_bin);

        printf("------- end of mergein() ----\n");

	return 0;
}

