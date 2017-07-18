# call_threeDimVerticalProfile.py
import string
import subprocess
import os
from os.path import basename

if __name__ == '__main__':
  import sys
  sys.path.append('../time_bounds')
  from getTimeBounds import correctTimeBounds1
else:
  from svc.src.time_bounds.getTimeBounds import correctTimeBounds1

class call_threeDimVerticalProfile:
    def __init__(self, model, var, start_time, end_time, lon1, lon2, lat1, lat2, months, output_dir, displayOpt):
        self.model = model
        self.var = var
        self.lon1 = lon1
        self.lon2 = lon2
        self.lat1 = lat1
        self.lat2 = lat2
        self.months = months
        self.output_dir = output_dir
        self.displayOpt = displayOpt
        availableTimeBnds = correctTimeBounds1('1', model.replace("_", "/"), var, start_time, end_time)
        self.start_time = availableTimeBnds[0]
        self.end_time = availableTimeBnds[1]

        # temporary fix
        # This application level knowledge may not belong here
        if self.model == 'NASA_AMSRE' and self.var == 'ts':
          self.var = 'tos'


    def displayThreeDimVerticalProfile(self):

        ### print 'current dir: ', os.getcwd()
        # inputs: model name, variable name, start-year-mon, end-year-mon, 'start lon, end lon', 'start lat, end lat', 'mon list'
        # example: ./octaveWrapper ncc_noresm cli 197501 199512 '0 180' '-30 30' '5,6,7,8' ./tmp
        inputs = self.model + ' ' + self.var + ' ' + self.start_time + ' ' + self.end_time + ' ' + \
                 self.lon1 + ',' + self.lon2 + ' ' + self.lat1 + ',' + self.lat2 + ' ' + \
                 self.months + ' ' + self.output_dir + ' ' + self.displayOpt
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
    c1 = call_threeDimVerticalProfile('ncc_noresm', 'cli', '197501', '199512', '0', '180', '-30', '30', '5,6,7,8', './', '7')

    mesg = c1.displayThreeDimVerticalProfile()
    print 'mesg: ', mesg

