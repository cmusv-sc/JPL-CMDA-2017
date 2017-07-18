
import calendar
import datetime
import numpy as N
import os.path
import sys

import front_end_cloudsat as FEC
import front_end_amsr as FEA
import front_end_ceres as FECERES
import front_end_airs as FEAIRS
import front_end_caliop_05km_alay as FE_CALIOP_05KMALAY
import front_end_caliop_05km_clay as FE_CALIOP_05KMCLAY
import front_end_caliop_40km_apro as FE_CALIOP_40KMAPRO
import front_end_caliop_05km_cpro as FE_CALIOP_05KMCPRO
import front_end_caliop_vfm as FE_CALIOP_VFM
import front_end_mls_temp as FEMLS_TEMP
import front_end_mls_iwc as FEMLS_IWC
import front_end_mls_h2o as FEMLS_H2O
import front_end_mls_co as FEMLS_CO
import front_end_mls_o3 as FEMLS_O3
import front_end_mls_hno3 as FEMLS_HNO3
import front_end_modis_cloud_5km as FEMODIS_CLOUD_5KM
import front_end_modis_cloud_1km as FEMODIS_CLOUD_1KM
import front_end_modis_aerosol as FEMODIS_AEROSOL
import front_end_ecmwf_idaily_surface as FEECMWF_IDAILY_SURFACE
import front_end_ecmwf_idaily_plevels as FEECMWF_IDAILY_PLEVELS
import front_end_ecmwf_yotc_aos_1p5deg as FEECMWF_YOTC_AOS_1P5DEG
### import front_end_ecmwf_yotc_oaml_1p5deg as FEECMWF_YOTC_OAML_1P5DEG
### import front_end_ecmwf_yotc_oapl_1p5deg as FEECMWF_YOTC_OAPL_1P5DEG
import front_end_ecmwf_yotc_aos_0p25deg as FEECMWF_YOTC_AOS_0P25DEG
import front_end_ecmwf_yotc_oaml_0p25deg as FEECMWF_YOTC_OAML_0P25DEG
import front_end_ecmwf_yotc_oapl_0p25deg as FEECMWF_YOTC_OAPL_0P25DEG

#
# finding a dataset using a name has been moved to dataset_registry
#


# mean radius of Earth in km
R = 6371
NAN = -999

def date_to_julian_day(year, month, day):
    try:
	# Get first day of the year
	firstday = datetime.date(year, 1, 1)
	thisday  = datetime.date(year, month, day)
	# Calculate the difference
	diff = thisday - firstday
	return diff.days+1
    except ValueError:
	raise ValueError
# end of date_to_julian_day()


def julian_day_to_date(year, julian_day):
    try:
	# Get delta
	delta = datetime.timedelta(days=julian_day-1)
	firstday = datetime.date(year, 1, 1)
	# Add delta to 1st day of year
	return firstday+delta
    except ValueError:
	raise ValueError
# end of julian_day_to_date()


def unix_time_to_date(unix_time):
    return datetime.datetime(1970,1,1, 0, 0, 0) + datetime.timedelta(seconds=int(unix_time))


def hours_since_19th_century_to_unix_time(inhours):
    date_time = datetime.datetime(1800,1,1, 0, 0, 0) + datetime.timedelta(hours=int(inhours))
    return datetime_to_unix_time(date_time)


def hours_since_20th_century_to_unix_time(inhours):
    date_time = datetime.datetime(1900,1,1, 0, 0, 0) + datetime.timedelta(hours=int(inhours))
    return datetime_to_unix_time(date_time)
    

def datetime_to_unix_time(date_time):

    # Get a time tuple corresponding to the date at 00:00:00
    ttuple = date_time.date().timetuple()

    # Adjust for the time elapsed singe midnight
    ttuple = (date_time.year, date_time.month, date_time.day,
              date_time.hour, date_time.minute, date_time.second, 0, 0, 0)
    
    # Convert time tuple to unix time
    ut = calendar.timegm(ttuple)
    
    return(ut)
# end of datetime_to_unix_time()

