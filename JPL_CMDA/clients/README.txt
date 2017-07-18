* To test the twoDimClimatology service, use a browser to open:
http://oscar2.jpl.nasa.gov:8088/twoDimClimatology/display?model=ukmo&data=/static/ts_Amon_HadGEM2-A_amip_r1i1p1_197809-200811.nc&image=/static/Fukmo_ts.jpeg

curl "http://cmacws.jpl.nasa.gov:8090/svc/twoDimSlice3D?model=UKMO_HadGEM2-ES&var=hus&start_time=199001&end_time=199512&pr=80000&lon1=0&lon2=20&lat1=-29&lat2=29&months=1,2,3,4,5,6,7,8,9,10,11,12"

curl "http://cmacws.jpl.nasa.gov:8090/svc/twoDimSlice3D?model=UKMO_HadGEM2-ES&var=ta&start_time=199001&end_time=199512&pr=80000&lon1=0&lon2=20&lat1=-29&lat2=29&months=1,2,3,4,5,6,7,8,9,10,11,12"

curl "http://cmacws4.jpl.nasa.gov:8090/svc/time_bounds?source=argo/argo&var=os"
curl "http://cmacws4.jpl.nasa.gov:8090/svc/time_bounds?source=nasa/modis&var=clt"
