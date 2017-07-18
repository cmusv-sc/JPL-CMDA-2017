# call_multiModelStatistics.py
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

class call_multiModelStatistics:
    def __init__(self, varInfoStr, outputDir, displayOpt):

        self.varInfo = varInfoStr
        self.outputDir = outputDir
        self.displayOpt = displayOpt

    def generate_multiModelStatistics(self):

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
    c1 = call_multiModelStatistics('ts ncc_noresm,gfdl_cm3,ncar_cam5 -999999 20,200,5 -40,40,2 199001 200312', './', 'model1=NCAR_CAM5&var1=ts&pres1=-999999&model2=GFDL_ESM2G&var2=ts&pres2=-999999&purpose=Test%20work%20flow%20%2C%20surface%20temp%201&lonS=20&lonE=200&latS=-40&latE=40&timeS=199001&timeE=200312&fromPage=http://cmda-dev.jpl.nasa.gov:8080/assets/html/multiModelStatistics.html&userid=0')
    mesg = c1.generate_multiModelStatistics()
    print 'mesg: ', mesg
