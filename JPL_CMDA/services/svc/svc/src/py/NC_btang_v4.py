#aaaa14a2 def save2nc(array, ncfile=None, name='data',\
#aaaa14a3 def nc_modify(oldNcFile, newNcFile=None, op=None)
#aaaa14a4 def get_offset(ncVar)
#== def_copy_att
#== def_copy_dim
#== def_copy_var

import os, string, time
from netCDF4 import Dataset
import numpy as np

tmpDir = '/tmp'
axislib0 = {
'x':{'name': 'lon',   'unit': 'degree_east',                  },
'y':{'name': 'lat',   'unit': 'degree_north',                 },
'z':{'name': 'depth', 'unit': 'meter',                        }, 
't':{'name': 'time',  'unit': 'days since 1900-01-01 00:00:00'},
'i':{'name': 'index', 'unit': 'i'},
'j':{'name': 'indexJ', 'unit': 'i'},
'k':{'name': 'indexK', 'unit': 'i'},
}

#aaaa14a2 def save2nc(array, ncfile=None, name='data',\
def save2nc(array, ncfile=None, name=None,\
unit='', missing_value=None, title='', \
#axisorder='tzyx', \
axisorder='iiiiii', \
axisarray=[None,None,None,None], \
newfile=0, \
format='NETCDF3_64BIT', \
axislib=axislib0):

  nDim = len(array.shape)

  # create a temp nc file
  if ncfile:
    newfile1 = newfile
    tempFile = ncfile
    if newfile:
      nc=Dataset(tempFile, 'w', format=format)
    else:
      nc=Dataset(tempFile, 'a')
  else:
    temp1 = string.replace(str(time.time()), '.', '_')
    tempFile = '%s/data_%s.cdf' %(tmpDir, temp1)

    nc=Dataset(tempFile, 'w', format=format)
    newfile1 = 0
 
  if title:
    nc.title = title

  # pick a prefix for axis name. 
  # The prefix should not have been used in the existing ncfile.
  prefix1 = 'a'

  if not newfile1:
    temp1 = string.join(nc.dimensions.keys(), ' ')
    # not to use 'd'
    temp3 = string.letters[:4] + string.letters[5:26]
    for i in temp3:
      if '%s_'%i not in temp1:
        prefix1 = i
        break
      
  # define axes
  # Note that in netcdf, as in numpy, the fastest changing index in ferret is
  # the last one.
  axisName1 = ['','','','']
  axis1 = [None,None,None,None]
  axisorder1 = axisorder[-nDim:]
  for i in range(len(array.shape)):
    # get axis name
    if axisorder1[i] in axislib.keys():
      axisName1[i] = axislib[axisorder1[i]]['name']
    else: 
      axisName1[i] = '%s_%d'%(prefix1, i+1)

    # axis name already in the nc file?
    existing1 = 0
    if not newfile1:
      if axisName1[i] in nc.dimensions.keys():
        if len(nc.dimensions[axisName1[i]]) != array.shape[i]:
          print 'array dimension does not match the existing dimension:'
          print 'nc.dimensions[axisName1[i]] != array.shape[i]'
          #print '%d: %d != %d' \
          #      %(i, nc.dimensions[axisName1[i]], array.shape[i])
          nc.close()
          return
        existing1 = 1

    # no need to define axis if it is already in ncfile.
    if existing1:
      continue

    # get axis values
    if type( axisarray[i] )!=type(None):
      axis1[i] = axisarray[i]
    else:
      axis1[i] = np.arange(1,array.shape[i]+1).astype('f')

    # create dimension, axis, and assing values
    nc.createDimension(axisName1[i], array.shape[i])
    temp1 = nc.createVariable(axisName1[i], axis1[i].dtype,(axisName1[i],))
    temp1[:] = axis1[i]

    # axis unit
    if axisorder1[i] in axislib.keys():
      temp1.units = axislib[axisorder1[i]]['unit']

  # the variable name
  if name:
    name1 = name

    # cannot overwrite existing variable
    if name1 in nc.variables.keys():
      print 'Variable name %s is already in the cdf file.'%name1
      nc.close()
      return

  else:
    name1 = 'data'
    i = 0
    while name1 in nc.variables.keys():
      i += 1
      name1 = 'data%d'%i
    print '%s is the variable name.' %name1

  # define variable
  if missing_value:
    temp1 = nc.createVariable(name1, array.dtype, \
    tuple(axisName1[:nDim]), fill_value=missing_value)
  else:
    temp1 = nc.createVariable(name1, array.dtype, \
    tuple(axisName1[:nDim]))

  temp1[:] = array
  if unit:
    temp1.units = unit
  #if missing_value:
  #  # do I need to change type here?

  #  temp1.missing_value = missing_value
  #  temp1._FillValue = missing_value

  nc.close()

  return tempFile


