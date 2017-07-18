# call_threeDimZonalMean.py
import string
import subprocess
import os
from os.path import basename

if __name__ == '__main__':
  import sys
  sys.path.append('../time_bounds')
  from getTimeBounds import correctTimeBounds2
else:
  from svc.src.time_bounds.getTimeBounds import correctTimeBounds2

class call_conditionalSampling:
    def __init__(self, data_source, var, start_time, end_time, lon1, lon2, lat1, lat2, pres1, pres2, months, env_var_source, env_var, bin_min, bin_max, bin_n, env_var_plev, output_dir, displayOpt):
        self.data_source = data_source		# for e.g. "NCAR_cam5" or "nasa_airs", etc
        self.var = var				# CMIP5 variable names, e.g. 'ta', 'hus', 'clt'
        self.lon1 = lon1			# longitude range, min, units = deg
        self.lon2 = lon2			# longitude range, max, units = deg
        self.lat1 = lat1			# latitude range, min, units = deg
        self.lat2 = lat2			# latitude range, max, units = deg
        self.pres1 = pres1			# pressure level 1 for pressure range 
        self.pres2 = pres2			# pressure level 2 for pressure range 
        self.months = months			# month index to specify season, e.g. 6,7,8 for boreal summer
        self.env_var_source = env_var_source	# large scale environmental variable data source, e.g. "NCAR_cam5"
        self.env_var = env_var			# large scale environmental variable CMIP5 name, e.g. 'ts', 'tos'
        self.bin_min = bin_min			# min value of bin boundary for sorting large scale env var
        self.bin_max = bin_max			# max value of bin boundary for sorting large scale env var
        self.bin_n = bin_n			# number of bins to be used
        self.env_var_plev = env_var_plev	# pressure level for env var if it is 3-d
        self.output_dir = output_dir		# output directory for figure and data file
        self.displayOpt = displayOpt		# display option, if in binary, the last 3 bits = [z y x]
        availableTimeBnds = correctTimeBounds2('2', data_source.replace("_", "/"), var, env_var_source.replace("_", "/"), env_var, start_time, end_time)
        self.start_time = availableTimeBnds[0]
        self.end_time = availableTimeBnds[1]
						# z = map scale, y = vertical axis, x = horizontal axis
						# 1 = log, 0 = lin

    def displayConditionalSampling(self):

        inputs = self.data_source + ' ' + self.var + ' ' + self.start_time + ' ' + self.end_time + ' ' + \
                 self.lon1 + ',' + self.lon2 + ' ' + self.lat1 + ',' + self.lat2 + ' ' + \
                 self.pres1 + ',' + self.pres2 + ' ' + self.months + ' ' + \
                 self.env_var_source + ' ' + self.env_var + ' ' + \
                 self.bin_min + ',' + self.bin_max + ',' + self.bin_n + ' ' + \
                 self.env_var_plev + ' ' + self.output_dir + ' ' + self.displayOpt
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
          return (stdout_value, image_filename, data_filename)
        except OSError, e:
          err_mesg = 'The subprocess "%s" returns with an error: %s.' % (cmdstring, e)
          return (err_mesg, '', '')


if __name__ == '__main__':
    #./octaveWrapper giss_e2-r clw 200101 200212 '0 360' '-90 90' '20000 90000' '1,2,3,4,5,6,7,8,9,10,11,12' 'giss_e2-r' tos '294,295,296,297,298, 299, 300, 301, 302, 303, 304, 305' '' '/tmp/'
    # c1 = call_conditionalSampling('cccma_canesm2', 'ts', '200101', '200212', '0', '360', '-90', '90', '', '', '5,6,7,8', 'cccma_canesm2', 'tos', '294','305','20', '',  './', '0')
    ### c1 = call_conditionalSampling('giss_e2-r', 'clw', '200101', '200212', '0', '360', '-30', '30', '20000', '90000', '5,6,7,8', 'giss_e2-r', 'tos', '294','305','20', '-1',  './', '6')

    c1 = call_conditionalSampling('giss_e2-r', 'cli', '200001', '200202', '0', '360', '-30', '30', '20000', '90000', '3,4,5', 'giss_e2-r', 'ta', '200','230','20', '20000',  './', '6')

    mesg = c1.displayConditionalSampling()
    print 'mesg: ', mesg


### ./octaveWrapper giss_e2-r cli 200001 200202 0,360 -30,30 20000,90000 3,4,5 giss_e2-r ta 294,305,20 200 /home/svc/cmac/trunk/services/svc/svc/static/conditionalSampling/70ba451132c303980b8195252cf26364 3
### causes division by zero and index out of bounds errors


