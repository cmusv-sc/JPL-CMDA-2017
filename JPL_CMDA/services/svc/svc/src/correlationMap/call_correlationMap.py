# call_correlationMap.py
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

class call_correlationMap:
    def __init__(self, pFile):

        self.pFile = pFile

        '''
        availableTimeBnds = correctTimeBounds2('2', 
          model1.replace("_", "/"), var1, model2.replace("_", "/"), 
          var2, start_time, end_time)
        self.start_time = availableTimeBnds[0]
        self.end_time = availableTimeBnds[1]
'''

    def display(self):

        command = './wrapper ' +  self.pFile
        cmd = command.split(' ')
        cmdstring = string.join(cmd, ' ')
        print 'cmdstring: ', cmdstring

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

          image_filename = os.path.basename(image_filename)
          print 'image_filename: ', image_filename
          data_filename = os.path.basename(data_filename)
          print 'data_filename: ', data_filename
          return (stdout_value, image_filename, data_filename)
        except OSError, e:
          err_mesg = 'The subprocess "%s" returns with an error: %s.' % (cmdstring, e)
          return (err_mesg, '', '')


if __name__ == '__main__':

    c1 = call_scatterPlot2V(\
         'ukmo_hadgem2-a', 'ts', '200', 'ukmo_hadgem2-a', 'clt', '200', '5', '199001', '199512', '0', '100', '-29', '29', \
         '/home/svc/cmac/trunk/services/svc/svc/static/scatterPlot2V')

    mesg = c1.display()
    print 'mesg: ', mesg


    """
    c1 = call_scatterPlot2V(\
         'ukmo_hadgem2-a', 'ts', '200', 'ukmo_hadgem2-a', 'clt', '200', '199001', '199512', '0', '100', '-29', '29', 500, \
         '/home/svc/cmac/trunk/services/svc/svc/static/diffPlot2V', 1)

    mesg = c1.display()
    print 'mesg: ', mesg
    """