# different data products may need to filter filenames using different substrings
# obsolete, new data set front ends will create a dataset container and make entry in get_dataset_container
def filename_filter(datarootdir, filename):
    ###print 'filename_filter - datarootdir = ', datarootdir, ', filename = ', filename, len(filename)
    # to get CloudSat, non-zip files
    if datarootdir.find('cloudsat') >= 0:
        return filename.find("_CS_") >= 0 and filename.find(".zip") == -1
    # to get version 5 final product files (no real time, no 3-day, no monthly)
    elif datarootdir.find('amsr') >= 0:
        return filename.find("amsr") >=0 and filename.find(".gz") >= 0 and len(filename) == 19 and filename.find("rt") == -1
    elif datarootdir.find('ceres') >= 0:
        return filename.find("CER_SSF") >=0 and (len(filename) == 75 or len(filename) == 50)
    elif datarootdir.find('airs') >= 0:
	print filename
        ### return filename.find('RetStd') >= 0 and (len(filename) == 56 or len(filename) == 55)
        return filename.endswith('.hdf') and filename.find('RetStd') >= 0 and filename.find('L3') < 0
    elif datarootdir.find('05kmALayer') >= 0:       # Caliop 05KM Aerosol Layer Product
        return filename.find('05kmALay') >= 0 and len(filename) == 56
    elif datarootdir.find('05kmCLayer') >= 0:       # Caliop 05KM Cloud Layer Product
        return filename.find('05kmCLay') >= 0 and len(filename) == 56
    elif datarootdir.find('05kmCProfile') >= 0:     # Caliop 05KM Cloud Profile Product
        return filename.find('05kmCPro') >= 0 and len(filename) == 56
    elif datarootdir.find('40kmAProfile') >= 0:     # Caliop 40KM Aerosol Profile Product
        return filename.find('40kmAPro') >= 0 and len(filename) == 59
    elif datarootdir.find('VFM') >= 0:              # Caliop Vertical Feature Mask Product
        return filename.find('VFM') >= 0 and len(filename) == 51
    elif datarootdir.find('mls-temp') >= 0:         # MLS Temperature product
        return filename.find('MLS-Aura_L2GP-Temperature') >= 0 and len(filename) == 49
    elif datarootdir.find('mls-iwc') >= 0:          # MLS Temperature product
        return filename.find('MLS-Aura_L2GP-IWC') >= 0 and len(filename) == 41
    elif datarootdir.find('mls-h2o') >= 0:          # MLS Temperature product
        return filename.find('MLS-Aura_L2GP-H2O') >= 0 and len(filename) == 41
    elif datarootdir.find('mls-co') >= 0:           # MLS Temperature product
        return filename.find('MLS-Aura_L2GP-CO') >= 0 and len(filename) == 40
    elif datarootdir.find('mls-o3') >= 0:           # MLS Temperature product
        return filename.find('MLS-Aura_L2GP-O3') >= 0 and len(filename) == 40
    elif datarootdir.find('mls-hno3') >= 0:         # MLS Temperature product
        return filename.find('MLS-Aura_L2GP-HNO3') >= 0 and len(filename) == 42
    elif datarootdir.find('MYD04_L2') >= 0:         # Modis aerosol product MYD06 5km
        return filename.find('MYD04_L2') >= 0 and len(filename) == 44
    elif datarootdir.find('MYD06_L2_5KM') >= 0:         # Modis cloud product MYD06 5km
        return filename.find('MYD06_L2') >= 0 and len(filename) == 44
    #elif datarootdir.find('MYD06_L2_1KM') >= 0:     # Modis cloud product MYD06 1km
    elif datarootdir.find('modis-cloud-1km') >= 0:     # Modis cloud product MYD06 1km
        return filename.find('MYD06_L2') >= 0 and len(filename) == 44
    elif datarootdir.find('idaily-surface') >= 0:   # ECMWF Interim Daily Surface
        return filename.find('interim-daily-surface') >= 0 and len(filename) == 41
    elif datarootdir.find('idaily-plevels') >= 0:   # ECMWF Interim Daily Pressure Levels
        return filename.find('interim-daily-plevels') >= 0 and len(filename) == 41
    elif datarootdir.find('yotc-oaml-1.5deg') >= 0: # ECMWF YOTC, 1.5 Degree Operational Analysis Model Levels
        return filename.find('yotc-oaml-1.5deg') >= 0 and len(filename) == 30
    elif datarootdir.find('yotc-oapl-1.5deg') >= 0: # ECMWF YOTC, 1.5 Degree Operational Analysis Pressure Levels
        return filename.find('yotc-oapl-1.5deg') >= 0 and len(filename) == 30
    elif datarootdir.find('yotc-aos-1.5deg') >= 0:  # ECMWF YOTC, 1.5 Degree Analysis, Operational Surface
        return filename.find('yotc-aos-1.5deg') >= 0 and len(filename) == 29
    elif datarootdir.find('yotc-oaml-0.25deg') >= 0: # ECMWF YOTC, 0.25 Degree Operational Analysis Model Levels
        return filename.find('yotc-oaml-0.25deg') >= 0 and len(filename) == 31
    elif datarootdir.find('yotc-oapl-0.25deg') >= 0: # ECMWF YOTC, 0.25 Degree Operational Analysis Pressure Levels
        return filename.find('yotc-oapl-0.25deg') >= 0 and len(filename) == 31
    elif datarootdir.find('yotc-aos-0.25deg') >= 0:  # ECMWF YOTC, 0.25 Degree Analysis, Operational Surface
        return filename.find('yotc-aos-0.25deg') >= 0 and len(filename) == 30
    elif datarootdir.find('era_interim_analysis_surface') >= 0:  # ECMWF era_interim_analysis_surface
	### print 'len(filename): ', len(filename)
        return filename.find('ei.oper.an.sfc') >= 0 and len(filename) == 38
    elif datarootdir.find('era_interim_analysis_level') >= 0:  # ECMWF era_interim_analysis_level
        return filename.find('ei.oper.an.pl') >= 0 and len(filename) == 37
    else:
        return None
