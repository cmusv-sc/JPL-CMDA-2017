# call_EOF.py
import string
import subprocess
import os
from os.path import basename

class call_universalPlotting:
    def __init__(self, pFile):
        self.pFile = pFile

    def display(self):

        ### print 'current dir: ', os.getcwd()
        # inputs: model name, variable name, start-year-mon, end-year-mon, 'start lon, end lon', 'start lat, end lat', 'mon list'
        # example: ./octaveWrapper ukmo_hadgem2-a ts 199001 199512 '0,100' '-29,29' '4,5,6,10,12'
                 #'%g'%self.lon1 + ',' + '%g'%self.lon2 + ' ' + '%g'%self.lat1 + ',' + '%g'%self.lat2 + ' ' + \
        '''
        inputs = str(self.nVar)
        for iVar in range(self.nVar):
          inputs = inputs + ' ' + self.models[iVar] + ' ' + self.vars1[iVar] + ' ' + self.pres1[iVar]

        inputs = inputs + ' ' + self.months + ' ' + \
                 self.lon1 + ',' + self.lon2 + ' ' + self.lat1 + ',' + self.lat2 + ' ' + \
                 self.output_dir 

        print 'inputs: ', inputs
        command = './wrapper ' +  inputs
        cmd = command.split(' ')
        cmdstring = string.join(cmd, ' ')
        print 'cmdstring: ', cmdstring
'''

        #print 'self.pFile: ', self.pFile
        import os
        #print "os.path.isfile('./wrapper'): ", os.path.isfile('./wrapper')
        command = './wrapper ' + self.pFile
        print command 
        cmd = command.split(' ')
        cmdstring = string.join(cmd, ' ')
        #print 'cmd: ', cmd
        #if 1:
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

          image_filename = os.path.basename(image_filename)
          print 'image_filename: ', image_filename
          data_filename = os.path.basename(data_filename)
          print 'data_filename: ', data_filename
          return (stdout_value, image_filename, data_filename)
        #if 0:
        except OSError, e:
          err_mesg = 'The subprocess "%s" returns with an error: %s.' % (cmdstring, e)
          return (err_mesg, '', '')


if __name__ == '__main__':

    c1 = call_randomForest(\
         '3', 
         'ukmo_hadgem2-a', 'ts', '200', 
         'ukmo_hadgem2-a', 'clt', '200', 
         'ukmo_hadgem2-a', 'clt', '200', 
         '0', '100', '-29', '29', \
         '/home/svc/cmac/trunk/services/svc/svc/static/randomForest')

    mesg = c1.display()
    print 'mesg: ', mesg


