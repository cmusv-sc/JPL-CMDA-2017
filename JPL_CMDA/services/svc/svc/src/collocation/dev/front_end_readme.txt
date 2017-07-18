Notes on implementing Front Ends

A front end provides the conversion from an instrument specific data set format to a
common format suitable for processing by the middle end.

There are two upper edge classes that provide an interface to the middle-end, 
a dset class and a front_end class. The dataset class provides the interface for a 
virtual instrument type (e.g. cloudsat).  The front end type provide the data interface 
for a specific file.

In addition, there is a dataset registry which maps a "virtual" instrument name to its
corresponding dataset object.  Later, a front_end object can be obtained to access
data in a particular file for that instrument.

The normal usage is:
- get a dataset by name from the registry
- use the dataset to perform instrument specific actions
- use the dataset to attach to a specific data source (i.e. file)
- use the front end to get data from the data source

Front ends developed prior to the dataset interface will use the unnamed dataset object,
dset_nemo.  Code that was distributed in various upper layer modules has been collected 
and encapsulated in through the dset_nemo object.

New front ends can use the dset and front end interfaces.

To implement a new virtual instrument:
- Insert a new registration entry at the end of DatasetRegistry.py
- Create a dataset class with the prefix dset_ and derived from the class dset_abstract
- Create a front end class with the prefix front_end and derived from the class front_end_abstract
- Implement methods to support dataset specific functions
- Create an XML configuration file with your dataset name, date ranges, input dirs, and output dirs

At this point, you should be able to sucessfully run "python build_file_list.py dsetname" 
with your new dataset name as its argument

- Implement methods to access a data source
- Add code to register the dataset and test source file in front_end_test_driver.py

At this point, you should be able to sucessfully run "python front_end_test_driver.py dsetname"
with your new dataset name as its argument

Once these steps have been completed sucessfully, you are ready to run an end to end test.

===================================
Notes on Datasets:
--> ecmwf_idaily_surface_ncar
This is a straightforward front end that processes a single ei.oper.an.sfc.regn128sc.yyyymmddhh.nc file.

--> ecmwf_idaily_plevels_ncar
The ei.oper.an.pl.regn128sc.yyyymmddhh.nc file and ei.oper.an.pl.regn128pl.yyyymmddhh.nc data are combined to supply
the middle end with a single "virtual" file.

--> ecmwf_yotc_oper_an_pl_ncar_X
There are 4 frontends to process the yotc operational analysis at pressure level data.

ecmwf_yotc_oper_an_pl_ncar_0 processes the yt_oper_an_pl_yyyymmdd00_000_018_060128_203128_400.nc files that contain
data generated prior to 1/26/2010.

ecmwf_yotc_oper_an_pl_ncar_1 processes the yt_oper_an_pl_yyyymmdd00_000_018_129128_157128_799.nc files that contain
data generated prior to 1/26/2010.  The geolocation information is contained in yt_oper_an_pl_geoinfo_799.nc.  
The 799 files are gridded with half as many longitude values as the 400 files.

ecmwf_yotc_oper_an_pl_ncar_2 processes the yt_oper_an_pl_yyyymmdd00_000_018_060128_203128_640.nc files that contain
data generated after 1/26/2010.  The 640 files have the same parameters as the 400 files, but are on a finer grid.

ecmwf_yotc_oper_an_pl_ncar_3 processes the yt_oper_an_pl_yyyymmdd00_000_018_129128_157128_1279.nc files that contain
data generated after 1/26/2010.  The geolocation information is contained in yt_oper_an_pl_geoinfo_1279.nc.  
The 1279 files are gridded with half as many longitude values as the 640 files.

--> ecmwf_yotc_oper_an_pl_ncar_X
There are 4 frontends to process the yotc operational analysis for model level data.


===================================
To Do:
The front end for ecmwf_yotc_oper_an_ml for the 799 and 1279 datasets is incomplete.  
The geo-information is not present in the data files so it is loaded from yt_oper_an_ml_geoinfo_xxx.nc
in the main source data directory.  
There were some format changes, so I need to figure out which files are needed and what format the data is in.




