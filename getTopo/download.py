
import os
import urllib
from http.cookiejar import CookieJar
import io
import zipfile
import numpy as np

from .utils import getFname, getOptions

URL = 'http://e4ftl01.cr.usgs.gov/SRTM/SRTMGL1.003/2000.02.11/'

def downloadSRTMtile(lat, lon):

    fname = getFname(lat, lon)
    opts = getOptions()

    password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, 
                                  "https://urs.earthdata.nasa.gov", 
                                  opts['username'], 
                                  opts['password'])
    cookie_jar = CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPBasicAuthHandler(password_manager),
        urllib.request.HTTPCookieProcessor(cookie_jar))
    urllib.request.install_opener(opener)

    print('\tDownloading {}....'.format(fname), end="", flush=True)
    request = urllib.request.Request(URL+fname)
    response = urllib.request.urlopen(request)    
    dat = response.read()

    if 'download_location' in opts.keys():
        out_fname = os.path.join(opts['download_location'], fname)
        with open(out_fname, 'wb') as hgtzip_file:
            hgtzip_file.write(dat)
    print('Done', flush=True)        

    return dat

def readHgtZip(body):

    zip_file = zipfile.ZipFile(io.BytesIO(body), 'r')

    zip_file_name = zip_file.namelist()[0]
    hgt_string = zip_file.read(zip_file_name)
    zip_file.close()

    srtm = np.fromstring(string=hgt_string, dtype='int16').byteswap()
    srtm.shape = (3601, 3601)
    srtm = np.flipud(srtm)

    return srtm

