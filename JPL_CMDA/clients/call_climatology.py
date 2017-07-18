import httplib2, urllib
import urllib2
try:
    import simplejson as json
except Exception, e:
    import json
from urllib import urlencode
from urllib2 import HTTPError

model = 'ukmo'
data = '/static/ts_Amon_HadGEM2-A_amip_r1i1p1_197809-200811.nc'
image = '/static/ukmo_ts.jpeg'
parameters = {'model':model, 'data': data, 'image': image}
urlparams = urlencode(parameters)
print 'urlparams: ', urlparams
url = 'http://oscar2.jpl.nasa.gov:8088/' + 'twoDimClimatology/display?' + urlparams
print 'url: ', url
headers = {"Content-type": "multipart/form-data"}
try:
  http = httplib2.Http('.cache')
  (response, content) = http.request(url, 'GET', '', headers)
  ### print type(content)
  ### print 'len: ', len(content)
  ### print 'content: ', content

  obj = json.loads(content)
  print 'returned content: ', obj

  url = obj['url']
  print 'url: ', url

  # download the resulting image
  request = urllib2.Request(url=url)
  response = urllib2.urlopen(request).read()
  imageFile = url.split('/')[-1]
  print 'imageFile: ', imageFile
  f = open(imageFile, 'w')
  f.write(response)
  f.close()

except httplib2.HttpLib2Error, e:
  # the Base Exception for all exceptions raised by httplib2.
  msg = 'Unable to call "%s" due to %s: %s' % (url, type(e), str(e))
  print msg
except Exception, e:
  # any other exceptions
  msg = 'Unable to call "%s" due to %s: %s' % (url, type(e), str(e))
  print msg
# end try-except
