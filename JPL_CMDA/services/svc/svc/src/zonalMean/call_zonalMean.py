# call_zonalMean.py
import string
import subprocess
import os
from os.path import basename

if __name__ == '__main__':
  import sys
  sys.path.append('../time_bounds')
  sys.path.append('../py')
  from getTimeBounds import correctTimeBounds1
else:
  from svc.src.time_bounds.getTimeBounds import correctTimeBounds1

class call_zonalMean:
    def __init__(self, varInfoStr, outputDir, displayOpt):

        self.varInfo = varInfoStr
        self.outputDir = outputDir
        self.displayOpt = displayOpt

    def display_zonalMean(self):

        inputs = self.varInfo + ' ' + self.outputDir + ' ' + self.displayOpt
        print 'inputs: ', inputs
        command = './octaveWrapper ' +  inputs
        cmd = command.split(' ')
        cmdstring = string.join(cmd, ' ')
        print 'cmdstring: ', cmdstring

#        if self.start_time == '0' or self.end_time == '0':
#         return ('No Data', '', '')

        try:
          proc=subprocess.Popen(cmd, cwd='.', stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
          # wait for the process to finish
          stdout_value, stderr_value = proc.communicate()
          print 'stdout_value: ', stdout_value
          print 'stderr_value: ', stderr_value

          # libGL tend to give an unharmful error message, so we will ignore it
          if stderr_value.find('error:') >= 0 and stderr_value.find('error:') != stderr_value.find('error: failed to load driver: swrast') :
             return (stderr_value, '')

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
    c1 = call_zonalMean('/home/svc/new_github/CMDA/JPL_CMDA/services/svc/svc/static/anomaly/1491956720051/data_anomaly.nc', './', '0')
    mesg = c1.display_zonalMean()
    print 'mesg: ', mesg
