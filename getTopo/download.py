
import urllib
from http.cookiejar import CookieJar
import io
import zipfile
import numpy as np

from .utils import getFname, getCredentials

URL = 'http://e4ftl01.cr.usgs.gov/SRTM/SRTMGL1.003/2000.02.11/'

def downloadSRTMtile(lat, lon):

    fname = getFname(lat, lon)
    auth = getCredentials()

    password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, 
                                  "https://urs.earthdata.nasa.gov", 
                                  auth['username'], 
                                  auth['password'])
    cookie_jar = CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPBasicAuthHandler(password_manager),
        urllib.request.HTTPCookieProcessor(cookie_jar))
    urllib.request.install_opener(opener)

    print('\tDownloading {}....'.format(fname), end="", flush=True)
    request = urllib.request.Request(URL+fname)
    response = urllib.request.urlopen(request)    

    body = response.read()

    zip_file = zipfile.ZipFile(io.BytesIO(body))

    zip_file_name = zip_file.namelist()[0]
    hgt_string = zip_file.read(zip_file_name)
    zip_file.close()

    srtm = np.fromstring(string=hgt_string, dtype='int16').byteswap()
    srtm.shape = (3601, 3601)
    srtm = np.flipud(srtm)
    print('Done', flush=True)

    return srtm