#aaaa14a3 def nc_modify(oldNcFile, newNcFile=None, op=None)
def nc_modify(oldFile, newFile=None, op=None, printint=100):
  '''
op:
SST=$DATA                              -- rename
DATA=$DATA+1                           -- change values without rename
SST=($DATA+1).astype('f')              -- rename and change type
SST:_FillValue=Num.array(-9999.0,'f')  -- add or change attribute value
SST(time,lat,lon)=$SST                 -- change the 3 axis names to time, lat, lon
_MAIN_:comment='aaccc'                 -- add file att
                                            
Rules:
- Only one variable is allowed in one expression.
- A variable can only appears once.
- In changing a att, if the varName changes, specify the new varName.
- Unless there is only one step for att change, a new file is generated.

Done:
- allow multiple steps of changes

TODO:
- find a way to change axis precision
- add function to convert 'd' to 's'
- change var missing value

- allow multiple variables in expression
- allow creation of new variable
- option of saving only the new variable
- allow i,j to deal with large array

Test
import NC_btang_v2 as NC1
reload(NC1)
# size 5447472
nc1 = '/home/btang/install/ferret/fer_dsets/data/coads_climatology.cdf'  
NC1.nc_modify(nc1, 'temp12.nc', op="sst=$SST.astype('d');time=$TIME")

reload(NC1)
NC1.nc_modify(nc1, 'temp12.nc', op="sst1=$SST.astype('d');time=$TIME;sst1:_FillValue=Num.array(-999,'f')")

reload(NC1)
nc1 = '/home/btang/install/ferret/fer_dsets/data/coads_climatology.cdf'  
NC1.nc_modify(nc1, 'temp12.nc', op="__:comment='aadd';SST(x1,x2,x3)=$SST.astype('d')")

# on spartan
reload(NC1)
nc2 = '/hosts/ourocean2/data9/btang/blending_02/data/blended/20090225/global.nc'
NC1.nc_modify(nc2, 'temp12.nc', op="__:comment='aadd';SST(x1,x2,x3)=$SST")

slice 

'''
  # search_patterns
  # parse_op
  # loop_ops
    # attribute_pattern
    # variable_pattern
    # save_op_properties

  # change_one_att
    # change_attr

  # always_need new nc file from here on

  # open_old_file
  # check_var_exist
  # change_axis_name
  # create_new_nc_file
  # create_file_attributes

  # calc_name_change
  # loop_opList_for_name_change
    # change_value
    # change_var_name
      # change_dimension_name

  # inverse_varName9, to be used in att setting

  # create_dimensions
  # loop_variables
    # create_new_variable
    # assign_attributes

  # change_att
      # change_file_att
      # change_var_att
  # close_both_new and old files

  import re
  cwd1 = os.getcwd() 

  # search_patterns
  # att match
  p1 = re.compile(r'([a-zA-Z_]\w*):([a-zA-Z_]\w*)=(.*)$')

  # new variable match
  p2 = re.compile(r'([a-zA-Z_]\w*)=(.*)$')

  # new variable match, with axes
  p2a = re.compile(r'([a-zA-Z_]\w*)\((.*?)\)=(.*)$')

  # old variable search
  p3 = re.compile(r'\$([a-zA-Z_]\w*)')

  # old variable index search. not yet used.
  p4 = re.compile(r'\$([a-zA-Z_]\w*)\[(.*)\]')

  # typecode search
  p5 = re.compile(r'astype\((.*?)\)')

  '''
# experiment with re
import re
p1 = re.compile(r'([a-zA-Z_]\w*):([a-zA-Z_]\w*)=(.*)$')
m = p1.match("adf_dfd:xyz=45.astype('f')")
m.groups()

p2 = re.compile(r'([a-zA-Z_]\w*)=')
m = p2.search("adf_dfd5=$xyz5__.astype('f')")
m.groups()

p2a = re.compile(r'([a-zA-Z_]\w*)\((.*?)\)=(.*)$')
m = p2a.search("adf_dfd5(time,lat,lon)=$xyz5__.astype('f')")
m.groups()

p4 = re.compile(r'\$([a-zA-Z_]\w*)\[(.*)\]')
m = p4.search("add=$acc[x=50:60].astype('d')")
m.groups()
 
p5 = re.compile(r'astype\((.*?)\)')
m = p5.search("adf_dfd5=$xyz5__.astype('f')")
m.groups()

'''
  # parse_op
  opList = []

  ops = op.split(';')

  oo = {
    'attExp': None,
    'attName': None,
    'varName': None,
    'varExp': None,
    'axisNew': None,
    'varNameNew': None,
    'typecode': None,
  }

  # loop_ops
  for op1 in ops:

    o1 = oo.copy()

    # attribute_pattern
    temp1 = p1.match(op1)
    if temp1:
      o1['varNameNew'] = temp1.groups()[0]
      o1['attName'] = temp1.groups()[1]
      o1['attExp'] = temp1.groups()[2]

    # variable_pattern
    else:
      op2 = op1.replace('$','')
      temp2 = p2.match(op2)
      temp2a = p2a.match(op2)

      if temp2:
        o1['varNameNew'] = temp2.groups()[0]
        o1['varExp'] = temp2.groups()[1]

      if temp2a:
        o1['varNameNew'] = temp2a.groups()[0]
        o1['axisNew'] = temp2a.groups()[1].split(',')
        o1['varExp'] = temp2a.groups()[2]

      temp3 = p3.search(op1)
      if temp3:
        o1['varName'] = temp3.groups()[0]
        o1['varExp'] = o1['varExp'].replace(o1['varName'], "nc.variables['%s'][:]"%(o1['varName']))

      temp4 = p5.search(op1)
      if temp4:
        o1['typecode'] = eval( temp4.groups()[0] )

        if (not o1['varNameNew']) or (not o1['varName']):
          print '!!!!!!!!! The new variable name not specified.'
          return None

    # save_op_properties
    opList.append(o1)

  #import pdb; pdb.set_trace()
       
  # change_one_att
  if len(opList)==1 \
     and opList[0]['attName'] \
     and (not newFile):

    nc=Dataset(oldFile, 'r+')
    o = opList[0]

    # change_attr
    if o['attName']:
      var0 = nc.variables[o['varNameNew']]
      temp1 = 'var0.%s=%s'%(o['attName'], o['attExp']) 
      exec(temp1)
      nc.close()
    return

  # always_need new nc file from here on

  if newFile:
    newFileName = newFile
  else:
    newFileName = os.join(cwd1, 'temp999.nc')

  # open_old_file
  nc=Dataset(oldFile, 'r')

  # check_var_exist
  for o in opList:
    if o['varName']:
      if o['varName'] not in nc.variables.keys():
        nc.close()
        print '!!!!!!!!!!!! %s is NOT in %s '%(o['varName'], oldFile)
        return None

  # change_axis_name
  varChange = [o['varName'] for o in opList]
  opList2 = []
  for o in opList:
    if o['axisNew']!=None:
      var1 = nc.variables[o['varName']]
      dim1 = var1.dimensions
      if len(dim1)!=len(o['axisNew']):
        print "len(dim1)!=len(o['axisNew']): ", len(dim1), len(o['axisNew'])
        return None

      opList2 = []
      for i in range(len(dim1)):
        if dim1[i] in varChange:
          print 'Varname to be changed is specified more than once: ', dim1[i]
          return None

        o1 = oo.copy()
        o1['varName'] = dim1[i] 
        o1['varNameNew'] = o['axisNew'][i] 
        o1['varExp'] = "nc.variables['%s'][:]"%(o1['varName'])
        opList2.append(o1)

      # only the first axisNew is used.
      break
  opList += opList2
 
  # create_new_nc_file
  ncNew=Dataset(newFile, 'w')

  # create_file_attributes
  for a in nc.__dict__.keys():
    temp3 = 'ncNew.%s = nc.__dict__[a]'%(a)
    exec(temp3)

  # calc_name_change
  varName9 = {}
  dimName9 = {}
  varValue9 = {}
  typecode9 = {}

  for v in nc.variables.keys():
    varName9[v] = v
    varValue9[v] = "nc.variables['%s']"%v
    typecode9[v] = nc.variables[v].dtype

  for v in nc.dimensions.keys():
    dimName9[v] = v

  # loop_opList_for_name_change
  for o in opList:

    if o['varExp']:
      # change_value
      varValue9[o['varName']] = o['varExp']

      # change_var_name
      varName9[o['varName']] = o['varNameNew']

      if o['typecode']:
        typecode9[o['varName']] = o['typecode']

      # change_dimension_name
      if o['varName'] in nc.dimensions.keys():
        dimName9[o['varName']] = o['varNameNew']

  # inverse_varName9, to be used in att setting
  varName10 = {}
  for v in varName9.keys():
    varName10[varName9[v]] = v 

  # create_dimensions
  for d in nc.dimensions.keys():
    ncNew.createDimension(dimName9[d], nc.dimensions[d])

  # loop_variables
  variablesNew = {}
  for v in nc.variables.keys():
    var3 = nc.variables[v]
    dim8 = tuple( [dimName9[i] for i in var3.dimensions] )
    
    # create_new_variable
    variablesNew[v] = ncNew.createVariable(varName9[v], typecode9[v], dim8)

    #print dim8
    #print ncNew.dimensions
    #print variablesNew[v].shape
    #print varValue9[v]
    #print eval(varValue9[v]+'.shape')

    if len(dim8)==1:
      variablesNew[v][:,] = eval(varValue9[v])[:,]

    elif len(dim8)==2:
      nLat9 = ncNew.dimensions[dim8[-2]]
      print 'assign variable: ', varValue9[v], '  :',
      for j in range(nLat9):
        if j%printint==0:
          print j,
        variablesNew[v][j,:] = eval(varValue9[v]+'[%d,:]'%j)
      print ''

    elif len(dim8)==3:
      nLat9 = ncNew.dimensions[dim8[-2]]
      print 'assign variable: ', varValue9[v], '  :',
      for j in range(nLat9):
        if j%printint==0:
          print j,
        variablesNew[v][:,j,:] = eval(varValue9[v]+'[:,%d,:]'%j)
      print ''

    # assign_attributes
    for a in var3.__dict__.keys():
      exec('variablesNew[v].%s = var3.__dict__[a]'%(a) )
  
  # change_att
  for o in opList:
    if o['attName']:
      # change_file_att
      if o['varNameNew']=='__':
        temp1 = 'ncNew.%s=%s'%(o['attName'], o['attExp']) 
      # change_var_att
      else: 
        v1 = varName10[o['varNameNew']]
        var0 = variablesNew[v1]
        temp1 = 'var0.%s=%s'%(o['attName'], o['attExp']) 

      exec(temp1)

  #import pdb; pdb.set_trace()

  # close_both_new and old files
  nc.close()
  ncNew.close()
   
