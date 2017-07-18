# def_calcTimeBounds(fn):
# def_getTimeBounds(serviceType, dataSource, varName):
# def_correctTimeBounds1
# def_correctTimeBounds2
# if___name__ == '__main__':

import sys
import os
import glob
import re
sys.path.append('./svc/src/py')
### sys.path.append('/home/svc/new_github/JPL-WebService/JPL_CMDA/services/svc/svc/src/py')
print 'in getTimeBounds'
print sys.path
import cmac
p1 = re.compile( r'_(\d*)-(\d*).nc')

dir00 = cmac.getRootDir()[0]
print 'dir00: ', dir00

# calc time bounds from filename
# def_calcTimeBounds(fn):
def calcTimeBounds(fn):
  # find the start of the time bounds
  m1 = p1.search(fn)
  g1 =  m1.groups()
  if len(g1)!=2:
    return [0, 0]

  #print fn, g1
  year1 = int(g1[0])
  year2 = int(g1[1])

  return [year1, year2]

# def_getTimeBounds(serviceType, dataSource, varName):
def getTimeBounds(serviceType, dataSource, varName):
  # serviceType = '1': Chengxing Zhai's services
  # serviceType = '2': Benyang Tang's services

  subdirs1 = ['regridded', 'break', '.']
  #subdirs2 = ['regridded', 'original', '.']
  #subdirs2 = ['regridded',  '.']
  subdirs2 = ['regridded', 'break', '.']

  if serviceType=='1':
    subdirs = subdirs1
  else:
    subdirs = subdirs2

  year1b = 0
  year2b = 0

  # loop over subdirs
  for subdir in subdirs:

    # list of files
    temp1 =  dir00 + '/' + dataSource.lower() + '/' + subdir + '/' + varName + '_*.nc'
    #print temp1
    files = glob.glob( temp1 )

    # if no files in that subdir
    if len(files)==0:
      continue

    files1 = [os.path.split(file1)[1] for file1 in files]

    year1a = []
    year2a = []
    # loop over files
    for file1 in files1:

      # determine time bounds
      bounds = calcTimeBounds(file1)
      year1a.append(bounds[0]) 
      year2a.append(bounds[1]) 

    year1b = min(year1a) 
    year2b = max(year2a)

    if year1b>0:
      print temp1
      return [year1b, year2b]

  return [0,0]

# def_correctTimeBounds1(serviceType, dataSource, varName, timeS, timeE):
def correctTimeBounds1(serviceType, dataSource, varName, timeS, timeE):
  # getTimeBounds(serviceType, dataSource, varName):
  timeS1 = int(timeS)
  timeE1 = int(timeE)
  dataTimeBounds = getTimeBounds(serviceType, dataSource, varName)
  timeS2 = max(timeS1, dataTimeBounds[0]) 
  timeE2 = min(timeE1, dataTimeBounds[1]) 

  if timeE2<timeS2:
    return ['0', '0']
 
  return [str(timeS2), str(timeE2)]

# def_correctTimeBounds2
def correctTimeBounds2(serviceType, dataSource1, varName1, dataSource2, varName2, timeS, timeE):
  timeS1 = int(timeS)
  timeE1 = int(timeE)
  dataTimeBounds1 = getTimeBounds(serviceType, dataSource1, varName1)
  dataTimeBounds2 = getTimeBounds(serviceType, dataSource2, varName2)

  timeS2 = max(timeS1, dataTimeBounds1[0], dataTimeBounds2[0]) 
  timeE2 = min(timeE1, dataTimeBounds1[1], dataTimeBounds2[1]) 

  if timeE2<timeS2:
    return ['0', '0']
 
  return [str(timeS2), str(timeE2)]

# if___name__ == '__main__':
if __name__ == '__main__':
        if 1:
          sources = ["nasa/modis", ]
          vars = ['lai', ]

        if 0:
          sources = ["argo/argo", "cccma/canam4", "cccma/canesm2", "csiro/mk3.6", "gfdl/cm3", "gfdl/cm3_hist", "gfdl/esm2g",
                           "giss/e2-h", "giss/e2-r", "ipsl/cm5a-lr", "miroc/miroc5", "nasa/airs", "nasa/amsre", "nasa/aviso",
                           "nasa/ceres", "nasa/gpcp", "nasa/grace", "nasa/mls", "nasa/modis", "nasa/quikscat", "nasa/trmm",
                           "ncar/cam5", "ncar/cam5-1-fv2", "ncc/noresm", "noaa/nodc", "ukmo/hadgem2-a", "ukmo/hadgem2-es"]

          vars = ["pr", "cli", "clt", "lai", "rlds", "rldscs","rlus", "rlut", "rlutcs", "rsds", "rsdscs", "rsdt", "rsus", "rsuscs",
                        "rsut", "rsutcs", "sfcWind", "ts", "uas", "vas", "clw", "hus", "ta", "tos", "zos", "ohc700", "ohc2000", "zo", "zl", "os", "ot"] 

                        #["clivi", "clwvi", "z1", "z0", "cltStddev", "cltNobs", "sfcWindNobs", "sfcWindStderr", "uasNobs", "uasStderr", "vasNobs", "vasStderr",
                        #"prw"]
        print("start test")

        #serviceType = '1'
        serviceType = '2'

        for source in sources:
                for var in vars:
                        bounds = getTimeBounds(serviceType, source, var)
                        print '%20s  %10s:  %7d : %7d'%(source, var, bounds[0], bounds[1])
        print("end test")


