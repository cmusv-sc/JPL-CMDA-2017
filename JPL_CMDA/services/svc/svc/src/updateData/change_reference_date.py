import os
from netCDF4 import Dataset

def change_ref_days(nc_file):
  src_days = 'days since 0000-01-01 00:00:00'
  tgt_days = 'days since 1850-01-01 00:00:00'

  rootgrp = Dataset(nc_file, 'r+', format='NETCDF4')
  """
  print 'variables.items: '
  print rootgrp.variables.items()
  print '============================'
  print ''
  """
  # gives you 'units' attribute
  print 'variables["time"].units: '
  print rootgrp.variables['time'].units
  print '============================'
  print ''
  # gives you 'calendar' attribute
  print 'variables["time"].calendar: '
  print rootgrp.variables['time'].calendar
  print '============================'
  print ''
  ### print rootgrp.dimensions.items()
  ### print rootgrp.variables.OrderedDict()

  print 'variables["time"].[...]: '
  print rootgrp.variables['time'][:]
  print '============================'
  print ''


  if rootgrp.variables['time'].units == src_days:
    rootgrp.variables['time'].units = tgt_days
    # descrease every value by 365*1850
    rootgrp.variables['time'][:] = rootgrp.variables['time'][:] - 365 * 1850

    print '****** time units changed ****** '
    print ''
    print 'variables["time"].units: '
    print rootgrp.variables['time'].units
    print '============================'
    print ''
    print 'updated variables["time"].[...]: '
    print rootgrp.variables['time'][:]
    print '============================'
    print ''

  # close file
  rootgrp.close()


def main():
  ### nc_file = '/home/svc/tos_Omon_CESM1-CAM5_historical_r1i1p1_199501-200512.nc'
  ### nc_file = 'zos_Omon_CESM1-CAM5_historical_r1i1p1_199501-200512.nc'
  
  rootDir = '.'
  for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):
    print('Found directory: %s' % dirName)
    for fname in fileList:
      ### print('\t%s' % fname)

      if '.nc' in fname:
        nc_file = fname
        print('-----------------------------\n%s' % nc_file)
        change_ref_days(nc_file)


if __name__ == '__main__':
  main()


