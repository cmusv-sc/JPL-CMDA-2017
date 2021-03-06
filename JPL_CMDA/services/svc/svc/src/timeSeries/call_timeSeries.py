# call_timeSeries.py
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

class call_timeSeries:
    def __init__(self, varInfoStr, outputDir, displayOpt):

        self.varInfo = varInfoStr
        self.outputDir = outputDir
        self.displayOpt = displayOpt

    def display_timeSeries(self):

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

          if stderr_value.find('error:') >= 0:
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
    c1 = call_timeSeries('ncc_noresm ta 500 100,140 -20,20 ncc_noresm ta 700 240,260 -20,20 ncc_noresm ta 600 160,240 -40,-20 ncc_noresm ts -999999 40,200 20,40 199001 200312', './', '0')
    mesg = c1.display_timeSeries()
    print 'mesg: ', mesg
