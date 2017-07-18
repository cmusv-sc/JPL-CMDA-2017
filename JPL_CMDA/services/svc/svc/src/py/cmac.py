#== def_find_bound(x):
#== def_getRootDir():
#== class_MAPPLOT():
  #== def_plot(self):

import os
import numpy as np
import matplotlib 
matplotlib.use('Agg')  
import matplotlib.pylab as Mat
Mat.ioff()
from mpl_toolkits.basemap import Basemap

#== def_getRootDir():
def getRootDir():
  # use data.cfg to set the data root dir.

  # assuming the cwd is where this code file is
  configFile = '../../../data.cfg'
  cwd = os.getcwd()
  cmacDir = os.path.abspath(os.path.join(cwd, '../../../..'))
  configFile = os.path.abspath(os.path.join(cwd, configFile))
  print 'cmacDir: ', cmacDir
  print 'configFile: ', configFile

  # if not, use 'services' to figure it out  
  if not os.path.isfile(configFile):
    print 'use JPL-WebService to figure out'
    cwd = os.getcwd()
    print 'in getRootDir, cwd: ', cwd
    #ind1 = cwd.find('services')
    ind1 = cwd.find('JPL_CMDA')
    if ind1>-1:
      cmacDir = cwd[:ind1]
      print 'cmacDir: ', cmacDir
      #configFile = os.path.join(cmacDir, 'services/svc/data.cfg')
      configFile = os.path.join(cmacDir, 'JPL_CMDA/services/svc/data.cfg')
      print 'configFile: ', configFile

    if not os.path.isfile(configFile):
      print 'failed to find data.cfg: %s'%(configFile)
      return None 
    
  if not os.path.isfile(configFile):
    print 'Check again. failed to find data.cfg: %s'%(configFile)
    return None 
    
  try:
    temp1 = open(configFile).read() 
    print 'temp1: ', temp1
    if temp1[-1]=='\n':
      temp1 = temp1[:-1]
    if temp1[-1]=='/':
      temp1 = temp1[:-1]
    # zzzz
    #if os.path.isdir(temp1):
    if 1:
      dataDir = temp1 + '/cmip5' 
      #a.dataDir = temp1  # should change to this when data.cfg is without 'cmip5'
      return dataDir, cmacDir
        
  except:
    print 'failed to read data.cfg.'
    return None

  print 'failed to get data.cfg.'
  return None

#== def_find_bound(x):
# for used in matplotlib as axis variable
def find_bound(x, min1=None, max1=None):
  '''
Modify x so it becomes the end points.
'''
  temp1 = np.zeros((len(x)+1,), dtype=x.dtype)
  temp1[1:-1] = (x[1:,]+x[:-1])/2.
  temp1[0] = x[0] - (temp1[1]-x[0])
  temp1[-1] = x[-1] + (x[-1] - temp1[-2])

  if min1:
    temp1[0] = max(temp1[0], min1)
  if max1:
    temp1[-1] = min(temp1[-1], max1)

  return temp1


#== class_MAPPLOT():
class MAPPLOT():
  def __init__(self):

    self.data1 = None

    self.lon1 = None
    self.lat1 = None

    self.vmin1 = None
    self.vmax1 = None

    self.xLable = None
    self.yLable = None
    self.title = None

    self.plotH = None

    self.outFile = None

  #== def_plot(self):
  def plot(self):
    # convert lon/lat for calling pcolor()
    lon2 = find_bound(self.lon1)
    lat2 = find_bound(self.lat1)

    lat2[0] = max(-90, lat2[0])
    lat2[-1] = min(90, lat2[-1])

    # aspect ratio
    lat12 = (self.lat1[0] + self.lat1[-1])/2.0
    aspect1 = (self.lat1[-1]-self.lat1[0]) / (self.lon1[-1]-self.lon1[0])*np.cos(np.pi*lat12/180.0)
    aspect2 = np.cos(np.pi*lat12/180.0)
    self.plotW = min( self.plotH/aspect1, 12)

    print self.lat1[-1]
    print self.lat1[0]
    print aspect1
    print 'plotW, plotH: ',
    print self.plotW, self.plotH

    # calc data range
    print 'self.vmin1, vmax1: ',
    print self.vmin1
    print self.vmax1
    if self.vmin1 is None:
      self.vmin1 = self.data1.min()
      self.vmax1 = self.data1.max()
    print 'self.vmin1, vmax1: ',
    print self.vmin1
    print self.vmax1

    # start plotting
    #f1 =Mat.figure(figsize=(self.plotW, self.plotH))
    f1 =Mat.figure(figsize=(14, 10))

    m = Basemap(lon2[0], lat2[0], lon2[-1], lat2[-1], 
         resolution='c', suppress_ticks=False)
    im = m.pcolor(lon2, lat2, self.data1, vmin=self.vmin1, vmax=self.vmax1, shading='flat')
    ax1 = Mat.gca()
    Mat.setp(ax1, aspect=1./aspect2)
    m.drawcoastlines(color=(.7,.7,.7))

    # title, labels
    Mat.title(self.title)
    Mat.xlabel(self.yLabel)
    Mat.ylabel(self.xLabel)
    labels = ax1.get_xticklabels()
    Mat.setp(labels, rotation=45, fontsize=10)

    # colorbar
    hc = Mat.colorbar()

    # save to file
    Mat.savefig(self.outFile, dpi=100)
    
#== class_ANOMALY():
class ANOMALY():
  def __init__(self):
    self.data1 = None
    self.data2 = None

    self.time1 = None
    self.time2 = None

