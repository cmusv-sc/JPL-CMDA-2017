#define pi 3.14159265357
// mean radius of Earth in km
#define R 6371.0

double degree_to_radian(double degree);
double get_Cartesian_distance(double lat1, double lon1, double lat2, double lon2);
double get_Haversine_distance(double lat1, double lon1, double lat2, double lon2);
double get_4D_distance(double lat1, double lon1, double lat2, double lon2, double t1, double t2, double w);