# end of filename_filter()


# different data products may need to filter dirnames using different substrings
# obsolete, new data set front ends will create a dataset container and make entry in get_dataset_container
def dir_filter(datarootdir, dirname):
    #print '\n inside dir_filter: root=', datarootdir, 'dir=', dirname
    # to avoid "prev-hdf"
    if datarootdir.find('cloudsat') >= 0:
        return dirname.find("prev-hdf") == -1
    elif datarootdir.find('amsr') >= 0:
        # to do nothing for now
        return True
    elif datarootdir.find('ceres') >= 0:
        # to do nothing for now
        return True
    elif datarootdir.find('airs') >= 0:
        #return dirname.find('airx2ret') >= 0        # AIRS in cumulus
	return True	                             # in order to make it work for both cumulus and cmacws
    elif datarootdir.find('05kmALayer') >= 0:       # Caliop
        # todo nothing for now
        return True
    elif datarootdir.find('05kmCLayer') >= 0:       # Caliop
        # todo nothing for now
        return True
    elif datarootdir.find('05kmCProfile') >= 0:     # Caliop
        # todo nothing for now
        return True
    elif datarootdir.find('40kmAProfile') >= 0:     # Caliop
        # todo nothing for now
        return True
    elif datarootdir.find('VFM') >= 0:              # Caliop
        # todo nothing for now
        return True
    elif datarootdir.find('mls-temp') >= 0:         # MLS
        # todo nothing for now
        return True
    elif datarootdir.find('mls-iwc') >= 0:          # MLS
        # todo nothing for now
        return True
    elif datarootdir.find('mls-h2o') >= 0:          # MLS
        # todo nothing for now
        return True
    elif datarootdir.find('mls-co') >= 0:           # MLS
        # todo nothing for now
        return True
    elif datarootdir.find('mls-o3') >= 0:           # MLS
        # todo nothing for now
        return True
    elif datarootdir.find('mls-hno3') >= 0:         # MLS
        # todo nothing for now
        return True
    elif datarootdir.find('MYD04_L2') >= 0:         # MODIS Aerosol 5km
        # todo nothing for now
        return True
    elif datarootdir.find('MYD06_L2_5KM') >= 0:     # MODIS Cloud 5km
        # todo nothing for now
        return True
    #elif datarootdir.find('MYD06_L2_1KM') >= 0:     # MODIS Cloud 1km
    elif datarootdir.find('modis-cloud-1km') >= 0:     # MODIS Cloud 1km
        # todo nothing for now
        return True
    elif datarootdir.find('idaily-surface') >= 0:   # ECMWF Interim Daily Surface
        # todo nothing for now
        return True
    elif datarootdir.find('idaily-plevels') >= 0:   # ECMWF Interim Daily Pressure Levels
        # todo nothing for now
        return True
    elif datarootdir.find('yotc-oaml-1.5deg') >= 0: # ECMWF YOTC, 1.5 Degree Operational Analysis Model Levels
        # todo nothing for now
        return True
    elif datarootdir.find('yotc-oapl-1.5deg') >= 0: # ECMWF YOTC, 1.5 Degree Operational Analysis Pressure Levels
        # todo nothing for now
        return True
    elif datarootdir.find('yotc-aos-1.5deg') >= 0:  # ECMWF YOTC, 1.5 Degree Analysis, Operational Surface
        # todo nothing for now
        return True
    elif datarootdir.find('yotc-oaml-0.25deg') >= 0: # ECMWF YOTC, 0.25 Degree Operational Analysis Model Levels
        # todo nothing for now
        return True
    elif datarootdir.find('yotc-oapl-0.25deg') >= 0: # ECMWF YOTC, 0.25 Degree Operational Analysis Pressure Levels
        # todo nothing for now
        return True
    elif datarootdir.find('yotc-aos-0.25deg') >= 0:  # ECMWF YOTC, 0.25 Degree Analysis, Operational Surface
        # todo nothing for now
        return True
    elif datarootdir.find('era_interim_analysis_surface') >= 0:  # ECMWF era_interim_analysis_surface
        # todo nothing for now
	### print 'dir_filter returned True'
        return True
    elif datarootdir.find('era_interim_analysis_level') >= 0:  # ECMWF era_interim_analysis_level
        # todo nothing for now
	### print 'dir_filter returned True'
        return True
    else:
        return None
# end of dir_filter()

