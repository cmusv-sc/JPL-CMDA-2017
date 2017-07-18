import requests
import os
import shutil

def download_file_from_url(url, target_file):
    global dump
    file = requests.get(url, stream=True)
    dump = file.raw

    with open(target_file, 'wb') as f:
      shutil.copyfileobj(dump, f)
    del dump

if __name__ == "__main__":
  url = 'http://cmda-dev.jpl.nasa.gov:8090/static/anomaly/310541cee13d0b93d6104d5c974bc962/data_anomaly.nc'
  download_file_from_url(url, '/tmp/test.nc')

