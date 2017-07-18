#== def_convertPres
#== twoDimSlice3D__
#== correlationMap_
#== universalPlotting__
#== universalPlotting3__
#== podaac_
#== scatterPlot_
#== diffPlot2V__
#== conditionalSampling_
#== conditionalSampling2Var__
#== regridAndDownload__
#== randomForest__
#== EOF__
#== JointEOF__
#== conditionalPdf__
#== anomaly__
#== map2d__
#== mapPlot__
#== twoDimMap__
#== mapView__
#== mapViewWF__
#== timeSeriesWF_
#== timeSeries__
#== twoDimZonalMean__
#== threeDimZonalMean__
#== fileUpload__
#== universalP3
#== fileUpload2__
#== fileCheck__
#== threeDimVarVertical_
#== multiModelStatistics__
#== zonalMean__
#== testAxios__

import os, hashlib, shutil
from datetime import datetime, timedelta
import md5
import urllib2
import httplib
import json
#Added by Chris
import requests, time, json

from flask import jsonify, request, url_for, make_response
from flask import render_template
from werkzeug import secure_filename

from svc import app
from svc.src.twoDimMap import call_twoDimMap
from svc.src.twoDimSlice3D import call_twoDimSlice3D
from svc.src.mapView import call_mapView
from svc.src.mapViewWorkFlow import call_mapViewWorkFlow
from svc.src.timeSeries import call_timeSeries
from svc.src.timeSeriesWorkFlow import call_timeSeriesWorkFlow
from svc.src.zonalMean import call_zonalMean
from svc.src.timeSeries2D import call_timeSeries2D
from svc.src.twoDimZonalMean import call_twoDimZonalMean
from svc.src.threeDimZonalMean import call_threeDimZonalMean
from svc.src.threeDimVerticalProfile import call_threeDimVerticalProfile
from svc.src.scatterPlot2V import call_scatterPlot2V
from svc.src.conditionalSampling import call_conditionalSampling
from svc.src.conditionalSampling2Var import call_conditionalSampling2Var
#from svc.src.collocation import call_collocation
from svc.src.time_bounds import getTimeBounds
from svc.src.regridAndDownload import call_regridAndDownload
from svc.src.multiModelStatistics import call_multiModelStatistics
from svc.src.correlationMap import call_correlationMap
from svc.src.randomForest import call_randomForest
from svc.src.EOF import call_EOF
from svc.src.JointEOF import call_JointEOF
from svc.src.conditionalPdf import call_conditionalPdf
from svc.src.anomaly import call_anomaly
#from svc.src.anomaly import call_service
from svc.src.mapPlot import call_mapPlot
from svc.src.map2d import call_map2d
from svc.src.universalPlotting import call_universalPlotting
from svc.src.universalPlotting2 import call_universalPlotting2
from svc.src.universalPlotting3 import call_universalPlotting3
from svc.src.py import download_file_from_url
from svc.src.py import checkNc

from flask import current_app
from functools import update_wrapper

### CMU_PROVENANCE_URL = 'http://einstein.sv.cmu.edu:9034/serviceExecutionLog/addServiceExecutionLog'
CMU_PROVENANCE_URL = 'http://hawking.sv.cmu.edu:9005/serviceExecutionLog/addServiceExecutionLog'

### VIRTUAL_EINSTEIN_URL = 'http://ec2-54-183-194-175.us-west-1.compute.amazonaws.com:9034/serviceExecutionLog/addServiceExecutionLog'
### Why do we need virtual einstein?
### VIRTUAL_EINSTEIN_URL = 'http://ec2-54-183-11-107.us-west-1.compute.amazonaws.com:9034/serviceExecutionLog/addServiceExecutionLog'

HEADERS = {'Content-Type': 'application/json'}
### USE_CMU = True
USE_CMU = False

""" 
userIdDict = { 
              "admin": 1,
              "caquilinger": 2,
              "jbrodie": 3,
              "rbuchholz": 4,
              "fcannon": 5,
              "ochimborazo": 6,
              "mclavner": 7,
              "jgristey": 8,
              "nkille": 9,
              "mlinz": 10,
              "emaroon": 11,
              "gmarques": 12,
              "cmartinezvi": 13,
              "amerrifield": 14,
              "jnanteza": 15,
              "kneff": 16,
              "fpolverari": 17,
              "mroge": 18,
              "ksauter": 19,
              "htseng": 20,
              "abeatriz": 21,
              "hwei": 22,
              "kwillmot": 23,
              "dzermenodia": 24,
              "kzhang": 25,
              "lei": 26,
              "czhai": 27,
              "btang": 28,
              "jzhang": 29,
              "wwang": 30,
              "xwei": 31,
              "ifenty": 32,
              "jteixeira": 33,
              "ddrewry": 34,
              "hsu": 35,
              "kandreadis": 36,
              "zxing": 37,
              "tkubar": 38,
              "jjiang": 39,
              "qbao": 40,
              "mqi": 41,
              "rwang": 42
              }
""" 

IPDict = { 
              "54.183.194.175": 26,

              }


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


def get_host_port(cfg_file):
    myvars = {}
    myfile =  open(cfg_file)
    for line in myfile:
        name, var = line.partition("=")[::2]
        name = name.strip()
        var = var.strip('\n').strip()
        if name is not '' and var is not '':
            myvars[name] = var

    ### print myvars

    return myvars["HOSTNAME"], myvars["PORT"]


def url_is_alive(url):
  request = urllib2.Request(url)
  print request
  request.get_method = lambda: 'HEAD'
  print request.get_method

  try:
    print urllib2.urlopen(request)
    return True
  except urllib2.HTTPError:
    return False
  except urllib2.URLError:
    return False


def exists(site, path):
  conn = httplib.HTTPConnection(site)
  conn.request('HEAD', path)
  response = conn.getresponse()
  conn.close()
  return response.status == 200


#== def_convertPres
def convertPres(var1, pres1):
  if int(pres1) == -999999 :
    return str(pres1)
  if var1=='ot' or var1=='os':
    fac = 10000
  else:
    fac = 100
  return str(int(pres1)*fac)

#== def_generalServiceResp
def generalServiceResp (serviceObj):
    """Run service """
    executionStartTime = int(time.time())

    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    print "request.query_string: ", 
    print request.query_string

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    # the first argument is for direct input data files from a work flow or user upload

    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    try:
      seed_str = frontend_url
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/' + serviceObj.name + '/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/' + serviceObj.name)
      # instantiate the app. class
      serviceObj.setOutputDir(output_dir)
      # call the app. function
      (message, imgFileName, dataFileName) = serviceObj.display()
      # chdir back
      os.chdir(current_dir)
      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
           req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
           response2 = urllib2.urlopen(req2) 
           userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
 
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      backend_url = 'http://' + hostname + ':' + port + '/svc/' + serviceObj.name
      print 'backend_url: ', backend_url
      plotUrl = 'http://' + hostname + ':' + port + '/static/' + serviceObj.name + '/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/' + serviceObj.name + '/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 :
        success = False
        plotUrl = ''
        dataUrl = ''


    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)

    purpose = request.args.get('purpose')#"Test .\'\"\\purpose"
#    serviceConfigurationId = "Test .\'\"\\confId"
#    datasetLogId = "Test .\'\"\\logId"
    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print post_json
            print 'submitting provenance from ' + serviceObj.name + ' ...'
            print requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
            print 'submitted provenance'
        except:
            print 'Something went wrong with Wei\'s stuff'


    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

