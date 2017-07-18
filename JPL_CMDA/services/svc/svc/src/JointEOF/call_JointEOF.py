# call_JointEOF.py
import string
import math
import subprocess
import os
import glob
from os.path import basename
from netCDF4 import Dataset
from netCDF4 import date2num
from netCDF4 import num2date
from datetime import date
from datetime import timedelta
import numpy as np
from netCDF4 import MFDataset
import matplotlib
matplotlib.use('Agg')
import matplotlib.pylab as plt
from mpl_toolkits.basemap import Basemap
plt.ioff()
import matplotlib.gridspec as gridspec

def ncdate2date(thisDate) :
  return date(thisDate.year, thisDate.month, thisDate.day)

def getDataRootDirectory() :
  f = open('../../../data.cfg', 'r')
  dir = f.readline()
  f.close()
  return dir[:-1] # remove the trailing newline

def parseDateInFileName(file):
  if file[-10] == '-' or '_' :
    return [ yyyymm2date(file[-9:-3]), yyyymm2date(file[-16:-10], True)]
  else:
    date1 = date(int(file[-11:-7]), int(file[-7:-5]), int(file[-5:-3]))
    date2 = date(int(file[-20:-16]), int(file[-16:-14]), int(file[-14:-12]))
    return [date1, date2]

def getTimeRange(file, useFileName=False):
  if useFileName :
    return parseDateInFileName(file)
  else:
    nc_file = Dataset(file, 'r')
    t = nc_file.variables['time']
    t_start = t[0]
    t_end = t[-1]
    if hasattr(t, 'calendar'):
      cal = t.calendar
    else:
      cal = 'standard'
    date1 = ncdate2date(num2date(t_start, t.units, cal))
    date2 = ncdate2date(num2date(t_end, t.units,cal))
    nc_file.close()
    return [date1, date2]

def yyyymm2date(s, lastDay=False):
  if lastDay:
    thisDate = date(int(s[0:4]), int(s[4:6]), 28)
    thisDate = thisDate + timedelta(4)
    return thisDate.replace(day=1) - timedelta(1)
  else:
    return date(int(s[0:4]), int(s[4:6]), 1)

def dataFileRelevant(file, timeRange) :
  fileTimeRange = getTimeRange(file)
  return not (timeRange[1] < fileTimeRange[0] or timeRange[0] > fileTimeRange[1])

def getDataFilePaths (source, var, timeRange) :
  source = source.split('_')
  dataDir = getDataRootDirectory() + '/cmip5/' + source[0] + '/' + source[1]
  fList = glob.glob(dataDir + '/regridded/' + var + '*.nc') 
  if len(fList) < 1 :
    fList = glob.glob(dataDir + '/' + var + '*.nc') 
  relevantFiles = []
  for file in fList:
    if dataFileRelevant(file, timeRange) :
      relevantFiles.append(file)
  return relevantFiles

def numberOfMonths(startDateStr, endDateStr) :
  return (int(endDateStr[0:4]) - int(startDateStr[0:4]))*12 + (int(endDateStr[4:6]) - int(startDateStr[4:6])) + 1

def durationInMonths(dateRange) :
  return (dateRange[1].year - dateRange[0].year)*12 + (dateRange[1].month - dateRange[0].month) + 1;

def calculateAnomaly(data, dim=0, idx = range(0,12)) :
  dataShape = data.shape
  newshape = (int(np.prod(dataShape[0:dim])), int(dataShape[dim]), int(np.prod(dataShape[(dim+1):(-1)])))
  data_reshaped = data.reshape(newshape)
  for ii in idx:
    thisIdx = range(ii,dataShape[dim], 12)
    data_clim = np.mean(data_reshaped[:, thisIdx,:], 1).reshape(newshape[0], 1, newshape[2])
    data_reshaped[:, thisIdx,:] = data_reshaped[:, thisIdx,:] - np.tile(data_clim, (1, len(thisIdx),1))
  data = data_reshaped.reshape(dataShape)

