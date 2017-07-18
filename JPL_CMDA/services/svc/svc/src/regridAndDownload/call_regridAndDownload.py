# call_twoDimMap.py
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

class call_regridAndDownload:
    def __init__(self, model, var, start_time, end_time, lon1, lon2, dlon, lat1, lat2, dlat, plev, output_dir):
        self.model = model
        self.var = var
        self.lon1 = lon1
        self.lon2 = lon2
        self.dlon = dlon
        self.lat1 = lat1
        self.lat2 = lat2
        self.dlat = dlat
        self.plev = plev
        self.output_dir = output_dir
        availableTimeBnds = correctTimeBounds1('1', model.replace("_", "/"), var, start_time, end_time)
        self.start_time = availableTimeBnds[0]
        self.end_time = availableTimeBnds[1]

        # temporary fix
        # This application level knowledge may not belong here
        if self.model == 'NASA_AMSRE' and self.var == 'ts':
          self.var = 'tos'


    def regridAndDownload(self):

        ### print 'current dir: ', os.getcwd()
        # inputs: model name, variable name, start-year-mon, end-year-mon, 'start lon, end lon', 'start lat, end lat', 'mon list'
        # example: ./octaveWrapper ukmo_hadgem2-a ts 199001 199512 '0,100' '-29,29' '4,5,6,10,12'
        inputs = self.model + ' ' + self.var + ' ' + self.start_time + ' ' + self.end_time + ' ' + \
                 self.lon1 + ',' + self.lon2 + ',' + self.dlon + ' ' + self.lat1 + ',' + self.lat2 + ',' + self.dlat + ' ' + \
                 self.plev + ' ' + self.output_dir
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
            ## print '*****: ', line
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
    ### c1 = call_twoDimMap('ukmo_hadgem2-a', 'ts', '199001', '199512', '0', '100', '-29', '29', '4,5,6,10,12', '/home/svc/cmac/trunk/services/twoDimMap/twoDimMap/static/')
    ### c1 = call_twoDimMap('cccma_canam4', 'ts', '199001', '199512', '0', '100', '-29', '29', '4,5,6,10,12', '/home/svc/cmac/trunk/services/twoDimMap/twoDimMap/static/')
    c1 = call_regridAndDownload('ncc_noresm', 'ta', '199001', '200012', '0', '360', '4', '-90', '90', '4',  '100000,80000,50000,30000,20000,10000', './')
    ### c1 = call_twoDimMap('ukmo_hadgem2-es', 'ts', '199001', '199512', '0', '100', '-29', '29', '4,5,6,10,12', '/home/svc/cmac/trunk/services/twoDimMap/twoDimMap/static/')

    mesg = c1.regridAndDownload()
    print 'mesg: ', mesg