#== twoDimMap__
@app.route('/svc/twoDimMap', methods=["GET"])
@crossdomain(origin='*')
def displayTwoDimMap():
    """Run displayTwoDimMap"""
    executionStartTime = int(time.time())

    # status and message
    success = True
    message = "ok"
    ### url = ''
    plotUrl = ''
    dataUrl = ''

    # get model, var, start time, end time, lon1, lon2, lat1, lat2, months, scale
    model = request.args.get('model1', '').lower()
    var = request.args.get('var1', '')
    startT = request.args.get('timeS', '')
    endT = request.args.get('timeE', '')
    lon1 = request.args.get('lonS', '')
    lon2 = request.args.get('lonE', '')
    lat1 = request.args.get('latS', '')
    lat2 = request.args.get('latE', '')
    months = request.args.get('months', '')
    scale = request.args.get('scale1', '')
    purpose = request.args.get('purpose', '')
    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    #added by CMU
    parameters_json = {'model':model, 'var':var, 'startT':startT,
                       'endT':endT, 'lon1':lon1, 'lon2':lon2,
                       'lat1':lat1, 'lat2':lat2, 'months':months,
                       'scale':scale}

    print 'model: ', model
    print 'var: ', var
    print 'startT: ', startT
    print 'endT: ', endT
    print 'lon1: ', lon1
    print 'lon2: ', lon2
    print 'lat1: ', lat1
    print 'lat2: ', lat2
    print 'months: ', months
    print 'scale: ', scale

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      seed_str = model+var+startT+endT+lon1+lon2+lat1+lat2+months+scale
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/twoDimMap/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/twoDimMap')
      # instantiate the app. class
      c1 = call_twoDimMap.call_twoDimMap(model, var, startT, endT, lon1, lon2, lat1, lat2, months, output_dir, scale)
      # call the app. function
      (message, imgFileName, dataFileName) = c1.displayTwoDimMap()
      # chdir back
      os.chdir(current_dir)

      hostname, port = get_host_port("host.cfg")

      dirN2 = output_dir.split('static/')[1] 
      temp2 = '''
<!DOCTYPE html>

<html lang="en">
<head>
  <meta charset="utf-8">
        <script type="text/javascript" src="http://cds.jpl.nasa.gov/widgets/microplot/microplot-2.3.1/js/libs.js"></script>
        <script type="text/javascript" src="http://cds.jpl.nasa.gov/widgets/microplot/microplot-2.3.1/js/main.js"></script>

</head>

<body>
<div class="microplot-container"
   style="width: 500px;height: 500px;"
   microplot-dataset="http://cmda-dev.jpl.nasa.gov:8023/data/output/%s/%s/%s[]?output=json"
   microplot-colors-scheme="http://data.jpl.nasa.gov/colortable/matplotlib-1.2.1/jet/64[]?output=json"
   microplot-graph-vflip="true">
</div>
</body>
</html>
'''%(dirN2, dataFileName, var)
      pid2 = open('%s/microP.html'%output_dir, 'w')
      pid2.write(temp2)
      pid2.close()

      ### userId = 2

      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
          print 'hostname: ', hostname
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data')
          response2 = urllib2.urlopen(req2)
          userId = json.loads(response2.read())['username']
          print 'userId: ', userId
        except Exception, e:
          print 'e: ', e
          userId = 2
        """

      # get userId from userIdDict
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else:
        userId = 26
      """
 
      # get userId from IPDict
      ### userId = IPDict[hostname]

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      backend_url = 'http://' + hostname + ':' + port + '/svc/twoDimMap'
      print 'backend_url: ', backend_url
      plotUrl = 'http://' + hostname + ':' + port + '/static/twoDimMap/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/twoDimMap/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      """
      print exists(hostname + ':' + port, '/static/twoDimMap/' + tag + '/' + imgFileName)

      print 'test of plotUrl'
      print url_is_alive(plotUrl)
      print 'test of dataUrl'
      print url_is_alive(dataUrl)

      code1 = url_is_alive(dataUrl)
      print 'code1: ', code1
      if code1 is False:
        print '****** Error: %s not accessible' % dataUrl
        dataUrl = failedImgUrl

      code1 = url_is_alive(plotUrl)
      print 'code1: ', code1
      if code1 is False:
        print '****** Error: %s not accessible' % plotUrl
        plotUrl = failedImgUrl
      """

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 :
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in displayTwoDimMap()")
        message = str(e)

    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    # json dictionary for provenance service request
    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)

    if USE_CMU:
        try:
            print '======= call to CMU provenance service ======'
            print CMU_PROVENANCE_URL
            print post_json
            print requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
            print '======= end of call to CMU provenance service ======'
        except:
            print 'Something went wrong with Wei\'s stuff'

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

@app.route('/svc/twoDimMapPOST', methods=["POST"])
@crossdomain(origin='*')
def displayTwoDimMapPOST():
    """Run displayTwoDimMap"""
    executionStartTime = int(time.time())

    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    # get model, var, start time, end time, lon1, lon2, lat1, lat2, months, scale
    jsonData = request.json

    model = jsonData['model']
    var = jsonData['var']    
    startT = jsonData['start_time']
    endT = jsonData['end_time']
    lon1 = jsonData['lon1']
    lon2 = jsonData['lon2']
    lat1 = jsonData['lat1']
    lat2 = jsonData['lat2']
    months = jsonData['months']
    scale = jsonData['scale']

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    #added by Chris
    parameters_json = {'model':model, 'var':var, 'startT':startT,
                       'endT':endT, 'lon1':lon1, 'lon2':lon2,
                       'lat1':lat1, 'lat2':lat2, 'months':months,
                       'scale':scale}

    print 'model: ', model
    print 'var: ', var
    print 'startT: ', startT
    print 'endT: ', endT
    print 'lon1: ', lon1
    print 'lon2: ', lon2
    print 'lat1: ', lat1
    print 'lat2: ', lat2
    print 'months: ', months
    print 'scale: ', scale

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      seed_str = model+var+startT+endT+lon1+lon2+lat1+lat2+months+scale
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/twoDimMap/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/twoDimMap')
      # instantiate the app. class
      c1 = call_twoDimMap.call_twoDimMap(model, var, startT, endT, lon1, lon2, lat1, lat2, months, output_dir, scale)
      # call the app. function
      (message, imgFileName, dataFileName) = c1.displayTwoDimMap()
      # chdir back
      os.chdir(current_dir)

      hostname, port = get_host_port("host.cfg")

      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
           req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
           response2 = urllib2.urlopen(req2) 
           userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
 
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      ### url = 'http://cmacws.jpl.nasa.gov:8090/static/twoDimMap/' + tag + '/' + imgFileName
      ### url = 'http://' + hostname + ':' + port + '/static/twoDimMap/' + tag + '/' + imgFileName
      ### print 'url: ', url
      plotUrl = 'http://' + hostname + ':' + port + '/static/twoDimMap/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/twoDimMap/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 :
        success = False
        ### url = ''
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in displayTwoDimMap()")
        message = str(e)

    purpose = request.args.get('purpose')#"Test .\'\"\\purpose"
    executionEndTime = int(time.time())

    ### urlLink = 'model1=%s&var1=%s&lon1=%s&lon2=%s&lat1=%s&lat2=%s&startT=%s&endT=%s&months=%s&scale=%s&image=%s&data_url=%s' % (model,var,lon1,lon2,lat1,lat2,startT,endT,months,scale,plotUrl,dataUrl)
    urlLink = request.query_string
    print 'urlLink: ', urlLink

    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong with Wei\'s stuff'
    #/added by Chris

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

#== mapView__
@app.route('/svc/mapView', methods=["GET"])
@crossdomain(origin='*')
def display_mapView():
    """Run display_mapView"""
    executionStartTime = int(time.time())

    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    print "request.query_string: ", 
    print request.query_string

    # get model, var, start time, end time, lon1, lon2, lat1, lat2, scale

    nVar = int(request.args.get('nVar'))

    keywords = ['model', 'var', 'pres', 'lon1_', 'lon2_', 'lat1_', 'lat2_', 'start_time_', 'end_time_', 'month_']
    sep_dict = {'model': ' ', 'var': ' ', 'pres':' ', 'lon1_':',', 'lon2_':' ', 'lat1_':',', 'lat2_': ' ', 'start_time_': ' ', 'end_time_' : ' ', 'month_' : ' '}
    keyMap = {'model': 'model', 'var': 'var', 'pres':'pres', 'lon1_':'vlonS', 'lon2_':'vlonE', 'lat1_':'vlatS', 'lat2_': 'vlatE', 'start_time_': 'vtimeS', 'end_time_' : 'vtimeE', 'month_' : 'vmonths'}
    varInfoStr = ''
    parameters_json = {}
    for varI in range(1, nVar+2):
      for kk in keywords:
        thisKey = kk +str(varI)
        webKey = keyMap[kk] +str(varI)
        if request.args.has_key(webKey):
          parameters_json[thisKey] = request.args.get(webKey, '')
        else:
          #genKey = kk;
          #if genKey[-1] == '_' :
          #  genKey = genKey[0:(-1)]
          genKey = keyMap[kk][1:]
          print 'varI, genKey: ', 
          print varI, genKey
          parameters_json[thisKey] = request.args.get(genKey, '')
        varInfoStr += parameters_json[thisKey] + sep_dict[kk]

    print 'varInfoStr: ',
    print varInfoStr
    scale = request.args.get('scale', '')

    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      seed_str = varInfoStr+scale
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/mapView/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/mapView')
      # instantiate the app. class
      print varInfoStr
      print output_dir
      print scale
      c1 = call_mapView.call_mapView(varInfoStr.strip(), output_dir, scale)
      # call the app. function
      (message, imgFileName, dataFileName) = c1.display_mapView()
      # chdir back
      os.chdir(current_dir)

      hostname, port = get_host_port("host.cfg")

      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
           req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
           response2 = urllib2.urlopen(req2) 
           userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
 
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      backend_url = 'http://' + hostname + ':' + port + '/svc/mapView'
      print 'backend_url: ', backend_url
      plotUrl = 'http://' + hostname + ':' + port + '/static/mapView/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/mapView/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 :
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in display_mapView()")
        message = str(e)

    purpose = request.args.get('purpose')#"Test .\'\"\\purpose"
#    serviceConfigurationId = "Test .\'\"\\confId"
#    datasetLogId = "Test .\'\"\\logId"
    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)

    if USE_CMU:
        try:
            print post_json
            print requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong in provenance submission'


    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

#== mapViewWF__
@app.route('/svc/mapViewWorkFlow', methods=["GET"])
@crossdomain(origin='*')
def display_mapViewWorkFlow():
    """Run display_mapViewWorkFlow"""
    executionStartTime = int(time.time())

    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    print "request.query_string: ", 
    print request.query_string

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    # the first argument is for direct input data files from a work flow or user upload
    parameters_json = {}
    fileKey = 'inputDataFile'
    parameters_json[fileKey] = request.args.get(fileKey, '')
    if parameters_json[fileKey] == '' :
      varInfoStr = '/ '

      nVar = int(request.args.get('nVar'))

      # get model, var, pressure leve, start time, end time, lon1, lon2, lat1, lat2, month index within a year, scale
      keywords = ['model', 'var', 'pres', 'lon1_', 'lon2_', 'lat1_', 'lat2_', 'start_time_', 'end_time_', 'month_']
      sep_dict = {'model': ' ', 'var': ' ', 'pres':' ', 'lon1_':',', 'lon2_':' ', 'lat1_':',', 'lat2_': ' ', 'start_time_': ' ', 'end_time_' : ' ', 'month_' : ' '}
      keyMap = {'model': 'model', 'var': 'var', 'pres':'pres', 'lon1_':'vlonS', 'lon2_':'vlonE', 'lat1_':'vlatS', 'lat2_': 'vlatE', 'start_time_': 'vtimeS', 'end_time_' : 'vtimeE', 'month_' : 'vmonths'}
      parameters_json = {}
      for varI in range(1, nVar+2):
        for kk in keywords:
          thisKey = kk +str(varI)
          webKey = keyMap[kk] +str(varI)
          if request.args.has_key(webKey):
            parameters_json[thisKey] = request.args.get(webKey, '')
          else:
            genKey = keyMap[kk][1:]
            print 'varI, genKey: ', 
            print varI, genKey
            parameters_json[thisKey] = request.args.get(genKey, '')
          varInfoStr += parameters_json[thisKey] + sep_dict[kk]
    else:
      varInfoStr = parameters_json[fileKey]

    scale = request.args.get('scale', '')
    parameters_json['scale'] = scale;
    print '== varInfoStr: ',
    print varInfoStr

    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    try:
      seed_str = varInfoStr+scale
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/mapViewWorkFlow/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)

      if parameters_json[fileKey] != '' :
        url_list = parameters_json[fileKey].split(',')
        varInfoStr = ''
        vIdx = 0
        for thisURL in url_list:
          if len(thisURL) == 0:
            continue
          if thisURL[0] == '/':
            thisLocalFile = thisURL
          else :
            vIdx += 1
            file_basename = os.path.basename(thisURL)
            thisLocalFile = output_dir + '/v' + str(vIdx) + '_' + file_basename
            download_file_from_url.download_file_from_url(thisURL, thisLocalFile)
          if varInfoStr != '' :
            thisLocalFile = ',' + thisLocalFile
          varInfoStr = varInfoStr + thisLocalFile 

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/mapViewWorkFlow')
      # instantiate the app. class
      c1 = call_mapViewWorkFlow.call_mapViewWorkFlow(varInfoStr, output_dir, scale)
      # call the app. function
      (message, imgFileName, dataFileName) = c1.display_mapViewWorkFlow()
      # chdir back
      os.chdir(current_dir)
      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
           req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
           response2 = urllib2.urlopen(req2) 
           userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
 
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      backend_url = 'http://' + hostname + ':' + port + '/svc/mapViewWorkFlow'
      print 'backend_url: ', backend_url
      plotUrl = 'http://' + hostname + ':' + port + '/static/mapViewWorkFlow/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/mapViewWorkFlow/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 :
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in display_timeSeriesWorkFlow()")
        message = str(e)

    purpose = request.args.get('purpose')#"Test .\'\"\\purpose"
#    serviceConfigurationId = "Test .\'\"\\confId"
#    datasetLogId = "Test .\'\"\\logId"
    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print post_json
            print 'submitting provenance from mapViewWorkFlow ...'
            print requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
            print 'submitted provenance'
        except:
            print 'Something went wrong with Wei\'s stuff'


    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })


#== timeSeries__
@app.route('/svc/timeSeries', methods=["GET"])
@crossdomain(origin='*')
def display_timeSeries():
    """Run display_timeSeries"""
    executionStartTime = int(time.time())

    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    print "request.query_string: ", 
    print request.query_string

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    # the first argument is for direct input data files from a work flow or user upload
    parameters_json = {}
    fileKey = 'inputDataFile'
    parameters_json[fileKey] = request.args.get(fileKey, '')

    nVar = int(request.args.get('nVar'))
    varInfoStr = ''

    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    # get model, var, start time, end time, lon1, lon2, lat1, lat2, scale
    keywordMap = {
      'model':'model', 
      'var':'var', 
      'pres':'pres', 
      'lon1_':'vlonS',
      'lon2_':'vlonE',
      'lat1_':'vlatS',
      'lat2_':'vlatE',
    }
    keywords = ['model', 'var', 'pres', 'lon1_', 'lon2_', 'lat1_', 'lat2_']
    #keywords = keywordMap.keys()
    sep_dict = {'model': ' ', 'var': ' ', 'pres':' ', 'lon1_':',', 'lon2_':' ', 'lat1_':',', 'lat2_': ' '}

    # get information for each variables
    for varI in range(1, nVar+1):
      for kk in keywords:
        thisKey = kk +str(varI)
        thisKey2 = keywordMap[kk] +str(varI)
        parameters_json[thisKey] = request.args.get(thisKey2, '')
#       parameters_json[thisKey] = request.args.get(thisKey, '')
        print thisKey, thisKey2, request.args.get(thisKey2, '')
        if len(kk)==5:
          if kk[:5]=='model':
            parameters_json[thisKey] = parameters_json[thisKey].lower()

        varInfoStr += parameters_json[thisKey] + sep_dict[kk]

    varInfoStr += request.args.get('timeS', '') + ' '
    varInfoStr += request.args.get('timeE', '')

    scale = request.args.get('scale', '')
    parameters_json['scale'] = scale;
    print '== varInfoStr: ',
    print varInfoStr

    try:
      seed_str = varInfoStr+scale
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/timeSeries/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)

      if parameters_json[fileKey] != '' :
        file_basename = os.path.basename(parameters_json[fileKey])
        varInfoStr = output_dir + '/' + file_basename
        download_file_from_url.download_file_from_url(parameters_json[fileKey], varInfoStr)
        varInfoStr += ' '

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/timeSeries')
      # instantiate the app. class
      c1 = call_timeSeries.call_timeSeries(varInfoStr, output_dir, scale)
      # call the app. function
      (message, imgFileName, dataFileName) = c1.display_timeSeries()
      # chdir back
      os.chdir(current_dir)

      hostname, port = get_host_port("host.cfg")

      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
           req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
           response2 = urllib2.urlopen(req2) 
           userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
 
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      backend_url = 'http://' + hostname + ':' + port + '/svc/timeSeries'
      print 'backend_url: ', backend_url
      plotUrl = 'http://' + hostname + ':' + port + '/static/timeSeries/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/timeSeries/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 :
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in display_timeSeries()")
        message = str(e)

    purpose = request.args.get('purpose')#"Test .\'\"\\purpose"
#    serviceConfigurationId = "Test .\'\"\\confId"
#    datasetLogId = "Test .\'\"\\logId"
    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print post_json
            print requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong with Wei\'s stuff'


    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

#== timeSeriesWF_
@app.route('/svc/timeSeriesWorkFlow', methods=["GET"])
@crossdomain(origin='*')
def display_timeSeriesWorkFlow():
    """Run display_timeSeriesWorkFlow"""
    executionStartTime = int(time.time())

    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    print "request.query_string: ", 
    print request.query_string

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    # the first argument is for direct input data files from a work flow or user upload
    parameters_json = {}
    fileKey = 'inputDataFile'
    parameters_json[fileKey] = request.args.get(fileKey, '')
    if parameters_json[fileKey] == '' :
      varInfoStr = '/ '

      nVar = int(request.args.get('nVar'))

      # get model, var, start time, end time, lon1, lon2, lat1, lat2, scale
      keywordMap = {
        'model':'model', 
        'var':'var', 
        'pres':'pres', 
        'lon1_':'lonS',
        'lon2_':'lonE',
        'lat1_':'latS',
        'lat2_':'latE',
      }
      keywords = ['model', 'var', 'pres', 'lon1_', 'lon2_', 'lat1_', 'lat2_']
      #keywords = keywordMap.keys()
      sep_dict = {'model': ' ', 'var': ' ', 'pres':' ', 'lon1_':',', 'lon2_':' ', 'lat1_':',', 'lat2_': ' '}

      # get information for each variables
      for varI in range(1, nVar+1):
        for kk in keywords:
          thisKey = kk +str(varI)
          thisKey2 = keywordMap[kk] +str(varI)
          parameters_json[thisKey] = request.args.get(thisKey2, '')
          if len(kk)==5:
            if kk[:5]=='model':
              parameters_json[thisKey] = parameters_json[thisKey].lower()

          varInfoStr += parameters_json[thisKey] + sep_dict[kk]

      varInfoStr += request.args.get('timeS', '') + ' '
      varInfoStr += request.args.get('timeE', '')
    else:
      varInfoStr = parameters_json[fileKey]

    scale = request.args.get('scale', '')
    parameters_json['scale'] = scale;
    print '== varInfoStr: ',
    print varInfoStr

    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '': 
      userId = int(userId)
    else:
      userId = 0

    try:
      seed_str = varInfoStr+scale
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/timeSeriesWorkFlow/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)

      if parameters_json[fileKey] != '' :
        url_list = parameters_json[fileKey].split(',')
        varInfoStr = ''
        vIdx = 0
        for thisURL in url_list:
          if len(thisURL) == 0:
            continue
          if thisURL[0] == '/':
            thisLocalFile = thisURL
          else :
            vIdx += 1
            file_basename = os.path.basename(thisURL)
            thisLocalFile = output_dir + '/v' + str(vIdx) + '_' + file_basename
            download_file_from_url.download_file_from_url(thisURL, thisLocalFile)
          if varInfoStr != '' :
            thisLocalFile = ',' + thisLocalFile
          varInfoStr = varInfoStr + thisLocalFile 

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/timeSeriesWorkFlow')
      # instantiate the app. class
      c1 = call_timeSeriesWorkFlow.call_timeSeriesWorkFlow(varInfoStr, output_dir, scale)
      # call the app. function
      (message, imgFileName, dataFileName) = c1.display_timeSeriesWorkFlow()
      # chdir back
      os.chdir(current_dir)

      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
           req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
           response2 = urllib2.urlopen(req2) 
           userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
 
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      backend_url = 'http://' + hostname + ':' + port + '/svc/timeSeriesWorkFlow'
      print 'backend_url: ', backend_url
      plotUrl = 'http://' + hostname + ':' + port + '/static/timeSeriesWorkFlow/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/timeSeriesWorkFlow/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 :
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in display_timeSeriesWorkFlow()")
        message = str(e)

    purpose = request.args.get('purpose')#"Test .\'\"\\purpose"
#    serviceConfigurationId = "Test .\'\"\\confId"
#    datasetLogId = "Test .\'\"\\logId"
    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print post_json
            print 'submitting provenance from timeSeriesWorkFlow ...'
            print requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
            print 'submitted provenance'
        except:
            print 'Something went wrong with Wei\'s stuff'


    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })


@app.route('/svc/timeSeries2D', methods=["GET"])
@crossdomain(origin='*')
def display_timeSeries2D():
    """Run display_timeSeries2D"""
    executionStartTime = int(time.time())

    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    # get model, var, start time, end time, lon1, lon2, lat1, lat2, scale

    model = request.args.get('model', '')
    var = request.args.get('var', '')
    startT = request.args.get('start_time', '')
    endT = request.args.get('end_time', '')
    lon1 = request.args.get('lon1', '')
    lon2 = request.args.get('lon2', '')
    lat1 = request.args.get('lat1', '')
    lat2 = request.args.get('lat2', '')
    scale = request.args.get('scale', '')
    purpose = request.args.get('purpose', '')  #"Test .\'\"\\purpose"

    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url

    parameters_json = {'model':model, 'var':var, 'startT':startT,
                       'endT':endT, 'lon1':lon1, 'lon2':lon2,
                       'lat1':lat1, 'lat2':lat2, 'scale':scale}

    print 'model: ', model
    print 'var: ', var
    print 'startT: ', startT
    print 'endT: ', endT
    print 'lon1: ', lon1
    print 'lon2: ', lon2
    print 'lat1: ', lat1
    print 'lat2: ', lat2
    print 'scale: ', scale
    print 'purpose: ', purpose

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    try:
      seed_str = model+var+startT+endT+lon1+lon2+lat1+lat2+scale
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/timeSeries2D/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/timeSeries2D')
      # instantiate the app. class
      c1 = call_timeSeries2D.call_timeSeries2D(model, var, startT, endT, lon1, lon2, lat1, lat2, output_dir, scale)
      # call the app. function
      (message, imgFileName, dataFileName) = c1.display_timeSeries2D()
      # chdir back
      os.chdir(current_dir)

      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
          response2 = urllib2.urlopen(req2) 
          userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
 
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      backend_url = 'http://' + hostname + ':' + port + '/svc/timeSeries2D'
      print 'backend_url: ', backend_url
      plotUrl = 'http://' + hostname + ':' + port + '/static/timeSeries2D/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/timeSeries2D/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 :
        success = False
        url = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in display_timeSeries2D()")
        message = str(e)

#    serviceConfigurationId = "Test .\'\"\\confId"
#    datasetLogId = "Test .\'\"\\logId"
    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    print 'post_json: ', post_json

    ### post_json_addPicture = {'url':url}
    ### post_json_addPicture = json.dumps(post_json_addPicture)
    ### post_json_addOutputfile = {'url':dataUrl}
    ### post_json_addOutputfile = json.dumps(post_json_addOutputfile)
    ### print 'post_json_addPicture: ', post_json_addPicture
    ### print 'post_json_addOutputfile: ', post_json_addOutputfile

    if USE_CMU:
        try:
            print requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong with Wei\'s stuff'


    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

#== twoDimSlice3D__
@app.route('/svc/twoDimSlice3D', methods=["GET"])
# @app.route('/svc/twoDimSlice3D', methods=["POST"])
@crossdomain(origin='*')
def displayTwoDimSlice3D():

    """Run displayTwoDimSlice3D"""
    executionStartTime = int(time.time())
    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''
    
    # get model, var, start time, end time, pressure_level, lon1, lon2, lat1, lat2, months, scale
    model = request.args.get('model1', '').lower()
    var = request.args.get('var1', '')
    startT = request.args.get('timeS', '')
    endT = request.args.get('timeE', '')
    pr = request.args.get('pres1', '')
    lon1 = request.args.get('lonS', '')
    lon2 = request.args.get('lonE', '')
    lat1 = request.args.get('latS', '')
    lat2 = request.args.get('latE', '')
    months = request.args.get('months', '')
    scale = request.args.get('scale1', '')

    pr = convertPres(var, pr)
    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    '''
    jsonData = request.json

    model = jsonData['model']
    var = jsonData['var']    
    startT = jsonData['start_time']
    endT = jsonData['end_time']
    pr = jsonData['pr']
    lon1 = jsonData['lon1']
    lon2 = jsonData['lon2']
    lat1 = jsonData['lat1']
    lat2 = jsonData['lat2']
    months = jsonData['months']
    scale = jsonData['scale']
    '''
    parameters_json = {'model':model, 'var':var, 'startT':startT,
                       'endT':endT, 'pr':pr, 'lon1':lon1, 'lon2':lon2,
                       'lat1':lat1, 'lat2':lat2, 'months':months,
                       'scale':scale}

    print 'model: ', model
    print 'var: ', var
    print 'startT: ', startT
    print 'endT: ', endT
    print 'pr: ', pr
    print 'lon1: ', lon1
    print 'lon2: ', lon2
    print 'lat1: ', lat1
    print 'lat2: ', lat2
    print 'months: ', months
    print 'scale: ', scale

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      seed_str = model+var+startT+endT+pr+lon1+lon2+lat1+lat2+months+scale
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/twoDimSlice3D/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/twoDimSlice3D')
      # instantiate the app. class
      c1 = call_twoDimSlice3D.call_twoDimSlice3D(model, var, startT, endT, pr, lon1, lon2, lat1, lat2, months, output_dir, scale)
      # call the app. function
      (message, imgFileName, dataFileName) = c1.displayTwoDimSlice3D()
      # chdir back
      os.chdir(current_dir)

      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
          response2 = urllib2.urlopen(req2) 
          userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
      
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 26
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      backend_url = 'http://' + hostname + ':' + port + '/svc/twoDimSlice3D'
      print 'backend_url: ', backend_url
      plotUrl = 'http://' + hostname + ':' + port + '/static/twoDimSlice3D/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/twoDimSlice3D/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 :
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in displayTwoDimSlice3D()")
        message = str(e)

    purpose = request.args.get('purpose')#"Test .\'\"\\purpose"
    executionEndTime = int(time.time())

    ### urlLink = 'model1=%s&var1=%s&lon1=%s&lon2=%s&lat1=%s&lat2=%s&startT=%s&endT=%s&months=%s&scale=%s&image=%s&data_url=%s' % (model,var,lon1,lon2,lat1,lat2,startT,endT,months,scale,plotUrl,dataUrl)
    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    # json dictionary for provenance service request
    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print post_json
            print requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong with Wei\'s stuff'

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

#== twoDimZonalMean__
@app.route('/svc/twoDimZonalMean', methods=["GET"])
@crossdomain(origin='*')
def displayTwoDimZonalMean():
    """Run displayTwoDimZonalMean"""
    executionStartTime = int(time.time())
    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    # get model, var, start time, end time, lat1, lat2, months, scale

    model = request.args.get('model1', '').lower()
    var = request.args.get('var1', '')
    startT = request.args.get('timeS', '')
    endT = request.args.get('timeE', '')
    lat1 = request.args.get('latS', '')
    lat2 = request.args.get('latE', '')
    months = request.args.get('months', '')
    scale = request.args.get('scale1', '')  
    ### query_string = request.args.get('query_string', '')
    query_string = request.query_string
    frontend_url = request.args.get('fromPage', '')

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    parameters_json = {'data source':model, 'variable name':var, 'start year-month':startT,
                       'end year-month':endT,
                       'start lat (deg)':lat1, 'end lat (deg)':lat2, 'select months':months,
                       'variable scale':scale}

    print 'model: ', model
    print 'var: ', var
    print 'startT: ', startT
    print 'endT: ', endT
    print 'lat1: ', lat1
    print 'lat2: ', lat2
    print 'months: ', months
    print 'scale: ', scale
    print 'query_string: ', query_string

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      seed_str = model+var+startT+endT+lat1+lat2+months+scale
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/twoDimZonalMean/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/twoDimZonalMean')
      # instantiate the app. class
      c1 = call_twoDimZonalMean.call_twoDimZonalMean(model, var, startT, endT, lat1, lat2, months, output_dir, scale)
      # call the app. function
      ### print 'before the call to c1.displayTwoDimZonalMean() ...'
      (message, imgFileName, dataFileName) = c1.displayTwoDimZonalMean()
      ### print 'after the call to c1.displayTwoDimZonalMean()'
      # chdir back
      os.chdir(current_dir)

      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
          response2 = urllib2.urlopen(req2) 
          userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
      
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """
 
      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      backend_url = 'http://' + hostname + ':' + port + '/svc/twoDimZonalMean'
      print 'backend_url: ', backend_url
      plotUrl = 'http://' + hostname + ':' + port + '/static/twoDimZonalMean/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/twoDimZonalMean/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 :
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in displayTwoDimZonalMean()")
        message = str(e)

    purpose = request.args.get('purpose')#"Test .\'\"\\purpose"