def readDataFromFileList(fileList, var, lonRange, latRange, timeRange, plev) :
  nMonths = durationInMonths(timeRange)
  for thisFile in fileList :
    print 'reading file ...', thisFile
    nc_file = Dataset(thisFile, 'r')
    if not ('data' in locals() ) :
      lat = nc_file.variables['lat'][:]
      lon = nc_file.variables['lon'][:]
      lon_mask = np.logical_and(lon >= lonRange[0], lon <= lonRange[1])
      lat_mask = np.logical_and(lat >= latRange[0], lat <= latRange[1])
      lon = lon[lon_mask]
      lat = lat[lat_mask]
      data = np.ndarray(shape=(nMonths, len(lat), len(lon)), dtype=float)
      longName = nc_file.variables[var].getncattr('long_name')
      units = nc_file.variables[var].getncattr('units')
    thisDateRange = getTimeRange(thisFile)
    nMonths_thisFile = durationInMonths(thisDateRange)
    monthIdx1 = durationInMonths([timeRange[0], thisDateRange[0]])-1
    monthIdx2 = durationInMonths([timeRange[0], thisDateRange[1]])
    idx2Data_start = 0;
    idx2Data_end = nMonths_thisFile;

    if monthIdx1 < 0:
      idx2Data_start = - monthIdx1;
      monthIdx1 = 0;

    if monthIdx2 >= nMonths:
      idx2Data_end = idx2Data_end - (monthIdx2 - nMonths);
      monthIdx2 = nMonths;

    if plev == -999999:
      data[monthIdx1:monthIdx2,:,:] = nc_file.variables[var][idx2Data_start:idx2Data_end,lat_mask, lon_mask]
    else:
      pIdx = np.argmin(abs(nc_file.variables['plev'][:] - plev))
      data[monthIdx1:monthIdx2,:,:] = nc_file.variables[var][idx2Data_start:idx2Data_end, pIdx, lat_mask, lon_mask].reshape(monthIdx2-monthIdx1, len(lat), len(lon))

  return [data, lon, lat, longName, units]

def dispMap(lon, lat, mapData, this_ax, title) :
  m = Basemap(lon[0], lat[0], lon[-1], lat[-1], resolution='c', suppress_ticks=False, ax=this_ax)
  im = m.pcolor(lon, lat, mapData, vmin=np.amin(mapData), vmax=np.amax(mapData), shading='flat')
  m.drawcoastlines(color=(.7,.7,.7))
  cbar = m.colorbar(im, location='bottom', pad = "10%")
  plt.title(title)
  return m

def getPlev(url, plevKey, var) :
  plev = int(url[plevKey])
  ### -999999 are special fill values
  if plev != -999999 :
    ### convert plev to from hPa to Pa
    plev = plev * 100 
    if var == 'ot' or var == 'os' :
      ### from dbar to hPa
      plev = plev * 100
  return plev