# obsolete, new data set front ends will create a dataset container and make entry in get_dataset_container
def get_start_time(datarootdir, filename):
    if datarootdir.find('cloudsat') >= 0:
        y = int(filename[0:4])
        julian = int(filename[4:7])
        h = int(filename[7:9])
        m = int(filename[9:11])
        s = int(filename[11:13])
        d1 = julian_day_to_date(y, julian)
        diff = datetime.timedelta(minutes=1) # CloudSat adds ~20 sec of data to the beginning and end
        return datetime.datetime(y, d1.month, d1.day, h, m, s) - diff
    elif datarootdir.find('amsr') >= 0:
        y = int(filename[6:10])
        mon = int(filename[10:12])
        day = int(filename[12:14])
        return datetime.datetime(y,mon,day)
    elif datarootdir.find('ceres') >= 0:
	"""
        y = int(filename[65:69])
        mon = int(filename[69:71])
        day = int(filename[71:73])
        h = int(filename[73:75])
	"""

	l1 = len(filename)
        y = int(filename[l1-10:l1-6])
        mon = int(filename[l1-6:l1-4])
        day = int(filename[l1-4:l1-2])
        h = int(filename[l1-2:l1])
        m = 0
        s = 0
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('airs') >= 0:
        y = int(filename[5:9])
        mon = int(filename[10:12])
        day = int(filename[13:15])
        granule = int(filename[16:19])
        h = 0
        m = 5
        s = 25
        # Should add one leap second for data on or after 12/31/2005
        # and additional leap seconds as they accur thereafter.  See
        # page 13 of the "README Document for AIRS Level-2 Version 005
        # Standard Products".  Without this, there is a very slight
        # drift.
        return datetime.datetime(y,mon,day, h, m, s)+datetime.timedelta(minutes=6 * (granule - 1))
    elif datarootdir.find('05kmALayer') >= 0:               # Caliop
        y = int(filename[31:35])
        mon = int(filename[36:38])
        day = int(filename[39:41])
        h = int(filename[42:44])
        m = int(filename[45:47])
        s = int(filename[48:50])
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('05kmCLayer') >= 0:               # Caliop
        y = int(filename[31:35])
        mon = int(filename[36:38])
        day = int(filename[39:41])
        h = int(filename[42:44])
        m = int(filename[45:47])
        s = int(filename[48:50])
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('05kmCProfile') >= 0:             # Caliop
        y = int(filename[31:35])
        mon = int(filename[36:38])
        day = int(filename[39:41])
        h = int(filename[42:44])
        m = int(filename[45:47])
        s = int(filename[48:50])
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('40kmAProfile') >= 0:             # Caliop
        y = int(filename[34:38])
        mon = int(filename[39:41])
        day = int(filename[42:44])
        h = int(filename[45:47])
        m = int(filename[48:50])
        s = int(filename[51:53])
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('VFM') >= 0:                      # Caliop
        y = int(filename[26:30])
        mon = int(filename[31:33])
        day = int(filename[34:36])
        h = int(filename[37:39])
        m = int(filename[40:42])
        s = int(filename[43:45])
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('mls-temp') >= 0:                 # MLS
        y    = int(filename[37:41])
        jday = int(filename[42:45])
        date = julian_day_to_date(y, jday)
        mon  = date.month
        day  = date.day
        h = 0
        m = 0
        s = 0
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('mls-iwc') >= 0:                  # MLS
        y    = int(filename[29:33])
        jday = int(filename[34:37])
        date = julian_day_to_date(y, jday)
        mon  = date.month
        day  = date.day
        h = 0
        m = 0
        s = 0
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('mls-h2o') >= 0:                  # MLS
        y    = int(filename[29:33])
        jday = int(filename[34:37])
        date = julian_day_to_date(y, jday)
        mon  = date.month
        day  = date.day
        h = 0
        m = 0
        s = 0
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('mls-co') >= 0:                   # MLS
        y    = int(filename[28:32])
        jday = int(filename[33:36])
        date = julian_day_to_date(y, jday)
        mon  = date.month
        day  = date.day
        h = 0
        m = 0
        s = 0
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('mls-o3') >= 0:                   # MLS
        y    = int(filename[28:32])
        jday = int(filename[33:36])
        date = julian_day_to_date(y, jday)
        mon  = date.month
        day  = date.day
        h = 0
        m = 0
        s = 0
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('mls-hno3') >= 0:                 # MLS
        y    = int(filename[30:34])
        jday = int(filename[35:38])
        date = julian_day_to_date(y, jday)
        mon  = date.month
        day  = date.day
        h = 0
        m = 0
        s = 0
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('MYD04_L2') >= 0:                 # MODIS Aerosol 5km
        y    = int(filename[10:14])
        jday = int(filename[14:17])
        date = julian_day_to_date(y, jday)
        mon  = date.month
        day  = date.day
        h    = int(filename[18:20])
        m    = int(filename[20:22])
        s = 0
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('MYD06_L2_5KM') >= 0:              # MODIS Cloud 5km
        y    = int(filename[10:14])
        jday = int(filename[14:17])
        date = julian_day_to_date(y, jday)
        mon  = date.month
        day  = date.day
        h    = int(filename[18:20])
        m    = int(filename[20:22])
        s = 0
        return datetime.datetime(y,mon,day, h, m, s)
    #elif datarootdir.find('MYD06_L2_1KM') >= 0:              # MODIS Cloud 1km
    elif datarootdir.find('modis-cloud-1km') >= 0:              # MODIS Cloud 1km
        y    = int(filename[10:14])
        jday = int(filename[14:17])
        date = julian_day_to_date(y, jday)
        mon  = date.month
        day  = date.day
        h    = int(filename[18:20])
        m    = int(filename[20:22])
        s = 0
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('idaily-surface') >= 0:            # ECMWF Interim daily, Surface
        y = int(filename[28:32])
        mon = int(filename[33:35])
        day = int(filename[36:38])
        h = 0
        m = 0
        s = 0
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('idaily-plevels') >= 0:            # ECMWF Interim daily, Pressure Levels
        y = int(filename[28:32])
        mon = int(filename[33:35])
        day = int(filename[36:38])
        h = 0
        m = 0
        s = 0
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('yotc-oaml-1.5deg') >= 0:            # ECMWF YOTC, Operational Analysis Model Levels
        y = int(filename[17:21])
        mon = int(filename[22:24])
        day = int(filename[25:27])
        h = 0
        m = 0
        s = 0
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('yotc-oapl-1.5deg') >= 0:            # ECMWF YOTC, Operational Analysis Pressure Levels
        y = int(filename[17:21])
        mon = int(filename[22:24])
        day = int(filename[25:27])
        h = 0
        m = 0
        s = 0
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('yotc-aos-1.5deg') >= 0:             # ECMWF YOTC, Analysis, Operational Surface
        y = int(filename[16:20])
        mon = int(filename[21:23])
        day = int(filename[24:26])
        h = 0
        m = 0
        s = 0
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('yotc-oaml-0.25deg') >= 0:            # ECMWF YOTC, Operational Analysis Model Levels
        y = int(filename[18:22])
        mon = int(filename[23:25])
        day = int(filename[26:28])
        h = 0
        m = 0
        s = 0
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('yotc-oapl-0.25deg') >= 0:            # ECMWF YOTC, Operational Analysis Pressure Levels
        y = int(filename[18:22])
        mon = int(filename[23:25])
        day = int(filename[26:28])
        h = 0
        m = 0
        s = 0
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('yotc-aos-0.25deg') >= 0:             # ECMWF YOTC, Analysis, Operational Surface
        y = int(filename[17:21])
        mon = int(filename[22:24])
        day = int(filename[25:27])
        h = 0
        m = 0
        s = 0
        return datetime.datetime(y,mon,day, h, m, s)-datetime.timedelta(hours=3)
    elif datarootdir.find('era_interim_analysis_surface') >= 0: # ECMWF era_interim_analysis_surface
        y = int(filename[25:29])
        mon = int(filename[29:31])
        day = int(filename[31:33])
        h = int(filename[33:35])
        m = 0
        s = 0
        return datetime.datetime(y,mon,day, h, m, s)
    elif datarootdir.find('era_interim_analysis_level') >= 0: # ECMWF era_interim_analysis_level
        y   = filename[24:28]
        mon = filename[28:30]
        day = filename[30:32]
        h   = filename[32:34]
        m   = 0
        s   = 0
        ###print 'get_start_time - plevels -', datarootdir, filename, y, mon, day, h
        return datetime.datetime(int(y),int(mon),int(day), int(h), m, s)
    else:
	return None
