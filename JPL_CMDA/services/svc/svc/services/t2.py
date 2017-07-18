import urllib2

def get_status_code(url):
  ### print 'url: ', url
  try:
    ret = urllib2.urlopen(url)
    ### print 'ret.code: ', ret.code
    return ret.code
  except urllib2.HTTPError:
    return None


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


if __name__ == "__main__":
  ### url1 = 'http://52.53.198.227:8090/static/plottingFailed.png3'
  ### url1 = 'http://52.53.198.227:8090/static/plottingFailed.png'
  url1 = 'http://52.53.198.227:8090/static/twoDimMap/afb814df83df17a82dccb02f8b7288ce/gfdl_esm2g_pr_200401_200412_Annual.jpeg'
  url2 = 'http://52.53.198.227:8090/static/twoDimMap/afb814df83df17a82dccb02f8b7288ce/gfdl_esm2g_pr_200401_200412_Annual.nc'

  ### plotUrl:  http://52.53.198.227:8090/static/twoDimMap/afb814df83df17a82dccb02f8b7288ce/gfdl_esm2g_pr_200401_200412_Annual.jpeg
  ### dataUrl:  http://52.53.198.227:8090/static/twoDimMap/afb814df83df17a82dccb02f8b7288ce/gfdl_esm2g_pr_200401_200412_Annual.nc

  print url_is_alive(url1)
  print url_is_alive(url2)

  """
  code1 = get_status_code(url1)
  print 'code1: ', code1
  if code1 == 200:
    print "%s exists!" % url1
  else:
    print "%s does not exist!" % url1
  """