#aaaa14a4 def get_offset(ncVar)
def get_offset(ncVar):
  try:
    scale1 = ncVar.scale_factor[0]
    offset1 = ncVar.add_offset[0]
  except:
    scale1 = 1.0
    offset1 = 0.0

  return scale1, offset1

#== def_copy_att
def copy_att(nc1, nc2, overwrite=0):
  attr1 = nc1.ncattrs()
  attr2 = nc2.ncattrs()

  for a in attr1:
    nc2.setncattr(a, nc1.getncattr(a))

#== def_copy_dim
def copy_dim(nc1, nc2, overwrite=0):
  # overwrite is working
  dim1 = nc1.dimensions
  dim2 = nc2.dimensions

  key1 = dim1.keys()
  key2 = dim2.keys()

  #import pdb; pdb.set_trace()
  for d in key1:
    create1 = 1
    if d in key2:
      if overwrite==0:
        create1 = 0

    if create1==1:
      nc2.createDimension(d, len(dim1[d]))

#== def_copy_var
def copy_var(nc1, nc2, name1, name2=None, overwrite=0):
  if name2 is None:
    name2 = name1

  vars1 = nc1.variables
  vars2 = nc2.variables
  v1 = vars1[name1]

  #try:
  v2 = nc2.createVariable(name2, v1.dtype, v1.dimensions)
  v2[:] = v1[:]
  copy_att(v1, v2)

  #except:
  #  print 'variable name exists: %s'%name2