# end of get_start_time()

# obsolete, new data set front ends will create a dataset container and make entry in get_dataset_container
def get_end_time(datarootdir, filename):
    if datarootdir.find('cloudsat') >= 0:
        start = get_start_time(datarootdir, filename)
        diff1 = datetime.timedelta(minutes=98.97) # One CloudSat orbit takes 98.97 minutes
        diff2 = datetime.timedelta(minutes=2) # CloudSat adds ~20 sec of data to the beginning and end
        return start+diff1+diff2
    elif datarootdir.find('amsr') >= 0:
        return get_start_time(datarootdir, filename)+datetime.timedelta(hours=24)
    elif datarootdir.find('ceres') >= 0:
        return get_start_time(datarootdir, filename)+datetime.timedelta(hours=1)
    elif datarootdir.find('airs') >= 0:
        return get_start_time(datarootdir, filename)+datetime.timedelta(minutes=6)
    elif datarootdir.find('05kmALayer') >= 0:               # Caliop
        return get_start_time(datarootdir, filename)+datetime.timedelta(hours=0.83)
    elif datarootdir.find('05kmCLayer') >= 0:               # Caliop
        return get_start_time(datarootdir, filename)+datetime.timedelta(hours=0.83)
    elif datarootdir.find('05kmCProfile') >= 0:             # Caliop
        return get_start_time(datarootdir, filename)+datetime.timedelta(hours=0.83)
    elif datarootdir.find('40kmAProfile') >= 0:             # Caliop
        return get_start_time(datarootdir, filename)+datetime.timedelta(hours=0.83)
    elif datarootdir.find('VFM') >= 0:                      # Caliop
        return get_start_time(datarootdir, filename)+datetime.timedelta(hours=0.83)
    elif datarootdir.find('mls-temp') >= 0:
        return get_start_time(datarootdir, filename)+datetime.timedelta(days=1)
    elif datarootdir.find('mls-iwc') >= 0:
        return get_start_time(datarootdir, filename)+datetime.timedelta(days=1)
    elif datarootdir.find('mls-h2o') >= 0:
        return get_start_time(datarootdir, filename)+datetime.timedelta(days=1)
    elif datarootdir.find('mls-co') >= 0:
        return get_start_time(datarootdir, filename)+datetime.timedelta(days=1)
    elif datarootdir.find('mls-o3') >= 0:
        return get_start_time(datarootdir, filename)+datetime.timedelta(days=1)
    elif datarootdir.find('mls-hno3') >= 0:
        return get_start_time(datarootdir, filename)+datetime.timedelta(days=1)
    elif datarootdir.find('MYD04_L2') >= 0:
        return get_start_time(datarootdir, filename)+datetime.timedelta(minutes=5)
    elif datarootdir.find('MYD06_L2_5KM') >= 0:
        return get_start_time(datarootdir, filename)+datetime.timedelta(minutes=5)
    #elif datarootdir.find('MYD06_L2_1KM') >= 0:
    elif datarootdir.find('modis-cloud-1km') >= 0:
        return get_start_time(datarootdir, filename)+datetime.timedelta(minutes=5)
    elif datarootdir.find('idaily-surface') >= 0:
        return get_start_time(datarootdir, filename)+datetime.timedelta(days=1)
    elif datarootdir.find('idaily-plevels') >= 0:
        return get_start_time(datarootdir, filename)+datetime.timedelta(days=1)
    elif datarootdir.find('yotc-oaml-1.5deg') >= 0:
        return get_start_time(datarootdir, filename)+datetime.timedelta(days=1)
    elif datarootdir.find('yotc-oapl-1.5deg') >= 0:
        return get_start_time(datarootdir, filename)+datetime.timedelta(days=1)
    elif datarootdir.find('yotc-aos-1.5deg') >= 0:
        return get_start_time(datarootdir, filename)+datetime.timedelta(days=1)
    elif datarootdir.find('yotc-oaml-0.25deg') >= 0:
        return get_start_time(datarootdir, filename)+datetime.timedelta(days=1)
    elif datarootdir.find('yotc-oapl-0.25deg') >= 0:
        return get_start_time(datarootdir, filename)+datetime.timedelta(days=1)
    elif datarootdir.find('yotc-aos-0.25deg') >= 0:
        return get_start_time(datarootdir, filename)+datetime.timedelta(days=1)
    elif datarootdir.find('era_interim_analysis_surface') >= 0:
        return get_start_time(datarootdir, filename)
    elif datarootdir.find('era_interim_analysis_level') >= 0:
        return get_start_time(datarootdir, filename)
    else:
	return None
