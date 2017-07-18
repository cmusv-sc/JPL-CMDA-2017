 /* distance.i */
 %module distance
 %{
 /* Put header files here or function declarations like below */
 extern double R;
 extern double degree_to_radian(double degree);
 extern double get_Cartesian_distance(double lat1, double lon1, double lat2, double lon2);
 extern double get_Haversine_distance(double lat1, double lon1, double lat2, double lon2);
 %}

 extern double R;
 extern double degree_to_radian(double degree);
 extern double get_Cartesian_distance(double lat1, double lon1, double lat2, double lon2);
 extern double get_Haversine_distance(double lat1, double lon1, double lat2, double lon2);
