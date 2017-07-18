# call_collocation.py
import string
import subprocess
import os
from os.path import basename

class call_collocation:
    def __init__(self, 
sourceData = 'mls-h2o',
targetData = 'cloudsat',
timeS = '2008-05-01T00:00:00',
timeE = '2008-05-01T01:00:00',
output_dir = '/home/svc/cmac/trunk/services/twoDimMap/twoDimMap/static/'):

        self.sourceData = sourceData
        self.targetData = targetData 

        self.timeS = timeS
        self.timeE = timeE
        self.output_dir = output_dir

    def display(self):
        inputs = \
                 self.sourceData + ' ' + \
                 self.targetData + ' ' + \
                 self.timeS + ' ' + \
                 self.timeE + ' ' + \
                 self.output_dir 

        print 'inputs: ', inputs
        #command = '/home/bytang/projects/cmac/trunk/services/svc/svc/src/scatterPlot2V/wrapper ' +  inputs
        command = './wrapper ' +  inputs
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

          lines = stdout_value.split('\n')
          for line in lines:
            ### print '*****: ', line
            if line.find('figFile: ') >= 0:
              print '***** line: ', line
              image_filename = line[l1:]

          print 'image_filename: ', image_filename
          return (stdout_value, image_filename)

        except OSError, e:
          err_mesg = 'The subprocess "%s" returns with an error: %s.' % (cmdstring, e)
          return (err_mesg, '')

if __name__ == '__main__':
    c1 = call_collocation()

    mesg = c1.display()
    #print 'mesg: ' 
    #mesg = mesg.split('\n')
    for m in mesg: print m