# end of get_end_time()


def degree_to_radian(degree):
    return degree*N.pi/180.0


def get_Cartesian_distance(lat1, lon1, lat2, lon2):

    # convert from degree to radian
    lat1r = degree_to_radian(lat1)
    lon1r = degree_to_radian(lon1)
    lat2r = degree_to_radian(lat2)
    lon2r = degree_to_radian(lon2)

    half_pi = N.pi/2.0

    x1 = R * N.sin(half_pi-lat1r) * N.cos(lon1r)
    y1 = R * N.sin(half_pi-lat1r) * N.sin(lon1r)
    z1 = R * N.cos(half_pi-lat1r)

    x2 = R * N.sin(half_pi-lat2r) * N.cos(lon2r)
    y2 = R * N.sin(half_pi-lat2r) * N.sin(lon2r)
    z2 = R * N.cos(half_pi-lat2r)

    return N.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2) + (z1-z2)*(z1-z2))

# from http://www.movable-type.co.uk/scripts/latlong.html
def get_Haversine_distance(lat1, lon1, lat2, lon2):
    # mean radius of Earth in km
    R = 6371

    dLat = degree_to_radian(lat2-lat1)
    dLon = degree_to_radian(lon2-lon1)
    a = N.sin(dLat/2)*N.sin(dLat/2) + N.cos(degree_to_radian(lat1))*N.cos(degree_to_radian(lat2))*N.sin(dLon/2)*N.sin(dLon/2)
    c = 2*N.arctan2(N.sqrt(a), N.sqrt(1-a))
    d = R * c

    return d

def get_Haversine_distance2(lat1, lon1, lat2, lon2):
    # mean radius of Earth in km
    R = 6371

    cd = get_Cartesian_distance(lat1, lon1, lat2, lon2)
    ang = 2*N.arcsin(0.5*cd/R)  # the angle spanning the two points
    d = ang*R

    return d