#    serviceConfigurationId = "Test .\'\"\\confId"
#    datasetLogId = "Test .\'\"\\logId"
    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print post_json
            print requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong with Wei\'s stuff'

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

#== threeDimZonalMean__
@app.route('/svc/threeDimZonalMean', methods=["GET"])
@crossdomain(origin='*')
def displayThreeDimZonalMean():
    """Run displayThreeDimZonalMean"""
    executionStartTime = int(time.time())
    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    # get model, var, start time, end time, lat1, lat2, pres1, pres2, months, scale

    model = request.args.get('model1', '').lower()
    var = request.args.get('var1', '')
    startT = request.args.get('timeS', '')
    endT = request.args.get('timeE', '')
    lat1 = request.args.get('latS', '')
    lat2 = request.args.get('latE', '')
    pres1 = request.args.get('pres1', '')
    pres2 = request.args.get('pres1a', '')
    months = request.args.get('months', '')
    scale = request.args.get('scale2', '')
    query_string = request.query_string
    frontend_url = request.args.get('fromPage', '')

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    pres1 = convertPres(var, pres1)
    pres2 = convertPres(var, pres2)

    parameters_json = {'model':model, 'var':var, 'startT':startT,
                       'endT':endT, 
                       'lat1':lat1, 'lat2':lat2, 'pres1':pres1, 'pres2':pres2,
                       'months':months, 'scale':scale}

    print 'model: ', model
    print 'var: ', var
    print 'startT: ', startT
    print 'endT: ', endT
    print 'lat1: ', lat1
    print 'lat2: ', lat2
    print 'pres1: ', pres1
    print 'pres2: ', pres2
    print 'months: ', months
    print 'scale: ', scale

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      seed_str = model+var+startT+endT+lat1+lat2+pres1+pres2+months+scale
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/threeDimZonalMean/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/threeDimZonalMean')
      # instantiate the app. class
      c1 = call_threeDimZonalMean.call_threeDimZonalMean(model, var, startT, endT, lat1, lat2, pres1, pres2, months, output_dir, scale)
      # call the app. function
      ### (message, imgFileName) = c1.displayThreeDimZonalMean()
      (message, imgFileName, dataFileName) = c1.displayThreeDimZonalMean()
      # chdir back
      os.chdir(current_dir)

      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
          response2 = urllib2.urlopen(req2) 
          userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
      
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      backend_url = 'http://' + hostname + ':' + port + '/svc/threeDimZonalMean'
      print 'backend_url: ', backend_url
      plotUrl = 'http://' + hostname + ':' + port + '/static/threeDimZonalMean/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/threeDimZonalMean/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 :
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in displayThreeDimZonalMean()")
        message = str(e)

    purpose = request.args.get('purpose')#"Test .\'\"\\purpose"
#    serviceConfigurationId = "Test .\'\"\\confId"
#    datasetLogId = "Test .\'\"\\logId"
    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print post_json
            print requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong with Wei\'s stuff'


    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

#== fileUpload__
@app.route('/fileUpload', methods=["GET", "POST"])
@crossdomain(origin='*')
def fileUpload():
  uploadDir = '/home/svc/upload'
  ALLOWED_EXTENSIONS = set(['nc', 'cdf']) 
  #from flask import flash
  from werkzeug import secure_filename
  """Run fileUpload"""

  if request.method == 'POST':
    dict1 = {'success': True, 'message': '',}

    if 0: # a test
      dict1['message'] += "test. without uploading."
      form1 = request.form
      serverFile = str(form1.get('serverFile')) 
      filename1 = serverFile
      filename2 = os.path.join( uploadDir, filename1)
      #checkNc.checkNc(filename2, dict1)
      return jsonify(dict1)

    f = request.files['file']
    form1 = request.form
    serverFile = str(form1.get('serverFile')) 
    if f.filename=='':
      dict1['success'] = False
      dict1['message'] += 'No selected file'

    if '.' in f.filename and f.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
      filename = secure_filename(f.filename)
      temp1 = filename.rsplit('.',1)

      #if serverFile[:len(temp1[0])]==temp1[0]:
      #  dict1['message'] += "Flle already exists on server. Not to upload."
      #  filename1 = serverFile
      #  filename2 = os.path.join( uploadDir, filename1)
      #else:
      if 1:
        filename1 = temp1[0] + '_' + str(int(time.time())) + '.' + temp1[1]
        print filename1
        filename2 = os.path.join( uploadDir, filename1)
        f.save(filename2)
        dict1['message'] +=  "File has been uploaded."

      try:
        checkNc.checkNc(filename2, dict1)
      except Exception as e:
        dict1['success'] = False
        dict1['message'] += str(e)

    else:
      dict1['success'] = False
      dict1['message'] += 'Filename is not allowed.'

    return jsonify(dict1)

#== universalP3
@app.route("/universalP3")
@crossdomain(origin='*')
def universalP3():
  return render_template('aa.html')

#== fileUpload2__
@app.route("/fileUpload2", methods=["GET", "POST"])
@crossdomain(origin='*')
def upload():
  uploadDir = '/home/svc/upload'
  ALLOWED_EXTENSIONS = set(['nc', 'cdf']) 
  #from flask import flash
  from werkzeug import secure_filename

  if request.method=="POST":
    form = request.form

    # Create a unique "session ID" for this particular batch of uploads.
    #upload_key = str(uuid4())
    upload_key = ''

    # Is the upload using Ajax, or a direct POST by the form?
    is_ajax = True

    # Target folder for these uploads.
    #target = uploadDir
    #try:
    #    os.mkdir(target)
    #except:
    #    if is_ajax:
    #        return ajax_response(False, "Couldn't create upload directory: {}".format(target))
    #    else:
    #        return "Couldn't create upload directory: {}".format(target)

    print "=== Form Data ==="
    for key, value in form.items():
        print key, "=>", value

    for upload in request.files.getlist("file"):
        filename = upload.filename.rsplit("/")[0]
        # str() to remove u'
        destination = str("/".join([uploadDir, filename]))
        print "Accept incoming file:", filename
        print "Save it to:", destination
        upload.save(destination)

    success = True
    message = 'ok'
    status = 'ok'

    dict1 = {
      'success': success,
      'message': message,
      'status': status,
    }

    try:
      checkNc.checkNc(destination, dict1)
    except Exception as e:
      dict1['success'] = False
      dict1['message'] += "file check failed. \n" + str(e)

    print dict1
    return jsonify(dict1)



#== fileCheck__
@app.route('/fileCheck', methods=["GET", "POST"])
@crossdomain(origin='*')
def fileCheck0():
    #from flask import flash
    #from werkzeug import secure_filename
    """Run fileUpload"""
    if request.method == 'GET':
        dict1 = {'success': True, 'message': '',}

        #print 'yyyy'
        #print request.args.keys()
        #print dir(request.args)
        fn1 = request.args.get('file', '')

        # to undo the javascript escape()
        import urllib
        filename2 = urllib.unquote( str(fn1) )
        try:
          checkNc.checkNc(filename2, dict1)
        except Exception as e:
          dict1['success'] = False
          dict1['message'] += str(e)

        return jsonify(dict1)