class call_JointEOF:

    name = 'JointEOF'

    # url_args here is a dictionary, converted from HPPT request arguements
    def __init__(self, url_args, output_dir = None):
        self.sourceName1 = url_args['sourceName1']
        self.var1 = url_args['var1']
        self.lonRange1 = [float(url_args['lon1S']), float(url_args['lon1E'])]
        self.latRange1 = [float(url_args['lat1S']), float(url_args['lat1E'])]
        self.plev1 = getPlev(url_args,'plev1', self.var1)
        self.anomaly1 = int(url_args['anomaly1'])
        
        self.sourceName2 = url_args['sourceName2']
        self.var2 = url_args['var2']
        self.lonRange2 = [float(url_args['lon2S']), float(url_args['lon2E'])]
        self.latRange2 = [float(url_args['lat2S']), float(url_args['lat2E'])]
        self.plev2 = getPlev(url_args,'plev2', self.var2)
        self.anomaly2 = int(url_args['anomaly2'])

        self.output_dir = output_dir
        self.timeRange = [yyyymm2date(url_args['timeS']), yyyymm2date(url_args['timeE'], True)]

    def setOutputDir(self, output_dir):
        self.output_dir = output_dir

    def display(self):

        fileList1 = getDataFilePaths (self.sourceName1, self.var1, self.timeRange)
        data1, lon1, lat1, longName1, units1 = readDataFromFileList(fileList1, self.var1, self.lonRange1, self.latRange1, self.timeRange, self.plev1)

        if self.anomaly1:
          calculateAnomaly(data1, 2)

        fileList2 = getDataFilePaths (self.sourceName2, self.var2, self.timeRange)
        print ' file list 2 = ...' , fileList2
        data2, lon2, lat2, longName2, units2 = readDataFromFileList(fileList2, self.var2, self.lonRange2, self.latRange2, self.timeRange, self.plev2)

        if self.anomaly2:
          calculateAnomaly(data2, 2)
        
        nT = durationInMonths(self.timeRange)
        nLon1 = len(lon1)
        nLat1 = len(lat1)
        nLon2 = len(lon2)
        nLat2 = len(lat2)
        Q1, R1 = np.linalg.qr(data1.reshape([nT, nLon1*nLat1]).T)
        Q2, R2 = np.linalg.qr(data2.reshape([nT, nLon2*nLat2]).T)

        U,S,V = np.linalg.svd(np.dot(R1,R2.T))

        nModes = min([nT, nLon1*nLat1, nLon2*nLat2, 3])

        Amp1 = R1.T.dot(U[:,0:nModes])
        Amp2 = R2.T.dot(V[:,0:nModes])

        Pattern1 = Q1.dot(U[:,0:nModes]).reshape(nLat1, nLon1, nModes)
        Pattern2 = Q2.dot(V[:,0:nModes]).reshape(nLat2, nLon2, nModes)

        fig = plt.figure(figsize=(40,25))
        gs = gridspec.GridSpec(nModes+1,4);
        nModeDisp = min([10, nT, nLat1*nLon1, nLat2*nLon2])
        coVarExplained = np.power(S, 2)
        coVarExplained = coVarExplained / sum(coVarExplained)
        ax = plt.subplot(gs[0,1:2])
        ax.bar(range(1,nModeDisp+1), coVarExplained[0:nModeDisp]*100, align='center', alpha=0.5 )
        plt.xlabel('Mode index')
        plt.ylabel('Explained Percentage (%)')
        plt.title('Explained Covariance')
        for rI in range(0, nModes):
          thisTitle = 'Joint EOF mode' + str(rI+1) + ',' + longName1
          ax = plt.subplot(gs[rI+1,0])
          m = dispMap(lon1, lat1, Pattern1[:,:,rI], ax, thisTitle)
          thisTitle = 'Joint EOF mode' + str(rI+1) + ',' + longName2
          ax = plt.subplot(gs[rI+1,2])
          m = dispMap(lon2, lat2, Pattern2[:,:,rI], ax, thisTitle)
          ax = plt.subplot(gs[rI+1,1])
          ax.plot(range(0,nT), Amp1[:,rI])
          plt.ylabel(self.var1 + '(' + units1 + ')') 
          if nT >= 24 :
            plt.xticks(np.arange((13 - self.timeRange[0].month) % 12, self.timeRange[0].month+nT, 12), [str(int(x+self.timeRange[0].year + 1 -  math.trunc((13 - self.timeRange[0].month)/12))) for x in np.arange(0, nT/12)])
            plt.xlabel('Time (year)')
          else :
            plt.xlabel('Time (months since ' + self.timeRange[0].strftime('%Y-%m') + ')')
          plt.title('Temporal amplitude, mode ' + str(rI))
          ax = plt.subplot(gs[rI+1,3])
          ax.plot(range(1,nT+1), Amp2[:,rI])
          plt.ylabel(self.var2 + '(' + units2 + ')') 
          if nT >= 24 :
            plt.xticks(np.arange((13 - self.timeRange[0].month) % 12, self.timeRange[0].month+nT, 12), [str(int(x+self.timeRange[0].year + 1 -  math.trunc((13 - self.timeRange[0].month)/12))) for x in np.arange(0, nT/12)])
            plt.xlabel('Time (year)')
          else :
            plt.xlabel('Time (months since ' + self.timeRange[0].strftime('%Y-%m') + ')')
          plt.title('Temporal amplitude, mode ' + str(rI))
          
        productFileNameBase = 'jointEOF_' + self.sourceName1 + '_' + self.var1 + '_and_' + self.sourceName2 + '_' + self.var2
        figFile = productFileNameBase + '.jpeg' 
        dataFile = productFileNameBase + '.nc'
        fig.savefig(self.output_dir + '/' + figFile, dpi=100)

        ds = Dataset(self.output_dir + '/' + dataFile, 'w', format='NETCDF3_CLASSIC')
        ds.createDimension('lat1', nLat1)
        ds.createDimension('lon1', nLon1)
        ds.createDimension('lat2', nLat2)
        ds.createDimension('lon2', nLon2)
        ds.createDimension('mode', nModes)
        ds.createDimension('time', nT)
        thisT = ds.createVariable('time', np.float32, ('time'))
        thisLon1 = ds.createVariable('lon1', np.float32, ('lon1'))
        thisLat1 = ds.createVariable('lat1', np.float32, ('lat1'))
        thisLon2 = ds.createVariable('lon2', np.float32, ('lon2'))
        thisLat2 = ds.createVariable('lat2', np.float32, ('lat2'))
        thisMode = ds.createVariable('mode', np.float32, ('mode'))
        thisPattern1 = ds.createVariable('pattern1', np.float32, ('mode', 'lat1', 'lon1'))
        thisPattern2 = ds.createVariable('pattern2', np.float32, ('mode', 'lat2', 'lon2'))
        thisAmp1 = ds.createVariable('amp1', np.float32, ('time', 'mode'))
        thisAmp2 = ds.createVariable('amp2', np.float32, ('time', 'mode'))
        thisCovEx = ds.createVariable('covExplained', np.float32, ('mode'))
        ds.source = 'Produced by CMDA analysis tools: JointEOF'
        thisLon1.units = 'degrees_north'
        thisLon2.units = 'degrees_north'
        thisLat1.units = 'degrees_east'
        thisLat2.units = 'degrees_east'
        thisAmp1.units = units1
        thisAmp2.units = units2
        thisAmp1.long_name = longName1 + '_amplitude'
        thisAmp2.long_name = longName2 + '_amplitude'
        thisPattern1.units = '1'
        thisPattern2.units = '1'
        thisPattern1.long_name = longName1 + '_pattern'
        thisPattern2.long_name = longName2 + '_pattern'
        thisT.units = 'months since ' + self.timeRange[0].strftime('%Y-%m-%d %H:%M:%S')
        thisT.calendar = 'gregorian'
        print '.... saving data '
        thisLon1[:] = lon1;
        thisLon2[:] = lon2;
        thisLat1[:] = lat1;
        thisLat2[:] = lat2;
        thisT[:] = np.arange(0, nT);
        thisMode[:] = np.arange(0, nModes);
        thisAmp1[:] = Amp1;
        thisAmp2[:] = Amp2;
        thisPattern1[:] = Pattern1;
        thisPattern2[:] = Pattern2;
        thisCovEx[:] = coVarExplained[0:nModes];
        ds.close()
        ## save nc data
        err_mesg = 'Call returned successfully'
        return (err_mesg, figFile, dataFile)

if __name__ == '__main__':

    c1 = call_JointEOF({'sourceName1': 'gfdl_cm3', 'var1': 'pr', 'plev1' : -999999, 'lon1S' : 0, 'lon1E': 360, 'lat1S' : -90, 'lat1E': 90, 'sourceName2': 'gfdl_cm3', 'var2': 'hus', 'plev2' : 200, 'lon2S' : 0, 'lon2E': 360, 'lat2S' : -60, 'lat2E' : 60, 'timeS' : '200001', 'timeE' : '200412', 'anomaly1' : 0, 'anomaly2' : 0}, '.')

    mesg = c1.display()
    print 'mesg: ', mesg
