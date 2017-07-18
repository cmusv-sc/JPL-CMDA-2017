#!/bin/bash
curl -H "Content-Type: application/json" -X POST -d '{"model":"NCC_NORESM","var":"ta","start_time":"199001","end_time":"200012","lon1":"0","lon2":"360","dlon":"4","lat1":"-90","lat2":"90","dlat":"4","plev":"100000,80000,50000,30000,20000,10000"}' http://cmacws4.jpl.nasa.gov:8090/svc/regridAndDownload
