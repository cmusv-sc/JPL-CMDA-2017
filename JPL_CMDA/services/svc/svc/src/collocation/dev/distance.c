#include <math.h>
#include <stdio.h>

#define pi 3.14159265357

// # mean radius of Earth in km
double R = 6371.0;

double degree_to_radian(double degree);
double get_Cartesian_distance(double lat1, double lon1, double lat2, double lon2);
double get_Haversine_distance(double lat1, double lon1, double lat2, double lon2);

int main () {
    int i;
    double dis;

    // printf("Start calculating ...\n");

    for(i=0; i<3600000; i++) {
    // for(i=0; i<5; i++) {
	// dis = get_Cartesian_distance(i+1, i+10, i+100, i+110);
	// printf("Cartesian: %.8lf\n", dis);
	dis = get_Haversine_distance(i+1, i+10, i+100, i+110);
	// printf("Haversine: %.8lf\n", dis);
    }

}


double degree_to_radian(double degree) {
    return degree*pi/180.0;
}


double get_Cartesian_distance(double lat1, double lon1, double lat2, double lon2) {
    double lat1r, lon1r, lat2r, lon2r;
    double half_pi;
    double x1, y1, z1, x2, y2, z2;

    // # convert from degree to radian
    lat1r = degree_to_radian(lat1);
    lon1r = degree_to_radian(lon1);
    lat2r = degree_to_radian(lat2);
    lon2r = degree_to_radian(lon2);

    half_pi = pi/2.0;

    x1 = R * sin(half_pi-lat1r) * cos(lon1r);
    y1 = R * sin(half_pi-lat1r) * sin(lon1r);
    z1 = R * cos(half_pi-lat1r);

    x2 = R * sin(half_pi-lat2r) * cos(lon2r);
    y2 = R * sin(half_pi-lat2r) * sin(lon2r);
    z2 = R * cos(half_pi-lat2r);

    return sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2) + (z1-z2)*(z1-z2));
}


//# from http://www.movable-type.co.uk/scripts/latlong.html
double get_Haversine_distance(double lat1, double lon1, double lat2, double lon2) {
    double dLat, dLon, a, c, d;

    dLat = degree_to_radian(lat2-lat1);
    dLon = degree_to_radian(lon2-lon1);
    a = sin(dLat/2)*sin(dLat/2) + cos(degree_to_radian(lat1))*cos(degree_to_radian(lat2))*sin(dLon/2)*sin(dLon/2);
    c = 2*atan(sqrt(a)/sqrt(1-a));
    d = R * c;

    return d;
}

