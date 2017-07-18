from netCDF4 import Dataset
import netCDF4 
import os
def checkNc(fn, dict1):
  varList = []
  varDict = {}
  check1 = ''

  temp1 = os.path.split(fn)
  dict1['filename'] = temp1[1]

  print "in checkNc: ", fn
  try:
    nc = Dataset(fn)
  except Exception as e :
    dict1['message'] += "File on server is not found: %s \n\n%s"%(fn, repr(e))
    dict1['success'] = False
    return None

  varListAll = nc.variables.keys()
  
  str1 = ''
  dimList = []
  for var in varListAll:
    units1 = ''
    d1 = nc.variables[var]
    try:
      units1 = d1.units 
    except:
      temp1 = var.find('_bnds')
      if temp1==-1:
        check1 += var + ': need the units attribute.\n'

    print 'here 1'
    longName = var
    try:
      longName = d1.lone_name 
    except: pass
    try:
      longName = d1.lonename 
    except: pass
    try:
      longName = d1.name 
    except: pass
      
    print 'here 2'
    # to remove u' (unicode thing)
    dim1 = list(d1.dimensions)
    for i in range(len(dim1)):
      dim1[i] = str(dim1[i])
    dim1 = tuple(dim1)
 
    if var.find('_bnds')==-1:
      str1 += '%s: %s\n'%(var, str(dim1))
      dimList += list(dim1)

    varDict[var] = {'dim':  dim1, 
                    'units': units1,
                    'longName': longName,
                   }

  print 'here 3'
  str1 += '\nDimension Variables\n'
  dimList = list(set(dimList))
  dimDict = {}
  for dimVar in dimList:
    d2 = nc.variables[dimVar]
    print 'here 3a'
    try:
      time1 = netCDF4.num2date(d2[0], d2.units).timetuple()
      a1 = '%04d-%02d-%02d %02d:%02d:%02d'%(time1[0], time1[1], time1[2], time1[3], time1[4], time1[5])
      time2 = netCDF4.num2date(d2[-1], d2.units).timetuple()
      a2 = '%04d-%02d-%02d %02d:%02d:%02d'%(time2[0], time2[1], time2[2], time2[3], time2[4], time2[5])
    except:
      try:
        a1 = d2.min()
        a2 = d2.max()      
      except:
        a1 = 0
        a2 = 0
    str1 += '%s: %s to %s\n'%(dimVar, a1, a2)
    varDict[dimVar]['min'] = a1
    varDict[dimVar]['max'] = a2

  print 'here 4'
  varList = []
  for k in varListAll:
    if k not in dimList and k.find('_bnds')==-1: 
      varList.append(k)

  nc.close()
  check1 += '\nThe netCDF file has %d variables:\n%s'%(len(varList), str1) 

  dict1['varDict'] = varDict 
  dict1['varList'] = varList
  dict1['dimList'] = dimList 
  dict1['check'] = check1

  return None