def get_file_name_from_full_name(full_name):
    return os.path.basename(full_name)

# linear interpolation between two points
def linear_interpolation(x0, y0, x1, y1, x):
    return (y0 + (x-x0)*(y1-y0)/(x1-x0))


# find out what data set it is
# obsolete, new data set front ends will create a dataset container and make entry in get_dataset_container
def parse_data_type(datarootdir):
    print 'datarootdir: ', datarootdir
    if datarootdir.find('airs') >= 0:
        src_data = 'airs'
    elif datarootdir.find('amsr') >= 0:
        src_data = 'amsr'
    elif datarootdir.find('ceres') >= 0:
        src_data = 'ceres'
    elif datarootdir.find('05kmALayer') >= 0:
        src_data = 'caliop05kmALayer'
    elif datarootdir.find('05kmCLayer') >= 0:
        src_data = 'caliop05kmCLayer'
    elif datarootdir.find('05kmCProfile') >= 0:
        src_data = 'caliop05kmCProfile'
    elif datarootdir.find('40kmAProfile') >= 0:
        src_data = 'caliop40kmAProfile'
    elif datarootdir.find('VFM') >= 0:
        src_data = 'caliopVFM'
    elif datarootdir.find('mls-temp') >= 0:
        src_data = 'mls-temp'
    elif datarootdir.find('mls-iwc') >= 0:
        src_data = 'mls-iwc'
    elif datarootdir.find('mls-h2o') >= 0:
        src_data = 'mls-h2o'
    elif datarootdir.find('mls-co') >= 0:
        src_data = 'mls-co'
    elif datarootdir.find('mls-o3') >= 0:
        src_data = 'mls-o3'
    elif datarootdir.find('mls-hno3') >= 0:
        src_data = 'mls-hno3'
    elif datarootdir.find('MYD04_L2') >= 0:
        src_data = 'modis-aerosol'
    elif datarootdir.find('MYD06_L2_5KM') >= 0:
        src_data = 'modis-cloud-5km'
    elif datarootdir.find('MYD06_L2_1KM') >= 0:
        src_data = 'modis-cloud-1km'
    elif datarootdir.find('idaily-surface') >= 0:
	   src_data = 'ecmwf-idaily-surface'
    elif datarootdir.find('idaily-plevels') >= 0:
       src_data = 'ecmwf-idaily-plevels'
    elif datarootdir.find('yotc-aos-1.5deg') >= 0:
	   src_data = 'ecmwf-yotc-aos-1.5deg'
    elif datarootdir.find('yotc-oaml-1.5deg') >= 0:
	   src_data = 'ecmwf-yotc-oaml-1.5deg'
    elif datarootdir.find('yotc-oapl-1.5deg') >= 0:
	   src_data = 'ecmwf-yotc-oapl-1.5deg'
    elif datarootdir.find('yotc-aos-0.25deg') >= 0:
       src_data = 'ecmwf-yotc-aos-0.25deg'
    elif datarootdir.find('yotc-oaml-0.25deg') >= 0:
       src_data = 'ecmwf-yotc-oaml-0.25deg'
    elif datarootdir.find('yotc-oapl-0.25deg') >= 0:
        src_data = 'ecmwf-yotc-oapl-0.25deg'
    elif datarootdir.find('cloudsat') >= 0:
        src_data = 'cloudsat'
    elif datarootdir.find('era_interim_analysis_surface') >= 0:
        src_data = 'ecmwf_era_interim_analysis_surface'
    elif datarootdir.find('era_interim_analysis_level') >= 0:
        src_data = 'ecmwf_era_interim_analysis_level'
    else:
	print '****** Error in parse_data_type: source data set not supported yet !'
	sys.exit(1)

    return src_data
# end of parse_data_type()