#== threeDimVarVertical_
@app.route('/svc/threeDimVerticalProfile', methods=["GET"])
@crossdomain(origin='*')
def displayThreeDimVerticalProfile():
    """Run displayThreeDimVerticalProfile"""
    executionStartTime = int(time.time())
    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    # get model, var, start time, end time, lon1, lon2, lat1, lat2, months, scale

    model = request.args.get('model1', '').lower()
    var = request.args.get('var1', '')
    startT = request.args.get('timeS', '')
    endT = request.args.get('timeE', '')
    lon1 = request.args.get('lonS', '')
    lon2 = request.args.get('lonE', '')
    lat1 = request.args.get('latS', '')
    lat2 = request.args.get('latE', '')
    months = request.args.get('months', '')
    scale = request.args.get('scale3', '')
    query_string = request.query_string
    frontend_url = request.args.get('fromPage', '')

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    parameters_json = {'model':model, 'var':var, 'startT':startT,
                       'endT':endT, 'lon1':lon1, 'lon2':lon2,
                       'lat1':lat1, 'lat2':lat2, 'months':months,
                       'scale':scale}

    print 'model: ', model
    print 'var: ', var
    print 'startT: ', startT
    print 'endT: ', endT
    print 'lon1: ', lon1
    print 'lon2: ', lon2
    print 'lat1: ', lat1
    print 'lat2: ', lat2
    print 'months: ', months
    print 'scale: ', scale

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      seed_str = model+var+startT+endT+lat1+lat2+lon1+lon2+months+scale
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/threeDimVerticalProfile/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/threeDimVerticalProfile')
      # instantiate the app. class
      c1 = call_threeDimVerticalProfile.call_threeDimVerticalProfile(model, var, startT, endT, lon1, lon2, lat1, lat2, months, output_dir, scale)
      # call the app. function
      (message, imgFileName, dataFileName) = c1.displayThreeDimVerticalProfile()
      # chdir back
      os.chdir(current_dir)

      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
          response2 = urllib2.urlopen(req2) 
          userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
      
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """
 
      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      backend_url = 'http://' + hostname + ':' + port + '/svc/threeDimVerticalProfile'
      print 'backend_url: ', backend_url
      plotUrl = 'http://' + hostname + ':' + port + '/static/threeDimVerticalProfile/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/threeDimVerticalProfile/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 :
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in displayThreeDimVerticalProfile()")
        message = str(e)

    purpose = request.args.get('purpose')#"Test .\'\"\\purpose"
#    serviceConfigurationId = "Test .\'\"\\confId"
#    datasetLogId = "Test .\'\"\\logId"
    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)

    if USE_CMU:
        try:
            print post_json
            requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong with Wei\'s stuff'
    

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

#== universalPlotting__
@app.route('/svc/universalPlotting', methods=["GET"])
@crossdomain(origin='*')
def displayUniversalPlotting():
    """Run displayUniversalPlotting"""
    executionStartTime = int(time.time())
    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    center = []
    model = []
    var = []
    pres = []

    nVar = 1
    for i in range( nVar ):
      m1 = request.args.get('model'+str(i+1), '').lower()
      temp1 = m1.split('_')
      center.append(temp1[0])
      model.append(temp1[1])
      var.append(request.args.get('var'+str(i+1), ''))

    timeS = request.args.get('timeS', '')
    timeE = request.args.get('timeE', '')
    lonS = request.args.get('lonS', '')
    lonE = request.args.get('lonE', '')
    latS = request.args.get('latS', '')
    latE = request.args.get('latE', '')

    pres1 = request.args.get('pres1', '')
    pres1a = request.args.get('pres1a', '')

    lonMethod = request.args.get('lonMethod', '')
    latMethod = request.args.get('latMethod', '')
    presMethod = request.args.get('presMethod', '')
    timeMethod = request.args.get('timeMethod', '')

    ferretLevel = request.args.get('ferretLevel', '')
    colorMap = request.args.get('colorMap', '')
    plotTitle = request.args.get('plotTitle', '')

    userData = request.args.get('userData', '')
    userDataFile = request.args.get('userDataFile', '')
    userDataVar = request.args.get('userDataVar', '')
    userDataOpendap = request.args.get('userDataOpendap', '')

    uploadData = request.args.get('uploadData', '')
    uploadDataFilename = request.args.get('uploadDataFilename', '')
    uploadDataVar = request.args.get('uploadDataVar', '')

    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    json1 = {
       'center':center, 
       'model':model, 
       'varName':var, 
       'yearS':timeS[:4],
       'yearE':timeE[:4],
       'monthS':timeS[4:], 
       'monthE':timeE[4:], 
       'lonS':lonS, 
       'lonE':lonE,
       'latS':latS, 
       'latE':latE, 
       'pres1':pres1, 
       'pres1a':pres1a, 
       'lonMethod':lonMethod, 
       'latMethod':latMethod, 
       'presMethod':presMethod, 
       'timeMethod':timeMethod, 
       'userData':userData, 
       'userDataFile':userDataFile, 
       'userDataVar':userDataVar, 
       'userDataOpendap':userDataOpendap, 
       'uploadData':uploadData, 
       'uploadDataFilename':uploadDataFilename, 
       'uploadDataVar':uploadDataVar, 
       'ferretLevel':ferretLevel, 
       'colorMap':colorMap, 
       'plotTitle':plotTitle, 
    }

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir
    #if 1:
    try:
      seed_str = str(time.time())
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/universalPlotting/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)
      json1['outDir'] = output_dir

      import pickle
      pFile = '%s/p.pickle'%output_dir
      fid = open(pFile,'w')
      pickle.dump(json1, fid)
      fid.close()

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/universalPlotting')
      # instantiate the app. class
      c1 = call_universalPlotting.call_universalPlotting(pFile)
      # call the app. function (0 means the image created is scatter plot)
      ### (message, imgFileName) = c1.displayScatterPlot2V(0)
      (message, imgFileName, dataFileName) = c1.display()
      # chdir back
      os.chdir(current_dir)

      ind1 = message.find('No Data')
      if ind1>0:
        message1 = message[ind1:(ind1+200)]
        message1a = message1.split('\n')
        print message1a[0]
        print message1a[1]
     
      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
          response2 = urllib2.urlopen(req2) 
          userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
 
      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      purpose = request.args.get('purpose')#"Test .\'\"\\purpose"

      backend_url = 'http://' + hostname + ':' + port + '/svc/universalPlotting'
      print 'backend_url: ', backend_url
      print 'imgFileName: ', imgFileName
      plotUrl = 'http://' + hostname + ':' + port + '/static/universalPlotting/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/universalPlotting/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 or message.find('No Data') >= 0:
        success = False
        plotUrl = ''
        dataUrl = ''
    #if 0:
    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in displayScatterPlot2V()")
        message = str(e)

    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    # json dictionary for provenance service request
    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print post_json
            requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong with Wei\'s stuff'

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

#== universalPlotting3__
@app.route('/svc/universalPlotting3', methods=["GET"])
@crossdomain(origin='*')
def displayUniversalPlotting3():
    """Run displayUniversalPlotting3"""
    executionStartTime = int(time.time())
    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    json2 = {}
    keys = request.args.keys()
    for k in keys:
      json2[k] = request.args.get(k, '')

    userId = 0
    try:
      userId = int(json2['userId'])
    except:
      pass

    frontend_url = json2['fromPage']
    purpose = json2['purpose']

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir
    if 1:
    #try:
      seed_str = str(time.time())
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/universalPlotting3/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)
      json2['outDir'] = output_dir

      import pickle
      pFile = '%s/p.pickle'%output_dir
      fid = open(pFile,'w')
      pickle.dump(json2, fid)
      fid.close()

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/universalPlotting3')
      # instantiate the app. class
      c1 = call_universalPlotting.call_universalPlotting(pFile)
      # call the app. function (0 means the image created is scatter plot)
      ### (message, imgFileName) = c1.displayScatterPlot2V(0)
      (message, imgFileName, dataFileName) = c1.display()
      # chdir back
      os.chdir(current_dir)

      ind1 = message.find('No Data')
      if ind1>0:
        message1 = message[ind1:(ind1+200)]
        message1a = message1.split('\n')
        print message1a[0]
        print message1a[1]
     
      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
          response2 = urllib2.urlopen(req2) 
          userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
 
      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      purpose = request.args.get('purpose')#"Test .\'\"\\purpose"

      backend_url = 'http://' + hostname + ':' + port + '/svc/universalPlotting3'
      print 'backend_url: ', backend_url
      print 'imgFileName: ', imgFileName
      plotUrl = 'http://' + hostname + ':' + port + '/static/universalPlotting3/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/universalPlotting3/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 or message.find('No Data') >= 0:
        success = False
        plotUrl = ''
        dataUrl = ''
    if 0:
    #except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    #except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in displayScatterPlot2V()")
        message = str(e)

    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    # json dictionary for provenance service request
    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print post_json
            requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong with Wei\'s stuff'

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

#== podaac_
@app.route('/svc/podaac', methods=["GET"])
@crossdomain(origin='*')
def displayUniversalPlotting2():
    """Run displayUniversalPlotting"""
    executionStartTime = int(time.time())
    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    model = []
    var = []
    pres = []

    nVar = 1
    for i in range( nVar ):
      m1 = request.args.get('model'+str(i+1), '')
      temp1 = m1.split('_')
      model.append(m1)
      var.append(request.args.get('var'+str(i+1), ''))

    timeS = request.args.get('timeS', '')
    timeE = request.args.get('timeE', '')
    lonS = request.args.get('lonS', '')
    lonE = request.args.get('lonE', '')
    latS = request.args.get('latS', '')
    latE = request.args.get('latE', '')

    pres1 = request.args.get('pres1', '')
    pres1a = request.args.get('pres1a', '')

    lonMethod = request.args.get('lonMethod', '')
    latMethod = request.args.get('latMethod', '')
    presMethod = request.args.get('presMethod', '')
    timeMethod = request.args.get('timeMethod', '')

    ferretLevel = request.args.get('ferretLevel', '')
    colorMap = request.args.get('colorMap', '')
    plotTitle = request.args.get('plotTitle', '')

    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    json1 = {
       'model':model, 
       'varName':var, 
       'yearS':timeS[:4],
       'yearE':timeE[:4],
       'monthS':timeS[4:6], 
       'monthE':timeE[4:6], 
       'dayS':timeS[6:], 
       'dayE':timeE[6:], 
       'lonS':lonS, 
       'lonE':lonE,
       'latS':latS, 
       'latE':latE, 
       'pres1':pres1, 
       'pres1a':pres1a, 
       'lonMethod':lonMethod, 
       'latMethod':latMethod, 
       'presMethod':presMethod, 
       'timeMethod':timeMethod, 
       'ferretLevel':ferretLevel, 
       'colorMap':colorMap, 
       'plotTitle':plotTitle, 
    }

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir
    #if 1:
    try:
      seed_str = str(time.time())
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/universalPlotting2/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)
      json1['outDir'] = output_dir

      import pickle
      pFile = '%s/p.pickle'%output_dir
      fid = open(pFile,'w')
      pickle.dump(json1, fid)
      fid.close()

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/universalPlotting2')
      # instantiate the app. class
      c1 = call_universalPlotting2.call_universalPlotting(pFile)
      # call the app. function (0 means the image created is scatter plot)
      ### (message, imgFileName) = c1.displayScatterPlot2V(0)
      (message, imgFileName, dataFileName) = c1.display()
      # chdir back
      os.chdir(current_dir)

      ind1 = message.find('No Data')
      if ind1>0:
        message1 = message[ind1:(ind1+200)]
        message1a = message1.split('\n')
        print message1a[0]
        print message1a[1]
     
      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
          response2 = urllib2.urlopen(req2) 
          userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
 
      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      purpose = request.args.get('purpose')#"Test .\'\"\\purpose"

      backend_url = 'http://' + hostname + ':' + port + '/svc/universalPlotting2'
      print 'backend_url: ', backend_url
      print 'imgFileName: ', imgFileName
      plotUrl = 'http://' + hostname + ':' + port + '/static/universalPlotting2/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/universalPlotting2/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 or message.find('No Data') >= 0:
        success = False
        plotUrl = ''
        dataUrl = ''
    #if 0:
    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in displayScatterPlot2V()")
        message = str(e)

    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    # json dictionary for provenance service request
    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print post_json
            requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong with Wei\'s stuff'

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

#== scatterPlot_
@app.route('/svc/scatterPlot2Vars', methods=["GET"])
@crossdomain(origin='*')
def displayScatterPlot2V():
    """Run displayScatterPlot2V"""
    executionStartTime = int(time.time())
    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    # the old way 
    '''
    model1 = request.args.get('model1', '').lower()
    var1 = request.args.get('var1', '')
    pres1 = request.args.get('pres1', '')
    model2 = request.args.get('model2', '').lower()
    var2 = request.args.get('var2', '')
    pres2 = request.args.get('pres2', '')

    startT = request.args.get('timeS', '')
    endT = request.args.get('timeE', '')
    lon1 = request.args.get('lonS', '')
    lon2 = request.args.get('lonE', '')
    lat1 = request.args.get('latS', '')
    lat2 = request.args.get('latE', '')
    nSample = request.args.get('nSample', '')
    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url
'''

    # 
    center = []
    model = []
    var = []
    pres = []

    print "request.query_string: ", 
    print request.query_string
    nVar = 2
    for i in range( nVar ):
      m1 = request.args.get('model'+str(i+1), '').lower()
      temp1 = m1.split('_')
      center.append(temp1[0])
      model.append(temp1[1])
      var.append(request.args.get('var'+str(i+1), ''))
      pres.append(request.args.get('pres'+str(i+1), ''))

    startT = request.args.get('timeS', '')
    endT = request.args.get('timeE', '')
    lonS = request.args.get('lonS', '')
    lonE = request.args.get('lonE', '')
    latS = request.args.get('latS', '')
    latE = request.args.get('latE', '')
    nSample = request.args.get('nSample', '')
    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    '''
    parameters_json = {'model1':model1, 'var1':var1, 'pres1':pres1,
                       'model2':model2, 'var2':var2, 'pres2':pres2,
                       'startT':startT,
                       'endT':endT, 'lon1':lon1, 'lon2':lon2,
                       'lat1':lat1, 'lat2':lat2, 'nSample':nSample}
'''

    json1 = {
       'center':center, 
       'model':model, 
       'varName':var, 
       'pres':pres,
       'yearS':startT[:4],
       'yearE':endT[:4],
       'monthS':startT[4:], 
       'monthE':endT[4:], 
       'lon1S':lonS, 
       'lon1E':lonE,
       'lat1S':latS, 
       'lat1E':latE, 
       'nSample':nSample, 
       'queryString':request.query_string,
       'isDiffPlot':0,
    }
       

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      seed_str = str(time.time())
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/scatterPlot2V/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)
      json1['outDir'] = output_dir

      import pickle
      pFile = '%s/p.pickle'%output_dir
      fid = open(pFile,'w')
      pickle.dump(json1, fid)
      fid.close()

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/scatterPlot2V')
      # instantiate the app. class
      c1 = call_scatterPlot2V.call_scatterPlot2V(pFile)
      # call the app. function (0 means the image created is scatter plot)
      ### (message, imgFileName) = c1.displayScatterPlot2V(0)
      (message, imgFileName, dataFileName) = c1.display()
      # chdir back
      os.chdir(current_dir)

      ind1 = message.find('No Data')
      if ind1>0:
        message1 = message[ind1:(ind1+200)]
        message1a = message1.split('\n')
        print message1a[0]
        print message1a[1]
     
      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
          response2 = urllib2.urlopen(req2) 
          userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
      
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port
      print 'imgFileName: ', imgFileName

      backend_url = 'http://' + hostname + ':' + port + '/svc/scatterPlot2V'
      print 'backend_url: ', backend_url
      plotUrl = 'http://' + hostname + ':' + port + '/static/scatterPlot2V/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/scatterPlot2V/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 or message.find('No Data') >= 0:
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in displayScatterPlot2V()")
        message = str(e)

    purpose = request.args.get('purpose')#"Test .\'\"\\purpose"
    executionEndTime = int(time.time())

    # YYYYY
    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    # json dictionary for provenance service request
    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print post_json
            requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong with Wei\'s stuff'

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })


#== diffPlot2V__
@app.route('/svc/diffPlot2V', methods=["GET"])
@crossdomain(origin='*')
def displayDiffPlot2V():
    """Run displayDiffPlot2V"""
    executionStartTime = int(time.time())
    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    # 
    center = []
    model = []
    var = []
    pres = []

    print "request.query_string: ", 
    print request.query_string
    nVar = 2
    for i in range( nVar ):
      m1 = request.args.get('model'+str(i+1), '').lower()
      temp1 = m1.split('_')
      center.append(temp1[0])
      model.append(temp1[1])
      var.append(request.args.get('var'+str(i+1), ''))
      pres.append(request.args.get('pres'+str(i+1), ''))

    startT = request.args.get('timeS', '')
    endT = request.args.get('timeE', '')
    lonS = request.args.get('lonS', '')
    lonE = request.args.get('lonE', '')
    latS = request.args.get('latS', '')
    latE = request.args.get('latE', '')
    #nSample = request.args.get('nSample', '')
    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    json1 = {
       'center':center, 
       'model':model, 
       'varName':var, 
       'pres':pres,
       'yearS':startT[:4],
       'yearE':endT[:4],
       'monthS':startT[4:], 
       'monthE':endT[4:], 
       'lon1S':lonS, 
       'lon1E':lonE,
       'lat1S':latS, 
       'lat1E':latE, 
       'nSample':0, 
       'queryString':request.query_string,
       'isDiffPlot':1,
    }
       
    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      seed_str = str(time.time())
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/diffPlot2V/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)
      json1['outDir'] = output_dir

      import pickle
      pFile = '%s/p.pickle'%output_dir
      fid = open(pFile,'w')
      pickle.dump(json1, fid)
      fid.close()

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/scatterPlot2V')
      # instantiate the app. class
      c1 = call_scatterPlot2V.call_scatterPlot2V(pFile)
      # call the app. function (0 means the image created is scatter plot)
      ### (message, imgFileName) = c1.displayScatterPlot2V(0)
      (message, imgFileName, dataFileName) = c1.display()
      # chdir back
      os.chdir(current_dir)

      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
          response2 = urllib2.urlopen(req2) 
          userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
      
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      backend_url = 'http://' + hostname + ':' + port + '/svc/diffPlot2V'
      print 'backend_url: ', backend_url
      plotUrl = 'http://' + hostname + ':' + port + '/static/diffPlot2V/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/diffPlot2V/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 :
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in displayDiffPlot2V()")
        message = str(e)
    purpose = request.args.get('purpose')#"Test .\'\"\\purpose"
    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    # json dictionary for provenance service request
    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print post_json
            requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong with Wei\'s stuff'

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

#== conditionalSampling_
@app.route('/svc/conditionalSampling', methods=["GET"])
#@app.route('/svc/conditionalSampling', methods=["POST"])
@crossdomain(origin='*')
def displayConditionalSamp():
    """Run displayConditionalSamp"""
    executionStartTime = int(time.time())
    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    # get model1, var1, start time, end time, lon1, lon2, lat1, lat2, pres1, pres2, months, model2, var2, bin_min, bin_max, bin_n, env_var_plev, displayOpt
    model1 = request.args.get('model1', '').lower()
    var1 = request.args.get('var1', '')
    pres1 = request.args.get('pres1', '')
    pres2 = request.args.get('pres1a', '')
    model2 = request.args.get('model2', '').lower()
    var2 = request.args.get('var2', '')
    env_var_plev = request.args.get('pres2', '')
    startT = request.args.get('timeS', '')
    endT = request.args.get('timeE', '')
    lon1 = request.args.get('lonS', '')
    lon2 = request.args.get('lonE', '')
    lat1 = request.args.get('latS', '')
    lat2 = request.args.get('latE', '')
    months = request.args.get('months', '')
    bin_min = request.args.get('binMin2', '')
    bin_max = request.args.get('binMax2', '')
    bin_n = request.args.get('binN2', '')
    displayOpt = request.args.get('scale3', '')

    query_string = request.query_string
    frontend_url = request.args.get('fromPage', '')

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    pres1 = convertPres(var1, pres1)
    pres2 = convertPres(var1, pres2)
    env_var_plev = convertPres(var2, env_var_plev)

    # old edition
    '''
    model1 = request.args.get('model1', '')
    var1 = request.args.get('var1', '')
    startT = request.args.get('start_time', '')
    endT = request.args.get('end_time', '')
    lon1 = request.args.get('lon1', '')
    lon2 = request.args.get('lon2', '')
    lat1 = request.args.get('lat1', '')
    lat2 = request.args.get('lat2', '')
    pres1 = request.args.get('pres1', '')
    pres2 = request.args.get('pres2', '')
    months = request.args.get('months', '')
    model2 = request.args.get('model2', '')
    var2 = request.args.get('var2', '')
    bin_min = request.args.get('bin_min', '')
    bin_max = request.args.get('bin_max', '')
    bin_n = request.args.get('bin_n', '')
    env_var_plev = request.args.get('env_var_plev', '')
    displayOpt = request.args.get('displayOpt', '')
    '''

    parameters_json = {'model1':model1, 'var1':var1, 'pres1':pres1,
                       'model2':model2, 'var2':var2, 'pres2':pres2,
                       'startT':startT,
                       'endT':endT, 'lon1':lon1, 'lon2':lon2,
                       'lat1':lat1, 'lat2':lat2, 'months':months,
                       'bin_min':bin_min, 'bin_max':bin_max,
                       'bin_n':bin_n, 'env_var_plev':env_var_plev,
                       'displayOpt':displayOpt}

    print 'model1: ', model1
    print 'var1: ', var1
    print 'startT: ', startT
    print 'endT: ', endT
    print 'lon1: ', lon1
    print 'lon2: ', lon2
    print 'lat1: ', lat1
    print 'lat2: ', lat2
    print 'pres1: ', pres1
    print 'pres2: ', pres2
    print 'months: ', months
    print 'model2: ', model2
    print 'var2: ', var2
    print 'bin_min: ', bin_min
    print 'bin_max: ', bin_max
    print 'bin_n: ', bin_n
    print 'env_var_plev: ', env_var_plev
    print 'displayOpt: ', displayOpt

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      seed_str = model1+var1+startT+endT+lat1+lat2+lon1+lon2+pres1+pres2+months+model2+var2+bin_min+bin_max+bin_n+env_var_plev+displayOpt
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/conditionalSampling/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/conditionalSampling')
      # instantiate the app. class

      # c1 = call_conditionalSampling.call_conditionalSampling('giss_e2-r', 'clw', '200101', '200212', '0', '360', '-30', '30', '20000', '90000', '5,6,7,8', 'giss_e2-r', 'tos', '294','305','20', '',  './', '6')

      c1 = call_conditionalSampling.call_conditionalSampling(model1, var1, startT, endT, lon1, lon2, lat1, lat2, pres1, pres2, months, model2, var2, bin_min, bin_max, bin_n, env_var_plev, output_dir, displayOpt)
      # call the app. function
      (message, imgFileName, dataFileName) = c1.displayConditionalSampling()
      print 'imgFileName: ', imgFileName
      # chdir back
      os.chdir(current_dir)

      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
          response2 = urllib2.urlopen(req2) 
          userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
      
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      backend_url = 'http://' + hostname + ':' + port + '/svc/conditionalSampling'
      print 'backend_url: ', backend_url
      plotUrl = 'http://' + hostname + ':' + port + '/static/conditionalSampling/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/conditionalSampling/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 :
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)

    purpose = request.args.get('purpose')#"Test .\'\"\\purpose"
#    serviceConfigurationId = "Test .\'\"\\confId"
#    datasetLogId = "Test .\'\"\\logId"
    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print post_json
            print requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong with Wei\'s stuff'

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

#== conditionalSampling2Var__
@app.route('/svc/conditionalSampling2Var', methods=["GET"])
@crossdomain(origin='*')
def displayConditionalSamp2Var():
    """Run displayConditionalSamp2Var"""
    executionStartTime = int(time.time())
    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    # get model1, var1, start time, end time, lon1, lon2, lat1, lat2, pres1, pres2, months, model2, var2, bin_min, bin_max, bin_n, env_var_plev, displayOpt
    model1 = request.args.get('model1', '').lower()
    var1 = request.args.get('var1', '')
    model2 = request.args.get('model2', '').lower()
    var2 = request.args.get('var2', '')
    model3 = request.args.get('model3', '').lower()
    var3 = request.args.get('var3', '')
    startT = request.args.get('timeS', '')
    endT = request.args.get('timeE', '')
    lon1 = request.args.get('lonS', '')
    lon2 = request.args.get('lonE', '')
    lat1 = request.args.get('latS', '')
    lat2 = request.args.get('latE', '')
    pres1 = request.args.get('pres1', '')
    pres2 = request.args.get('pres1a', '')
    months = request.args.get('months', '')
    bin_min1 = request.args.get('binMin2', '')
    bin_max1 = request.args.get('binMax2', '')
    bin_n1 = request.args.get('binN2', '')
    bin_min2 = request.args.get('binMin3', '')
    bin_max2 = request.args.get('binMax3', '')
    bin_n2 = request.args.get('binN3', '')
    env_var_plev1 = request.args.get('pres2', '')
    env_var_plev2 = request.args.get('pres3', '')
    displayOpt = request.args.get('scale3', '')

    query_string = request.query_string
    frontend_url = request.args.get('fromPage', '')

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    pres1 = convertPres(var1, pres1)
    pres2 = convertPres(var1, pres2)
    env_var_plev1 = convertPres(var2, env_var_plev1)
    env_var_plev2 = convertPres(var3, env_var_plev2)

    '''
    jsonData = request.json   

    model1 = jsonData['model1']
    var1 = jsonData['var1']
    startT = jsonData['start_time']
    endT = jsonData['end_time']
    lon1 = jsonData['lon1']
    lon2 = jsonData['lon2']
    lat1 = jsonData['lat1']
    lat2 = jsonData['lat2']
    pres1 = jsonData['pres1']
    pres2 = jsonData['pres2']
    months = jsonData['months']
    model2 = jsonData['model2']
    var2 = jsonData['var2']
    bin_min = jsonData['bin_min']
    bin_max = jsonData['bin_max']
    bin_n = jsonData['bin_n']
    env_var_plev = jsonData['env_var_plev']
    displayOpt = jsonData['displayOpt']
    '''

    parameters_json = {'model1':model1, 'var1':var1, 'pres1':pres1, 'pres2':pres2,
                       'model2':model2, 'var2':var2, 
                       'model3':model3, 'var3':var3, 
                       'startT':startT,
                       'endT':endT, 'lon1':lon1, 'lon2':lon2,
                       'lat1':lat1, 'lat2':lat2, 'months':months,
                       'bin_min1':bin_min1, 'bin_max1':bin_max1,
                       'bin_n1':bin_n1, 'env_var_plev1':env_var_plev1,
                       'bin_min2':bin_min2, 'bin_max2':bin_max2,
                       'bin_n2':bin_n2, 'env_var_plev2':env_var_plev2,
                       'displayOpt':displayOpt}

    print 'model1: ', model1
    print 'var1: ', var1
    print 'startT: ', startT
    print 'endT: ', endT
    print 'lon1: ', lon1
    print 'lon2: ', lon2
    print 'lat1: ', lat1
    print 'lat2: ', lat2
    print 'pres1: ', pres1
    print 'pres2: ', pres2
    print 'months: ', months
    print 'model2: ', model2
    print 'var2: ', var2
    print 'bin_min1: ', bin_min1
    print 'bin_max1: ', bin_max1
    print 'bin_n1: ', bin_n1
    print 'env_var_plev1: ', env_var_plev1
    print 'bin_min2: ', bin_min2
    print 'bin_max2: ', bin_max2
    print 'bin_n2: ', bin_n2
    print 'env_var_plev2: ', env_var_plev2
    print 'displayOpt: ', displayOpt

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      seed_str = model1+var1+startT+endT+lat1+lat2+lon1+lon2+pres1+pres2+months+model2+var2+model3+var3+bin_min1+bin_max1+bin_n1+env_var_plev1+bin_min2+bin_max2+bin_n2+env_var_plev2+displayOpt
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/conditionalSampling2Var/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/conditionalSampling2Var')
      # instantiate the app. class

      # c1 = call_conditionalSampling.call_conditionalSampling('giss_e2-r', 'clw', '200101', '200212', '0', '360', '-30', '30', '20000', '90000', '5,6,7,8', 'giss_e2-r', 'tos', '294','305','20', '',  './', '6')

      c1 = call_conditionalSampling2Var.call_conditionalSampling2Var(model1, var1, startT, endT, lon1, lon2, lat1, lat2, pres1, pres2, months, 
        model2, var2, bin_min1, bin_max1, bin_n1, env_var_plev1, 
        model3, var3, bin_min2, bin_max2, bin_n2, env_var_plev2, 
        output_dir, displayOpt)

      # call the app. function
      (message, imgFileName, dataFileName) = c1.displayConditionalSampling2Var()
      print 'imgFileName: ', imgFileName
      # chdir back
      os.chdir(current_dir)

      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
          response2 = urllib2.urlopen(req2) 
          userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
 
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      backend_url = 'http://' + hostname + ':' + port + '/svc/conditionalSampling2Var'
      print 'backend_url: ', backend_url
      plotUrl = 'http://' + hostname + ':' + port + '/static/conditionalSampling2Var/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/conditionalSampling2Var/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 :
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)

    purpose = request.args.get('purpose')#"Test .\'\"\\purpose"
#    serviceConfigurationId = "Test .\'\"\\confId"
#    datasetLogId = "Test .\'\"\\logId"
    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print post_json
            print requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong with Wei\'s stuff'

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })



@app.route('/svc/co-locate', methods=["GET"])
@crossdomain(origin='*')
def displayColocation():
    """Run displayColocation"""
    executionStartTime = int(time.time())     
    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''
     
    # get source, target, start_time, end_time
     
    source = request.args.get('source', '')
    target = request.args.get('target', '')
    startT = request.args.get('start_time', '')
    endT = request.args.get('end_time', '')

    parameters_json = {'source':source, 'target':target,
                       'startT':startT, 'endT':endT}

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      seed_str = source+target+startT+endT
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/co-location/' #### + tag
      print 'output_dir: ', output_dir

      ### if not os.path.exists(output_dir):
        ### os.makedirs(output_dir)
       
      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/collocation')
      # instantiate the app. class
     
      c1 = call_collocation.call_collocation(source, target, startT, endT, output_dir)

      # call the app. function
      (message, imgFileName) = c1.display()
      print 'imgFileName: ', imgFileName
      # chdir back
      os.chdir(current_dir)

      hostname, port = get_host_port("host.cfg")
      if hostname == 'EC2':
        req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
        response = urllib2.urlopen(req)
        hostname = response.read()

      print 'hostname: ', hostname
      print 'port: ', port

      imgFileName = 'collocation_plot.png'
      plotUrl = 'http://' + hostname + ':' + port + '/static/co-location/' + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      ### print 'dataUrl: ', dataUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 :
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)

    serviceId = '3'
    purpose = request.args.get('purpose')#"Test .\'\"\\purpose"
    serviceConfigurationId = "Test .\'\"\\confId"
    datasetLogId = "Test .\'\"\\logId"
    executionEndTime = int(time.time())
    post_json = {'userId':userId, 'serviceId':serviceId, 'purpose':purpose,
                 'serviceConfigurationId':serviceConfigurationId, 'datasetLogId':datasetLogId,
                 'executionStartTime':executionStartTime, 'executionEndTime':executionEndTime,
                 'parameters': parameters_json}

    req_url = BASE_URL.format(userId, serviceId, purpose,
                          serviceConfigurationId, datasetLogId,
                          executionStartTime, executionEndTime)
    print req_url

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    }) 
   


@app.route('/svc/two_time_bounds', methods=["GET"])
@crossdomain(origin='*')
def displayTwoTimeBounds():
    """Run displayTwoTimeBounds"""
    executionStartTime = int(time.time())     
    # status and message
    success = True
    message = "ok"
   
    # get data source and variable name
    serviceType = request.args.get('serviceType', '')
    source1 = request.args.get('source1', '')
    var1 = request.args.get('var1', '')
    source2 = request.args.get('source2', '')
    var2 = request.args.get('var2', '')
    parameters_json = {'serviceType':serviceType, 'source1':source1,
                       'var1':var1, 'source2':source2, 'var2':var2}

    print 'source1: ', source1
    print 'var:1 ', var1
    print 'source2: ', source2
    print 'var2: ', var2

    retDateList1 = getTimeBounds.getTimeBounds(serviceType, source1, var1)
    print 'retDateList1: ', retDateList1

    if retDateList1[0] is not 0:
      lower1 = int(str(retDateList1[0]))
    else:
      lower1 = 0

    if retDateList1[1] is not 0:
      upper1 = int(str(retDateList1[1]))
    else:
      upper1 = 0

    retDateList2 = getTimeBounds.getTimeBounds(serviceType, source2, var2)
    print 'retDateList2: ', retDateList2

    if retDateList2[0] is not 0:
      lower2 = int(str(retDateList2[0]))
    else:
      lower2 = 0

    if retDateList2[1] is not 0:
      upper2 = int(str(retDateList2[1]))
    else:
      upper2 = 0

    serviceId = "displayTwoTimeBounds"
    purpose = request.args.get('purpose')#"Test .\'\"\\purpose"
    serviceConfigurationId = "Test .\'\"\\confId"
    datasetLogId = "Test .\'\"\\logId"
    executionEndTime = int(time.time())

    return jsonify({
        'success': success,
        'message': message,
        'time_bounds1': [lower1, upper1],
        'time_bounds2': [lower2, upper2]
    }) 



@app.route('/svc/time_bounds', methods=["GET"])
@crossdomain(origin='*')
def displayTimeBounds():
    """Run displayTimeBounds"""
    executionStartTime = int(time.time())
    # status and message
    success = True
    message = "ok"
   
    # get data source and variable name
    serviceType = request.args.get('serviceType', '')
    source = request.args.get('source', '')
    var = request.args.get('var', '')

    parameters_json = {'serviceType':serviceType, 'source':source, 'var':var}

    print 'source: ', source
    print 'var: ', var

    retDateList = getTimeBounds.getTimeBounds(serviceType, source, var)
    print 'retDateList: ', retDateList

    if retDateList[0] is not 0:
      lower = int(str(retDateList[0]))
    else:
      lower = 0

    if retDateList[1] is not 0:
      upper = int(str(retDateList[1]))
    else:
      upper = 0

    serviceId = "displayTimeBounds"
    purpose = request.args.get('purpose')#"Test .\'\"\\purpose"
    serviceConfigurationId = "Test .\'\"\\confId"
    datasetLogId = "Test .\'\"\\logId"
    executionEndTime = int(time.time())
    post_json = {'userId':userId, 'serviceId':serviceId, 'purpose':purpose,
                 'serviceConfigurationId':serviceConfigurationId, 'datasetLogId':datasetLogId,
                 'executionStartTime':executionStartTime, 'executionEndTime':executionEndTime,
                 'parameters': parameters_json}

    return jsonify({
        'success': success,
        'message': message,
        'time_bounds': [lower, upper]
    }) 

#== regridAndDownload__
@app.route('/svc/regridAndDownload', methods=["GET"])
@crossdomain(origin='*')
def regridAndDownload():
    """Run regridAndDownload"""
    executionStartTime = int(time.time())  
    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    # get model, var, start time, end time, lon1, lon2, dlon, lat1, lat2, dlat, plev

    model = request.args.get('model1', '').lower()
    var = request.args.get('var1', '')
    startT = request.args.get('timeS', '')
    endT = request.args.get('timeE', '')
    lon1 = request.args.get('lonS', '')
    lon2 = request.args.get('lonE', '')
    dlon = request.args.get('dlon', '')
    lat1 = request.args.get('latS', '')
    lat2 = request.args.get('latE', '')
    dlat = request.args.get('dlat', '')
    plev = request.args.get('pres1', '')
    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    #added by CMU
    parameters_json = {'model':model, 'var':var, 'startT':startT,
                       'endT':endT, 'lon1':lon1, 'lon2':lon2, 'dlon':dlon,
                       'lat1':lat1, 'lat2':lat2, 'dlat':dlat,
                       'plev':plev}

    print 'model: ', model
    print 'var: ', var
    print 'startT: ', startT
    print 'endT: ', endT
    print 'lon1: ', lon1
    print 'lon2: ', lon2
    print 'dlon: ', dlon
    print 'lat1: ', lat1
    print 'lat2: ', lat2
    print 'dlat: ', dlat
    print 'plev: ', plev

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      seed_str = model+var+startT+endT+lon1+lon2+dlon+lat1+lat2+dlat+plev
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/regridAndDownload/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/regridAndDownload')
      # instantiate the app. class
      c1 = call_regridAndDownload.call_regridAndDownload(model, var, startT, endT, lon1, lon2, dlon, lat1, lat2, dlat, plev, output_dir)
      # call the app. function
      (message, imgFileName, dataFileName) = c1.regridAndDownload()
      print 'message:', message
      print 'imgFileName:', imgFileName
      print 'dataFileName:', dataFileName
      # chdir back
      os.chdir(current_dir)

      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
          response2 = urllib2.urlopen(req2) 
          userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
 
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      backend_url = 'http://' + hostname + ':' + port + '/svc/regridAndDownload'
      print 'backend_url: ', backend_url
      plotUrl = 'http://' + hostname + ':' + port + '/static/regridAndDownload/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/regridAndDownload/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl
      notAvailImgUrl = 'http://' + hostname + ':' + port + '/static/plot_not_available.png'
      print 'notAvailImgUrl: ', notAvailImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = notAvailImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 :
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in regridAndDownload()")
        message = str(e)

    purpose = request.args.get('purpose')
    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    
    if USE_CMU:
        try:
            print post_json
            print requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
            
        except:
            print 'Something went wrong with Wei\'s stuff'
 

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })


@app.route('/svc/regridAndDownloadPOST', methods=["POST"])
@crossdomain(origin='*')
def regridAndDownloadPOST():
    """Run regridAndDownloadPOST"""

    # status and message
    success = True
    message = "ok"
    url = ''
    dataUrl = ''

    # get model, var, start time, end time, lon1, lon2, dlon, lat1, lat2, dlat, plev

    '''
    model = request.args.get('model', '')
    var = request.args.get('var', '')
    startT = request.args.get('start_time', '')
    endT = request.args.get('end_time', '')
    lon1 = request.args.get('lon1', '')
    lon2 = request.args.get('lon2', '')
    dlon = request.args.get('dlon', '')
    lat1 = request.args.get('lat1', '')
    lat2 = request.args.get('lat2', '')
    dlat = request.args.get('dlat', '')
    plev = request.args.get('plev', '')
    '''

    jsonData = request.json

    model = jsonData['model']
    var = jsonData['var']
    startT = jsonData['start_time']
    endT = jsonData['end_time']
    lon1 = jsonData['lon1']
    lon2 = jsonData['lon2']
    dlon = jsonData['dlon']
    lat1 = jsonData['lat1']
    lat2 = jsonData['lat2']
    dlat = jsonData['dlat']
    plev = jsonData['plev']

    print 'model: ', model
    print 'var: ', var
    print 'startT: ', startT
    print 'endT: ', endT
    print 'lon1: ', lon1
    print 'lon2: ', lon2
    print 'dlon: ', dlon
    print 'lat1: ', lat1
    print 'lat2: ', lat2
    print 'dlat: ', dlat
    print 'plev: ', plev

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      seed_str = model+var+startT+endT+lon1+lon2+dlon+lat1+lat2+dlat+plev
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/regridAndDownload/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/regridAndDownload')
      # instantiate the app. class
      c1 = call_regridAndDownload.call_regridAndDownload(model, var, startT, endT, lon1, lon2, dlon, lat1, lat2, dlat, plev, output_dir)
      # call the app. function
      (message, imgFileName, dataFileName) = c1.regridAndDownload()
      # chdir back
      os.chdir(current_dir)

      hostname, port = get_host_port("host.cfg")
      if hostname == 'EC2':
        req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
        response = urllib2.urlopen(req)
        hostname = response.read()

      print 'hostname: ', hostname
      print 'port: ', port

      ### url = 'http://cmacws.jpl.nasa.gov:8090/static/twoDimMap/' + tag + '/' + imgFileName
      url = 'http://' + hostname + ':' + port + '/static/regridAndDownload/' + tag + '/' + imgFileName
      print 'url: ', url
      dataUrl = 'http://' + hostname + ':' + port + '/static/regridAndDownload/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 :
        success = False
        url = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in regridAndDownload()")
        message = str(e)

    return jsonify({
        'success': success,
        'message': message,
        'url': url,
        'dataUrl': dataUrl
    })

#== multiModelStatistics__
@app.route('/svc/multiModelStatistics', methods=["GET"])
@crossdomain(origin='*')
def multiModelStatistics():
    """Run multiModelStatistics"""
    executionStartTime = int(time.time())  
    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    # get model, var, start time, end time, lon1, lon2, dlon, lat1, lat2, dlat, plev

    sources = request.args.get('model1', '').lower()
    var = request.args.get('var1', '')
    startT = request.args.get('timeS', '')
    endT = request.args.get('timeE', '')
    lon1 = request.args.get('lonS', '')
    lon2 = request.args.get('lonE', '')
    dlon = request.args.get('dLon', '')
    lat1 = request.args.get('latS', '')
    lat2 = request.args.get('latE', '')
    dlat = request.args.get('dLat', '')
    plev = request.args.get('pres1', '')
    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    #added by CMU
    parameters_json = {'sources':sources, 'var':var, 'startT':startT,
                       'endT':endT, 'lon1':lon1, 'lon2':lon2, 'dlon':dlon,
                       'lat1':lat1, 'lat2':lat2, 'dlat':dlat,
                       'plev':plev}

    print 'sources: ', sources
    print 'var: ', var
    print 'startT: ', startT
    print 'endT: ', endT
    print 'lon1: ', lon1
    print 'lon2: ', lon2
    print 'dlon: ', dlon
    print 'lat1: ', lat1
    print 'lat2: ', lat2
    print 'dlat: ', dlat
    print 'plev: ', plev

    lonSpecStr = lon1 + ',' +  lon2 + ',' + dlon
    latSpecStr = lat1 + ',' +  lat2 + ',' + dlat
    varInfoStr = var + ' ' + sources + ' ' + plev + ' ' + lonSpecStr + ' ' + latSpecStr + ' ' +  startT + ' ' + endT

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      seed_str = sources+var+startT+endT+lon1+lon2+dlon+lat1+lat2+dlat+plev
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/multiModelStatistics/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/multiModelStatistics')
      # instantiate the app. class
      c1 = call_multiModelStatistics.call_multiModelStatistics(varInfoStr, output_dir, request.query_string)
      # call the app. function
      (message, imgFileName, dataFileName) = c1.generate_multiModelStatistics()
      print 'message:', message
      print 'imgFileName:', imgFileName
      print 'dataFileName:', dataFileName
      # chdir back
      os.chdir(current_dir)

      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
          response2 = urllib2.urlopen(req2) 
          userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
 
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      backend_url = 'http://' + hostname + ':' + port + '/svc/multiModelStatistics'
      print 'backend_url: ', backend_url
      plotUrl = 'http://' + hostname + ':' + port + '/static/multiModelStatistics/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/multiModelStatistics/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl
      notAvailImgUrl = 'http://' + hostname + ':' + port + '/static/plot_not_available.png'
      print 'notAvailImgUrl: ', notAvailImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = notAvailImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 :
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in regridAndDownload()")
        message = str(e)

    purpose = request.args.get('purpose')
    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    
    if USE_CMU:
        try:
            print post_json
            print requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
            
        except:
            print 'Something went wrong with Wei\'s stuff'
 

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

#== correlationMap_
@app.route('/svc/correlationMap', methods=["GET"])
@crossdomain(origin='*')
def displayCorrelationMap():
    """Run displayCorrelationMap"""
    executionStartTime = int(time.time())
    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    # get model1, var1, pres1, model2, var2, pres2, start time, end time, lon1, lon2, lat1, lat2

    center = []
    model = []
    var = []
    pres = []

    nVar = 2
    for i in range( nVar):
      m1 = request.args.get('model'+str(i+1), '').lower()
      temp1 = m1.split('_')
      center.append(temp1[0])
      model.append(temp1[1])
      var.append(request.args.get('var'+str(i+1), ''))
      pres.append(request.args.get('pres'+str(i+1), ''))

    laggedTime = request.args.get('laggedTime', '')
    startT = request.args.get('timeS', '')
    endT = request.args.get('timeE', '')
    lonS = request.args.get('lonS', '')
    lonE = request.args.get('lonE', '')
    latS = request.args.get('latS', '')
    latE = request.args.get('latE', '')
    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    json1 = {
       'center':center, 
       'model':model, 
       'varName':var, 
       'pres':pres,
       'yearS':startT[:4],
       'yearE':endT[:4],
       'monthS':startT[4:], 
       'monthE':endT[4:], 
       'lon1S':lonS, 
       'lon1E':lonE,
       'lat1S':latS, 
       'lat1E':latE, 
       'laggedTime':laggedTime, 
    }

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      seed_str = str(time.time())
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/correlationMap/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)
      json1['outDir'] = output_dir

      import pickle
      pFile = '%s/p.pickle'%output_dir
      fid = open(pFile,'w')
      pickle.dump(json1, fid)
      fid.close()

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/correlationMap')
      # instantiate the app. class
      c1 = call_correlationMap.call_correlationMap(pFile)
      # call the app. function (0 means the image created is scatter plot)
      ### (message, imgFileName) = c1.displayScatterPlot2V(0)
      (message, imgFileName, dataFileName) = c1.display()
      # chdir back
      os.chdir(current_dir)

      ind1 = message.find('No Data')
      if ind1>0:
        message1 = message[ind1:(ind1+200)]
        message1a = message1.split('\n')
        print message1a[0]
        print message1a[1]
     
      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
          response2 = urllib2.urlopen(req2) 
          userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
 
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port
      print 'imgFileName: ', imgFileName

      backend_url = 'http://' + hostname + ':' + port + '/svc/correlationMap'
      print 'backend_url: ', backend_url
      plotUrl = 'http://' + hostname + ':' + port + '/static/correlationMap/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/correlationMap/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 or message.find('No Data') >= 0:
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in displayScatterPlot2V()")
        message = str(e)

    purpose = request.args.get('purpose')#"Test .\'\"\\purpose"
    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    # json dictionary for provenance service request
    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print '===================================================================='
            print post_json
            requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong with Wei\'s stuff'

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

# randomForest__
@app.route('/svc/randomForest', methods=["GET"])
@crossdomain(origin='*')
def displayRandomForest():
    """Run displayRandomForest"""
    executionStartTime = int(time.time())
    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    # get model1, var1, pres1, model2, var2, pres2, start time, end time, lon1, lon2, lat1, lat2, nSample

    center = []
    model = []
    var = []
    pres = []

    nVarP = 1

    nVar = int(request.args.get('nVar', ''))
    for i in range( nVar+nVarP ):
      m1 = request.args.get('model'+str(i+1), '').lower()
      temp1 = m1.split('_')
      center.append(temp1[0])
      model.append(temp1[1])
      var.append(request.args.get('var'+str(i+1), ''))
      pres.append(request.args.get('pres'+str(i+1), ''))

    startT = request.args.get('timeS', '')
    endT = request.args.get('timeE', '')
    lonS = request.args.get('lonS', '')
    lonE = request.args.get('lonE', '')
    latS = request.args.get('latS', '')
    latE = request.args.get('latE', '')
    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    json1 = {
       'nVar':nVar, 
       'center':center, 
       'model':model, 
       'varName':var, 
       'pres':pres,
       'yearS':startT[:4],
       'yearE':endT[:4],
       'monthS':startT[4:], 
       'monthE':endT[4:], 
       'lon1S':lonS, 
       'lon1E':lonE,
       'lat1S':latS, 
       'lat1E':latE, 
    }

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      seed_str = str(time.time())
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/randomForest/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)
      json1['outDir'] = output_dir

      import pickle
      pFile = '%s/p.pickle'%output_dir
      fid = open(pFile,'w')
      pickle.dump(json1, fid)
      fid.close()

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/randomForest')
      # instantiate the app. class
      c1 = call_randomForest.call_randomForest(pFile)
      # call the app. function (0 means the image created is scatter plot)
      ### (message, imgFileName) = c1.displayScatterPlot2V(0)
      (message, imgFileName, dataFileName) = c1.display()
      # chdir back
      os.chdir(current_dir)

      ind1 = message.find('No Data')
      if ind1>0:
        message1 = message[ind1:(ind1+200)]
        message1a = message1.split('\n')
        print message1a[0]
        print message1a[1]
     
      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
          response2 = urllib2.urlopen(req2) 
          userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
 
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      purpose = request.args.get('purpose')#"Test .\'\"\\purpose"

      backend_url = 'http://' + hostname + ':' + port + '/svc/randomForest'
      print 'backend_url: ', backend_url
      print 'imgFileName: ', imgFileName
      plotUrl = 'http://' + hostname + ':' + port + '/static/randomForest/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/randomForest/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 or message.find('No Data') >= 0:
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in displayScatterPlot2V()")
        message = str(e)

    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    # json dictionary for provenance service request
    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print post_json
            requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong with Wei\'s stuff'

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

# EOF__
@app.route('/svc/EOF', methods=["GET"])
@crossdomain(origin='*')
def displayEOF():
    """Run displayEOF"""
    executionStartTime = int(time.time())
    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    # get model1, var1, pres1, model2, var2, pres2, start time, end time, lon1, lon2, lat1, lat2, nSample

    center = []
    model = []
    var = []
    pres = []

    nVar = 1
    for i in range( nVar ):
      m1 = request.args.get('model'+str(i+1), '').lower()
      temp1 = m1.split('_')
      center.append(temp1[0])
      model.append(temp1[1])
      var.append(request.args.get('var'+str(i+1), ''))
      pres.append(request.args.get('pres'+str(i+1), ''))

    startT = request.args.get('timeS', '')
    endT = request.args.get('timeE', '')
    lonS = request.args.get('lonS', '')
    lonE = request.args.get('lonE', '')
    latS = request.args.get('latS', '')
    latE = request.args.get('latE', '')
    anomaly = request.args.get('anomaly', '')
    # JJJJ
    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    json1 = {
       'center':center, 
       'model':model, 
       'varName':var, 
       'pres':pres,
       'yearS':startT[:4],
       'yearE':endT[:4],
       'monthS':startT[4:], 
       'monthE':endT[4:], 
       'lon1S':lonS, 
       'lon1E':lonE,
       'lat1S':latS, 
       'lat1E':latE, 
       'anomaly':anomaly, 
    }

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      seed_str = str(time.time())
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/EOF/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)
      json1['outDir'] = output_dir

      import pickle
      pFile = '%s/p.pickle'%output_dir
      fid = open(pFile,'w')
      pickle.dump(json1, fid)
      fid.close()

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/EOF')
      # instantiate the app. class
      c1 = call_EOF.call_EOF(pFile)
      # call the app. function (0 means the image created is scatter plot)
      ### (message, imgFileName) = c1.displayScatterPlot2V(0)
      (message, imgFileName, dataFileName) = c1.display()
      # chdir back
      os.chdir(current_dir)

      ind1 = message.find('No Data')
      if ind1>0:
        message1 = message[ind1:(ind1+200)]
        message1a = message1.split('\n')
        print message1a[0]
        print message1a[1]
     
      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
          response2 = urllib2.urlopen(req2) 
          userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
 
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 2
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      purpose = request.args.get('purpose')#"Test .\'\"\\purpose"

      backend_url = 'http://' + hostname + ':' + port + '/svc/EOF'
      print 'backend_url: ', backend_url
      print 'imgFileName: ', imgFileName
      plotUrl = 'http://' + hostname + ':' + port + '/static/EOF/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/EOF/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 or message.find('No Data') >= 0:
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in displayScatterPlot2V()")
        message = str(e)

    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    # json dictionary for provenance service request
    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print post_json
            requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong with Wei\'s stuff'

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

# conditionalPdf__
@app.route('/svc/conditionalPdf', methods=["GET"])
@crossdomain(origin='*')
def displayConditionalPdf():
    """run displayConditionalPdf """
    executionStartTime = int(time.time())
    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    center = []
    model = []
    var = []
    pres = []

    nVar = 2
    for i in range( nVar ):
      m1 = request.args.get('model'+str(i+1), '').lower()
      temp1 = m1.split('_')
      center.append(temp1[0])
      model.append(temp1[1])
      var.append(request.args.get('var'+str(i+1), ''))
      pres.append(request.args.get('pres'+str(i+1), ''))

    startT = request.args.get('timeS', '')
    endT = request.args.get('timeE', '')
    lonS = request.args.get('lonS', '')
    lonE = request.args.get('lonE', '')
    latS = request.args.get('latS', '')
    latE = request.args.get('latE', '')
    anomaly = request.args.get('anomaly', '')
    nBinX = request.args.get('nBinX', '')
    nBinY = request.args.get('nBinY', '')
    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    json1 = {
       'nVar':nVar, 
       'center':center, 
       'model':model, 
       'varName':var, 
       'pres':pres,
       'yearS':startT[:4],
       'yearE':endT[:4],
       'monthS':startT[4:], 
       'monthE':endT[4:], 
       'lon1S':lonS, 
       'lon1E':lonE,
       'lat1S':latS, 
       'lat1E':latE, 
       'anomaly':anomaly, 
       'nBinX':nBinX, 
       'nBinY':nBinY, 
    }

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      seed_str = str(time.time())
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/conditionalPdf/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)
      json1['outDir'] = output_dir

      import pickle
      pFile = '%s/p.pickle'%output_dir
      fid = open(pFile,'w')
      pickle.dump(json1, fid)
      fid.close()

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/conditionalPdf')
      # instantiate the app. class
      c1 = call_conditionalPdf.call_service(pFile)
      # call the app. function (0 means the image created is scatter plot)
      ### (message, imgFileName) = c1.displayScatterPlot2V(0)
      (message, imgFileName, dataFileName) = c1.display()
      # chdir back
      os.chdir(current_dir)

      ind1 = message.find('No Data')
      if ind1>0:
        message1 = message[ind1:(ind1+200)]
        message1a = message1.split('\n')
        print message1a[0]
        print message1a[1]
     
      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
          response2 = urllib2.urlopen(req2) 
          userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
 
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      purpose = request.args.get('purpose')#"Test .\'\"\\purpose"

      backend_url = 'http://' + hostname + ':' + port + '/svc/conditionalPdf'
      print 'backend_url: ', backend_url
      print 'imgFileName: ', imgFileName
      plotUrl = 'http://' + hostname + ':' + port + '/static/conditionalPdf/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/conditionalPdf/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 or message.find('No Data') >= 0:
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in displayScatterPlot2V()")
        message = str(e)

    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    # json dictionary for provenance service request
    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print post_json
            requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong with Wei\'s stuff'

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

#== anomaly__
@app.route('/svc/anomaly', methods=["GET"])
@crossdomain(origin='*')
def displayAnomaly():
    """Run displayAnomaly"""
    executionStartTime = int(time.time())
    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    # get model1, var1, pres1, model2, var2, pres2, start time, end time, lon1, lon2, lat1, lat2, nSample

    center = []
    model = []
    var = []
    pres = []

    print "request.query_string: ", 
    print request.query_string
    nVar = 2
    for i in range( nVar ):
      m1 = request.args.get('model'+str(i+1), '').lower()
      temp1 = m1.split('_')
      center.append(temp1[0])
      model.append(temp1[1])
      var.append(request.args.get('var'+str(i+1), ''))
      pres.append(request.args.get('pres'+str(i+1), ''))


    startT = request.args.get('timeS', '')
    endT = request.args.get('timeE', '')
    lonS = request.args.get('lonS', '')
    lonE = request.args.get('lonE', '')
    latS = request.args.get('latS', '')
    latE = request.args.get('latE', '')
    startT2 = request.args.get('timeS2', '')
    endT2 = request.args.get('timeE2', '')
    removeSeason = request.args.get('removeSeason', '')
    useVar2 = request.args.get('useVar2', '')
    useTime2 = request.args.get('useTime2', '')
    tag1 = request.args.get('tag', '')
    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url
    print 'startT2, endT2: ', startT2, endT2

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    json1 = {
       'center':center, 
       'model':model, 
       'varName':var, 
       'pres':pres,
       'yearS':startT[:4],
       'yearE':endT[:4],
       'monthS':startT[4:], 
       'monthE':endT[4:], 
       'lon1S':lonS, 
       'lon1E':lonE,
       'lat1S':latS, 
       'lat1E':latE, 
       'removeSeason':removeSeason, 
       'useVar2':useVar2, 
       'useTime2':useTime2, 
       'yearS2':startT2[:4],
       'yearE2':endT2[:4],
       'monthS2':startT2[4:], 
       'monthE2':endT2[4:], 
       'queryString':request.query_string,
    }

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      seed_str = str(time.time())
      tag = tag1
      output_dir = current_dir + '/svc/static/anomaly/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)
      json1['outDir'] = output_dir

      import pickle
      pFile = '%s/p.pickle'%output_dir
      fid = open(pFile,'w')
      pickle.dump(json1, fid)
      fid.close()

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/anomaly')
      # instantiate the app. class
      c1 = call_anomaly.call_service(pFile)
      # call the app. function (0 means the image created is scatter plot)
      ### (message, imgFileName) = c1.displayScatterPlot2V(0)
      (message, imgFileName, dataFileName) = c1.display()
      # chdir back
      os.chdir(current_dir)

      ind1 = message.find('No Data')
      if ind1>0:
        message1 = message[ind1:(ind1+200)]
        message1a = message1.split('\n')
        print message1a[0]
        print message1a[1]
     
      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
          response2 = urllib2.urlopen(req2) 
          userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
 
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      purpose = request.args.get('purpose')#"Test .\'\"\\purpose"

      print 'imgFileName: ', imgFileName

      backend_url = 'http://' + hostname + ':' + port + '/svc/anomaly'
      print 'backend_url: ', backend_url
      plotUrl = 'http://' + hostname + ':' + port + '/static/anomaly/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/anomaly/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 or message.find('No Data') >= 0:
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in displayScatterPlot2V()")
        message = str(e)

    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    # json dictionary for provenance service request
    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print 'post_json: '
            print post_json
            print 'CMU_PROVENANCE_URL: '
            print CMU_PROVENANCE_URL
            requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong with Wei\'s stuff'

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

#== mapPlot__
@app.route('/svc/mapPlot', methods=["GET"])
@crossdomain(origin='*')
def displayMapPlot():
    """Run displayMapPlot"""
    executionStartTime = int(time.time())
    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    # get model1, var1, pres1, model2, var2, pres2, start time, end time, lon1, lon2, lat1, lat2, nSample

    center = []
    model = []
    var = []
    pres = []

    print "request.query_string: ", 
    print request.query_string

    useVmin1 = request.args.get('useVmin1', '')
    vmin1 = request.args.get('vmin1', '')
    vmax1 = request.args.get('vmax1', '')
    vint1 = request.args.get('vint1', '')
    useFerretLevel = request.args.get('useFerretLevel', '')
    ferretLevel = request.args.get('ferretLevel', '')
    inputDataFile = request.args.get('inputDataFile', '')
    colorMap = request.args.get('colorMap', '')
    plotTitle = request.args.get('plotTitle', '')
    data_url1 = inputDataFile

    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    json1 = {
       'useVmin1':useVmin1, 
       'vmin1':vmin1, 
       'vmax1':vmax1, 
       'vint1':vint1, 
       'useFerretLevel':useFerretLevel, 
       'ferretLevel':ferretLevel, 
       'inputDataFile':inputDataFile, 
       'colorMap':colorMap, 
       'plotTitle':plotTitle, 
       #'queryString':request.query_string,
    }

    tag = None
    if len(data_url1)>10:
      if data_url1[-1]=='c':
        fn1 = os.path.dirname(data_url1)
        tag = os.path.basename(fn1)

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      if tag is None:
        seed_str = str(time.time())
        tag = md5.new(seed_str).hexdigest()

      output_dir = current_dir + '/svc/static/mapPlot/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)
      json1['outDir'] = output_dir

      import pickle
      pFile = '%s/p.pickle'%output_dir
      fid = open(pFile,'w')
      pickle.dump(json1, fid)
      fid.close()

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/mapPlot')
      # instantiate the app. class
      c1 = call_mapPlot.call_service(pFile)
      # call the app. function (0 means the image created is scatter plot)
      ### (message, imgFileName) = c1.displayScatterPlot2V(0)
      (message, imgFileName, dataFileName) = c1.display()
      # chdir back
      os.chdir(current_dir)

      ind1 = message.find('No Data')
      if ind1>0:
        message1 = message[ind1:(ind1+200)]
        message1a = message1.split('\n')
        print message1a[0]
        print message1a[1]
     
      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
          response2 = urllib2.urlopen(req2) 
          userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
 
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      purpose = request.args.get('purpose')#"Test .\'\"\\purpose"
      print 'imgFileName: ', imgFileName

      backend_url = 'http://' + hostname + ':' + port + '/svc/mapPlot'
      print 'backend_url: ', backend_url
      plotUrl = 'http://' + hostname + ':' + port + '/static/mapPlot/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/mapPlot/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 or message.find('No Data') >= 0:
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in displayScatterPlot2V()")
        message = str(e)

    executionEndTime = int(time.time())

    urlLink = request.query_string
    print 'urlLink: ', urlLink

    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print post_json
            requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong with Wei\'s stuff'

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

#== map2d__
@app.route('/svc/map2d', methods=["GET"])
@crossdomain(origin='*')
def displayMap2d():
    """Run displayMap2d"""
    executionStartTime = int(time.time())
    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    # get model1, var1, pres1, model2, var2, pres2, start time, end time, lon1, lon2, lat1, lat2, nSample

    center = []
    model = []
    var = []
    pres = []

    print "request.query_string: ", 
    print request.query_string
    nVar = 1
    for i in range( nVar ):
      m1 = request.args.get('model'+str(i+1), '').lower()
      temp1 = m1.split('_')
      center.append(temp1[0])
      model.append(temp1[1])
      var.append(request.args.get('var'+str(i+1), ''))
      pres.append(request.args.get('pres'+str(i+1), ''))

    startT = request.args.get('timeS', '')
    endT = request.args.get('timeE', '')
    lonS = request.args.get('lonS', '')
    lonE = request.args.get('lonE', '')
    latS = request.args.get('latS', '')
    latE = request.args.get('latE', '')
    #useVmin1 = request.args.get('useVmin1', '')
    #vmin1 = request.args.get('vmin1', '')
    #vmax1 = request.args.get('vmax1', '')
    #data_url1 = request.args.get('data_url', '')

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    json1 = {
       'center':center, 
       'model':model, 
       'varName':var, 
       'pres':pres,
       'yearS':startT[:4],
       'yearE':endT[:4],
       'monthS':startT[4:], 
       'monthE':endT[4:], 
       'lon1S':lonS, 
       'lon1E':lonE,
       'lat1S':latS, 
       'lat1E':latE, 
       #'useVmin1':useVmin1, 
       #'vmin1':vmin1, 
       #'vmax1':vmax1, 
       #'data_url':data_url1, 
       'queryString':request.query_string,
    }

    tag = None
    #if len(data_url1)>10:
    #  if data_url1[-1]=='c':
    #    fn1 = os.path.dirname(data_url1)
    #    tag = os.path.basename(fn1)

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    try:
      if tag is None:
        seed_str = str(time.time())
        tag = md5.new(seed_str).hexdigest()

      output_dir = current_dir + '/svc/static/map2d/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)
      json1['outDir'] = output_dir

      import pickle
      pFile = '%s/p.pickle'%output_dir
      fid = open(pFile,'w')
      pickle.dump(json1, fid)
      fid.close()

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/map2d')
      # instantiate the app. class
      c1 = call_map2d.call_service(pFile)
      # call the app. function (0 means the image created is scatter plot)
      ### (message, imgFileName) = c1.displayScatterPlot2V(0)
      (message, imgFileName, dataFileName) = c1.display()
      # chdir back
      os.chdir(current_dir)

      ind1 = message.find('No Data')
      if ind1>0:
        message1 = message[ind1:(ind1+200)]
        message1a = message1.split('\n')
        print message1a[0]
        print message1a[1]
     
      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
          req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
          response2 = urllib2.urlopen(req2) 
          userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
 
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      purpose = request.args.get('purpose')#"Test .\'\"\\purpose"

      print 'imgFileName: ', imgFileName
      plotUrl = 'http://' + hostname + ':' + port + '/static/map2d/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/map2d/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 or message.find('No Data') >= 0:
        success = False
        plotUrl = ''
        dataUrl = ''

    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        ### message = str("Error caught in displayScatterPlot2V()")
        message = str(e)

    executionEndTime = int(time.time())

    urlLink = request.query_string
    print 'urlLink: ', urlLink

    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print post_json
            requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
        except:
            print 'Something went wrong with Wei\'s stuff'

    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

#== JointEOF__
@app.route('/svc/JointEOF', methods=["GET"])
@crossdomain(origin='*')
def displayJointEOF():
    """Run displayJointEOF"""
    serviceObj = call_JointEOF.call_JointEOF(request.args.to_dict())
    return generalServiceResp(serviceObj)

#== zonalMean__
@app.route('/svc/zonalMean', methods=["GET"])
@crossdomain(origin='*')
def displayZonalMean():
    """Run displayZonalMean"""
    executionStartTime = int(time.time())

    # status and message
    success = True
    message = "ok"
    plotUrl = ''
    dataUrl = ''

    print "request.query_string: ", 
    print request.query_string

    # get where the input file and output file are
    current_dir = os.getcwd()
    print 'current_dir: ', current_dir

    # the first argument is for direct input data files from a work flow or user upload
    parameters_json = {}
    fileKey = 'inputDataFile'
    parameters_json[fileKey] = request.args.get(fileKey, '')
    if parameters_json[fileKey] == '' :
      varInfoStr = '/ '

      nVar = int(request.args.get('nVar'))

      # get model, var, pressure leve, start time, end time, lon1, lon2, lat1, lat2, month index within a year, scale
      keywords = ['model', 'var', 'pres', 'lon1_', 'lon2_', 'lat1_', 'lat2_', 'start_time_', 'end_time_', 'month_']
      sep_dict = {'model': ' ', 'var': ' ', 'pres':' ', 'lon1_':',', 'lon2_':' ', 'lat1_':',', 'lat2_': ' ', 'start_time_': ' ', 'end_time_' : ' ', 'month_' : ' '}
      keyMap = {'model': 'model', 'var': 'var', 'pres':'pres', 'lon1_':'vlonS', 'lon2_':'vlonE', 'lat1_':'vlatS', 'lat2_': 'vlatE', 'start_time_': 'vtimeS', 'end_time_' : 'vtimeE', 'month_' : 'vmonths'}
      parameters_json = {}
      for varI in range(1, nVar+2):
        for kk in keywords:
          thisKey = kk +str(varI)
          webKey = keyMap[kk] +str(varI)
          if request.args.has_key(webKey):
            parameters_json[thisKey] = request.args.get(webKey, '')
          else:
            genKey = keyMap[kk][1:]
            print 'varI, genKey: ', 
            print varI, genKey
            parameters_json[thisKey] = request.args.get(genKey, '')
          varInfoStr += parameters_json[thisKey] + sep_dict[kk]
    else:
      varInfoStr = parameters_json[fileKey]

    scale = request.args.get('scale', '')
    parameters_json['scale'] = scale;
    print '== varInfoStr: ',
    print varInfoStr

    frontend_url = request.args.get('fromPage', '')
    print 'frontend_url: ', frontend_url

    userId = request.args.get('userid', '')
    print 'from url, userId: ', userId

    if userId != None and userId != '':
      userId = int(userId)
    else:
      userId = 0

    try:
      seed_str = varInfoStr+scale
      tag = md5.new(seed_str).hexdigest()
      output_dir = current_dir + '/svc/static/zonalMean/' + tag
      print 'output_dir: ', output_dir
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)

      if parameters_json[fileKey] != '' :
        url_list = parameters_json[fileKey].split(',')
        varInfoStr = ''
        vIdx = 0
        for thisURL in url_list:
          if len(thisURL) == 0:
            continue
          if thisURL[0] == '/':
            thisLocalFile = thisURL
          else :
            vIdx += 1
            file_basename = os.path.basename(thisURL)
            thisLocalFile = output_dir + '/v' + str(vIdx) + '_' + file_basename
            print 'thisURL=', thisURL
            download_file_from_url.download_file_from_url(thisURL, thisLocalFile)
          if varInfoStr != '' :
            thisLocalFile = ',' + thisLocalFile
          varInfoStr = varInfoStr + thisLocalFile 

      # chdir to where the app is
      os.chdir(current_dir+'/svc/src/zonalMean')
      # instantiate the app. class
      c1 = call_zonalMean.call_zonalMean(varInfoStr, output_dir, scale)
      # call the app. function
      (message, imgFileName, dataFileName) = c1.display_zonalMean()
      # chdir back
      os.chdir(current_dir)
      hostname, port = get_host_port("host.cfg")
      ### userId = 2
      if hostname == 'EC2':
        try:
          req = urllib2.Request('http://169.254.169.254/latest/meta-data/public-ipv4')
          response = urllib2.urlopen(req)
          hostname = response.read()
        except Exception, e:
          print 'e: ', e

        """
        try:
           req2 = urllib2.Request(' http://169.254.169.254/latest/user-data') 
           response2 = urllib2.urlopen(req2) 
           userId = json.loads(response2.read())['username'] 
        except Exception, e:
          print 'e: ', e
          userId = 2
        """
 
      """
      if userIdDict.has_key(userId):
        userId = userIdDict[userId]
      else :
        userId = 'lei'
      """

      print 'userId: ', userId
      print 'hostname: ', hostname
      print 'port: ', port

      backend_url = 'http://' + hostname + ':' + port + '/svc/zonalMean'
      print 'backend_url: ', backend_url
      plotUrl = 'http://' + hostname + ':' + port + '/static/zonalMean/' + tag + '/' + imgFileName
      print 'plotUrl: ', plotUrl
      dataUrl = 'http://' + hostname + ':' + port + '/static/zonalMean/' + tag + '/' + dataFileName
      print 'dataUrl: ', dataUrl
      failedImgUrl = 'http://' + hostname + ':' + port + '/static/plottingFailed.png'
      print 'failedImgUrl: ', failedImgUrl

      if imgFileName is '' or not os.path.exists(output_dir+'/'+imgFileName):
        print '****** Error: %s not exist' % imgFileName
        plotUrl = failedImgUrl

      if dataFileName is '' or not os.path.exists(output_dir+'/'+dataFileName):
        print '****** Error: %s not exist' % dataFileName
        dataUrl = failedImgUrl

      print 'message: ', message
      if len(message) == 0 or message.find('Error') >= 0 or message.find('error:') >= 0 :
        success = False
        plotUrl = ''
        dataUrl = ''


    except ValueError, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)
    except Exception, e:
        # chdir to current_dir in case the dir is changed to where the app is in the try block
        os.chdir(current_dir)
        print 'change dir back to: ', current_dir

        success = False
        message = str(e)

    purpose = request.args.get('purpose')#"Test .\'\"\\purpose"
#    serviceConfigurationId = "Test .\'\"\\confId"
#    datasetLogId = "Test .\'\"\\logId"
    executionEndTime = int(time.time())

    urlLink = request.query_string
    urlLink = urlLink.strip() + '&image=%s&data_url=%s' % (plotUrl, dataUrl)
    print 'urlLink: ', urlLink
    urlLink = urlLink.replace('&fromPage='+frontend_url, '')
    print 'urlLink: ', urlLink

    post_json = {'source': 'JPL', 'parameters':urlLink, 'frontend_url': frontend_url, 'backend_url': backend_url, 'userId': long(userId),
                     'executionStartTime':long(executionStartTime)*1000, 'executionEndTime':long(executionEndTime)*1000}

    post_json = json.dumps(post_json)
    if USE_CMU:
        try:
            print post_json
            print 'submitting provenance from zonalMean ...'
            print requests.post(CMU_PROVENANCE_URL, data=post_json, headers=HEADERS).text
            ### print requests.post(VIRTUAL_EINSTEIN_URL, data=post_json, headers=HEADERS).text
            print 'submitted provenance'
        except:
            print 'Something went wrong with Wei\'s stuff'


    return jsonify({
        'success': success,
        'message': message,
        'url': plotUrl,
        'dataUrl': dataUrl
    })

#== testAxios__
@app.route('/svc/testAxios', methods=["GET"])
@crossdomain(origin='*')
def testAxios():
    print 'zzzz in testAxios'
    # status and message
    success = True
    message = "start... "

    #para1 = str(request.args.get('aa', ''))
    para1 = request.args.get('aa', '')
    print 'para1: ',
    print para1
    #print str(para1)

    #message = message + para1
    message += para1 

    dict1 = {
      'success': success,
      'message': message,
    }
      
    return jsonify(dict1)
