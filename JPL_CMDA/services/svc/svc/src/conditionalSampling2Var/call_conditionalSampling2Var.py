# call_conditionalSampling2Var.py
import string
import subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import scipy.ndimage
import os
from fillNaN import replace_nans
from netCDF4 import Dataset
from scipy.ndimage.filters import gaussian_filter
from os.path import basename

if __name__ == '__main__':
  import sys
  sys.path.append('../time_bounds')
  sys.path.append('/home/zhai/work/JPL-WebService/JPL_CMDA/services/svc/svc/src/py')
  sys.path.append('/home/zhai/work/JPL-WebService/JPL_CMDA/services/svc/svc/src/time_bounds')
  from getTimeBounds import correctTimeBounds2
else:
  from svc.src.time_bounds.getTimeBounds import correctTimeBounds2

class call_conditionalSampling2Var:
    def __init__(self, data_source, var, start_time, end_time, lon1, lon2, lat1, lat2, pres1, pres2, months,
                 env_var_source1, env_var1, bin_min1, bin_max1, bin_n1, env_var_plev1,
                 env_var_source2, env_var2, bin_min2, bin_max2, bin_n2, env_var_plev2, output_dir, displayOpt):
        self.data_source = data_source		# for e.g. "NCAR_cam5" or "nasa_airs", etc
        self.var = var				# CMIP5 variable names, e.g. 'ta', 'hus', 'clt'
        self.lon1 = lon1			# longitude range, min, units = deg
        self.lon2 = lon2			# longitude range, max, units = deg
        self.lat1 = lat1			# latitude range, min, units = deg
        self.lat2 = lat2			# latitude range, max, units = deg
        self.pres1 = pres1			# pressure level 1 for pressure range 
        self.pres2 = pres2			# pressure level 2 for pressure range 
        self.months = months			# month index to specify season, e.g. 6,7,8 for boreal summer
        self.env_var_source1 = env_var_source1	# first large scale environmental variable data source, e.g. "NCAR_cam5"
        self.env_var1 = env_var1		# first large scale environmental variable CMIP5 name, e.g. 'ts', 'tos'
        self.bin_min1 = bin_min1		# min value of bin boundary for sorting first large scale env var
        self.bin_max1 = bin_max1		# max value of bin boundary for sorting first large scale env var
        self.bin_n1 = bin_n1			# number of bins to be used for the first large scale variable
        self.env_var_plev1 = env_var_plev1	# pressure level for env var if it is 3-d
        self.env_var_source2 = env_var_source2	# first large scale environmental variable data source, e.g. "NCAR_cam5"
        self.env_var2 = env_var2		# first large scale environmental variable CMIP5 name, e.g. 'ts', 'tos'
        self.bin_min2 = bin_min2		# min value of bin boundary for sorting first large scale env var
        self.bin_max2 = bin_max2		# max value of bin boundary for sorting first large scale env var
        self.bin_n2 = bin_n2			# number of bins to be used for the first large scale variable
        self.env_var_plev2 = env_var_plev2	# pressure level for env var if it is 3-d
        self.output_dir = output_dir		# output directory for figure and data file
        self.displayOpt = displayOpt		# display option, if in binary, the last 3 bits = [z y x]
        availableTimeBnds1 = correctTimeBounds2('2', data_source.replace("_", "/"), var, env_var_source1.replace("_", "/"), env_var1, start_time, end_time)
        availableTimeBnds2 = correctTimeBounds2('2', data_source.replace("_", "/"), var, env_var_source2.replace("_", "/"), env_var2, start_time, end_time)
        self.start_time = str(max(int(availableTimeBnds1[0]), int(availableTimeBnds2[0])));
        self.end_time = str(min(int(availableTimeBnds1[1]), int(availableTimeBnds2[1])));
						# z = map scale, y = vertical axis, x = horizontal axis
						# 1 = log, 0 = lin

    def displayConditionalSampling2Var(self):

        inputs = self.data_source + ' ' + self.var + ' ' + self.start_time + ' ' + self.end_time + ' ' + \
                 self.lon1 + ',' + self.lon2 + ' ' + self.lat1 + ',' + self.lat2 + ' ' + \
                 self.pres1 + ',' + self.pres2 + ' ' + self.months + ' ' + \
                 self.env_var_source1 + ' ' + self.env_var1 + ' ' + \
                 self.bin_min1 + ',' + self.bin_max1 + ',' + self.bin_n1 + ' ' +  self.env_var_plev1 + ' ' + \
                 self.env_var_source2 + ' ' + self.env_var2 + ' ' + \
                 self.bin_min2 + ',' + self.bin_max2 + ',' + self.bin_n2 + ' ' +  self.env_var_plev2 + ' ' + self.output_dir + ' ' + self.displayOpt
        print 'inputs: ', inputs
        command = './octaveWrapper ' +  inputs
        cmd = command.split(' ')
        cmdstring = string.join(cmd, ' ')
        print 'cmdstring: ', cmdstring

        if self.start_time == '0' or self.end_time == '0':
          return ('No Data', '', '')

        try:
          proc=subprocess.Popen(cmd, cwd='.', stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
          # wait for the process to finish
          stdout_value, stderr_value = proc.communicate()
          print 'stdout_value: ', stdout_value
          print 'stderr_value: ', stderr_value

          if stderr_value.find('error:') >= 0:
             return (stderr_value, '', '')

          fst = 'figFile: '
          l1 = len(fst)
          ### print 'l1: ', l1
          image_filename = ''

          fst2 = 'dataFile: '
          l2 = len(fst2)
          ### print 'l2: ', l2
          data_filename = ''

          lines = stdout_value.split('\n')
          for line in lines:
            ### print '*****: ', line
            if line.find('figFile: ') >= 0:
              print '***** line: ', line
              image_filename = line[l1:]

            if line.find('dataFile: ') >= 0:
              print '***** line: ', line
              data_filename = line[l2:]

          print 'image_filename: ', image_filename
          print 'data_filename: ', data_filename

          self.createImgFromData(image_filename, data_filename)

          return (stdout_value, image_filename, data_filename)
        except OSError, e:
          err_mesg = 'The subprocess "%s" returns with an error: %s.' % (cmdstring, e)
          return (err_mesg, '', '')

    def createImgFromData(self, image_filename, data_filename):
        fh = Dataset(self.output_dir + '/' + data_filename, mode='r')
        varName = self.var
        print varName
        m = fh.variables[varName][:]
        nSample = fh.variables[varName+"_nSample"][:]
        dimVar1 = fh.variables[varName].dimensions[0]
        dimVar2 = fh.variables[varName].dimensions[1]
        y = fh.variables[dimVar1][:]
        x = fh.variables[dimVar2][:]

        displayOpt = int(self.displayOpt);
        x_opt = displayOpt % 2
        displayOpt = (displayOpt / 2)
        y_opt = displayOpt % 2
        displayOpt = (displayOpt / 2)
        z_opt = displayOpt % 2

        cmap_id = 'jet'

        dataForPlot = m.data
        dataForPlot[m.mask] = np.nan

        if z_opt:
          # to have dynamic range of 10^4
          z = math.log10(dataForPlot + 1e-4*npnanmax(dataForPlot))
        else:
          z = dataForPlot
          if np.nanmin(z) * np.nanmax(z) < 0 :
            cmap_id = 'bwr'

        if y_opt:
          y = math.log10(y)

        if x_opt:
          x = math.log10(x)

        (xx, yy) = np.meshgrid(x, y)

        zz = replace_nans(z, 9, 0); 
        zz = scipy.ndimage.zoom(zz, 3, prefilter=False)
        xx = scipy.ndimage.zoom(xx, 3, prefilter=False)
        yy = scipy.ndimage.zoom(yy, 3, prefilter=False)
        z_gf = gaussian_filter(zz, 1.4)
        print 'data smoothed = ', z_gf
        x_gf = xx
        y_gf = yy

        cLim = [np.nanmin(z_gf), np.nanmax(z_gf)]
        print 'clim = ', cLim
        cvec = np.linspace(cLim[0], cLim[1], 7);

        f1 = plt.figure(figsize = (10.0, 8.0)) ;
        plt.pcolor(x_gf, y_gf, z_gf, cmap = cmap_id)
        plt.clim(cLim[0], cLim[1])
        cbar = plt.colorbar(ticks = cvec, orientation = 'horizontal')
        plt.hold
        CS = plt.contour(x_gf, y_gf, gaussian_filter(scipy.ndimage.zoom(nSample, 3), 1.4), 10, colors = 'k')
        plt.clabel(CS, fontsize = 9, inline = 1)
        plt.title(fh.getncattr('title'))
        plt.xlabel(fh.getncattr('x_labelStr'))
        plt.ylabel(fh.getncattr('y_labelStr'))
        if y_opt :
          currYTick = plt.yticks()
          plt.xticks(currYTick, [str(pow(10,y)) for y in currYTick[0]])

        if x_opt:
          currXTick = plt.xticks()
          plt.xticks(currXTick, [str(pow(10,x)) for x in currXTick[0]])

        if z_opt:
          cbar.ax.set_xticklabels(["%4.2e" % (pow(10,x)) for x in cvec])
        else:
          print 'max = ' + str(np.max(abs(cvec))) 
          print 'min = ' + str(np.min(abs(cvec))) 
          if ((np.max(abs(cvec)) < 0.01) or  (np.min(abs(cvec)) > 1000)) :
            cbar.ax.set_xticklabels(["%4.2e" % (x) for x in cvec])
          else:
            cbar.ax.set_xticklabels(["%5.2f" % (x) for x in cvec])

        cbar.ax.set_xlabel(fh.variables[varName].getncattr('long_name') + '(' + fh.variables[varName].getncattr('units') + ')')
        fh.close()
        plt.savefig(self.output_dir + '/' + image_filename)

        

if __name__ == '__main__':
    #./octaveWrapper giss_e2-r clw 200101 200212 '0 360' '-90 90' '20000 90000' '1,2,3,4,5,6,7,8,9,10,11,12' 'giss_e2-r' tos '294,295,296,297,298, 299, 300, 301, 302, 303, 304, 305' '' '/tmp/'
    # c1 = call_conditionalSampling('cccma_canesm2', 'ts', '200101', '200212', '0', '360', '-90', '90', '', '', '5,6,7,8', 'cccma_canesm2', 'tos', '294','305','20', '',  './', '0')
    ### c1 = call_conditionalSampling('giss_e2-r', 'clw', '200101', '200212', '0', '360', '-30', '30', '20000', '90000', '5,6,7,8', 'giss_e2-r', 'tos', '294','305','20', '-1',  './', '6')

    #c1 = call_conditionalSampling2Var('ncc_noresm', 'cli', '200001', '200202', '0', '360', '-60', '60', '20000', '25000', '3,4,5', 'ncc_noresm', 'tos', '290','303','13', '-999999', 'ncc_noresm', 'wap', '-0.06', '0.06', '6', '50000',  './', '0')
    c1 = call_conditionalSampling2Var('gfdl_esm2g', 'clt', '200401', '200412', '0', '360', '-90', '90', '-999999', '-999999', '1,2,3,4,5,6,7,8,9,10,11,12', 'gfdl_esm2g', 'ta', '220','280','21', '50000', 'gfdl_esm2g', 'hur', '1', '98', '20', '70000',  './', '0')

    mesg = c1.displayConditionalSampling2Var()
    print 'mesg: ', mesg


### ./octaveWrapper giss_e2-r cli 200001 200202 0,360 -30,30 20000,90000 3,4,5 giss_e2-r ta 294,305,20 200 /home/svc/cmac/trunk/services/svc/svc/static/conditionalSampling/70ba451132c303980b8195252cf26364 3
### causes division by zero and index out of bounds errors