# initialize a front end
# obsolete, new data set front ends will create a dataset container and make entry in get_dataset_container
def get_front_end(src_data, src_file):
	print '****** src_data: ', src_data
	print '****** src_file: ', src_file
        if src_data == 'airs':
            src_front_end = FEAIRS.front_end_airs(src_file)
        elif src_data == 'amsr':
            src_front_end = FEA.front_end_amsr(src_file)
        elif src_data == 'caliop05kmALayer':      # Caliop
            src_front_end = FE_CALIOP_05KMALAY.front_end_caliop_05km_alay(src_file)
        elif src_data == 'caliop05kmCLayer':      # Caliop
            src_front_end = FE_CALIOP_05KMCLAY.front_end_caliop_05km_clay(src_file)
        elif src_data == 'caliop05kmCProfile':    # Caliop
            src_front_end = FE_CALIOP_05KMCPRO.front_end_caliop_05km_cpro(src_file)
        elif src_data == 'caliop40kmAProfile':    # Caliop
            src_front_end = FE_CALIOP_40KMAPRO.front_end_caliop_40km_apro(src_file)
        elif src_data == 'caliopVFM':             # Caliop
            src_front_end = FE_CALIOP_VFM.front_end_caliop_vfm(src_file)
        elif src_data == 'ceres':
            src_front_end = FECERES.front_end_ceres(src_file)
        elif src_data == 'mls-temp':
            src_front_end = FEMLS_TEMP.front_end_mls_temp(src_file)
        elif src_data == 'mls-iwc':
            src_front_end = FEMLS_IWC.front_end_mls_iwc(src_file)
        elif src_data == 'mls-h2o':
            src_front_end = FEMLS_H2O.front_end_mls_h2o(src_file)
        elif src_data == 'mls-co':
            src_front_end = FEMLS_CO.front_end_mls_co(src_file)
        elif src_data == 'mls-o3':
            src_front_end = FEMLS_O3.front_end_mls_o3(src_file)
        elif src_data == 'mls-hno3':
            src_front_end = FEMLS_HNO3.front_end_mls_hno3(src_file)
        elif src_data == 'modis-aerosol':
            src_front_end = FEMODIS_AEROSOL.front_end_modis_aerosol(src_file)
        elif src_data == 'modis-cloud-5km':
            src_front_end = FEMODIS_CLOUD_5KM.front_end_modis_cloud_5km(src_file)
        elif src_data == 'modis-cloud-1km':
            src_front_end = FEMODIS_CLOUD_1KM.front_end_modis_cloud_1km(src_file)
        elif src_data == 'ecmwf-idaily-surface':
            src_front_end = FEECMWF_IDAILY_SURFACE.front_end_ecmwf_idaily_surface(src_file)
        elif src_data == 'ecmwf-idaily-plevels':
            src_front_end = FEECMWF_IDAILY_PLEVELS.front_end_ecmwf_idaily_plevels(src_file)
        elif src_data == 'ecmwf-yotc-aos-1.5deg':
            src_front_end = FEECMWF_YOTC_AOS_1P5DEG.front_end_ecmwf_yotc_aos_1p5deg(src_file)
        ### elif src_data == 'ecmwf-yotc-oaml-1.5deg':
            ### src_front_end = FEECMWF_YOTC_OAML_1P5DEG.front_end_ecmwf_yotc_oaml_1p5deg(src_file)
        ### elif src_data == 'ecmwf-yotc-oapl-1.5deg':
            ### src_front_end = FEECMWF_YOTC_OAPL_1P5DEG.front_end_ecmwf_yotc_oapl_1p5deg(src_file)
        elif src_data == 'ecmwf-yotc-aos-0.25deg':
            src_front_end = FEECMWF_YOTC_AOS_0P25DEG.front_end_ecmwf_yotc_aos_0p25deg(src_file)
        elif src_data == 'ecmwf-yotc-oaml-0.25deg':
            src_front_end = FEECMWF_YOTC_OAML_0P25DEG.front_end_ecmwf_yotc_oaml_0p25deg(src_file)
        elif src_data == 'ecmwf-yotc-oapl-0.25deg':
            src_front_end = FEECMWF_YOTC_OAPL_0P25DEG.front_end_ecmwf_yotc_oapl_0p25deg(src_file)
	elif src_data.find('cloudsat') >= 0:
            src_front_end = FEC.front_end_cloudsat(src_file)
        else:
            print '****** Error in get_front_end: source data set not supported yet !'
            sys.exit(1)

	return src_front_end
# end of get_front_end()


# calculate index range for each process
def index_distribution(index1, index2, num_proc):
    ### print 'index1,: ', index1, ', index2: ', index2, ', num_proc', num_proc
    tot = index2 - index1 + 1
    if tot <= 0 or num_proc < 1 or tot < num_proc:
	return -1

    ran = N.array([-1]*num_proc*2)
    ran = ran.reshape(num_proc, 2)
    ### print ran

    # each proc will be assigned cnt indices
    # some will get a residual
    cnt = int(tot/num_proc)
    residual = tot - cnt*num_proc
    ### print 'cnt: ', cnt, ', residual: ', residual

    # start and ending index numbers of each proc
    # init value
    for i in range(num_proc):
        ran[i][0] = cnt
        ran[i][1] = 0

    # keeps num indices each proc will be assigned
    for i in range(residual):
        ran[i][0] += 1
        ### print 'cont for ', i, ': ', ran[i][0]

    """
    for i in range(residual, num_proc):
        print 'cont for ', i, ': ', ran[i][0]
    """

    # end number of each proc
    ran[0][1] = ran[0][0] - 1 + index1
    for i in range (1, num_proc):
        ran[i][1] = ran[i-1][1] + ran[i][0]

    # start number of each proc
    for i in range(num_proc):
        ran[i][0] = ran[i][1] - ran[i][0] + 1

    # debug print
    ### for i in range(num_proc):
        ### print 'proc id: ', i, ', start: ', ran[i][0], ', end: ', ran[i][1]

    return ran
# end of index_distribution()

