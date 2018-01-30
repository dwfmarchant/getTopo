
import os
import urllib
from http.cookiejar import CookieJar
import io
from zipfile import ZipFile
import numpy as np

from .utils import getHgtZipFname, getOptions

URL = 'https://e4ftl01.cr.usgs.gov/MEASURES/SRTMGL1.003/2000.02.11/'

def downloadSRTMtile(fname):

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

    request = urllib.request.Request(URL+fname)
    response = urllib.request.urlopen(request)
    dat = response.read()

    if 'download_location' in opts.keys():
        out_fname = os.path.join(opts['download_location'], fname)
        out_fname = os.path.expanduser(out_fname)
        with open(out_fname, 'wb') as hgtzip_file:
            hgtzip_file.write(dat)
    print('Done', flush=True)

    return dat

def getSRTM(lat, lon):

    fname = getHgtZipFname(lat, lon)
    opts = getOptions()

    download = False
    if 'download_location' in opts.keys():
        # Check if file is already downloaded
        dl_fname = os.path.join(opts['download_location'], fname)
        dl_fname = os.path.expanduser(dl_fname)
        if os.path.exists(dl_fname):
            print('\tReading {}....'.format(fname), end="", flush=True)
            with open(dl_fname, 'rb') as hgtzip_file:
                dat = hgtzip_file.read()
        else:
            download = True
    else:
        download = True

    if download:
        print('\tDownloading {}....'.format(fname), end="", flush=True)
        dat = downloadSRTMtile(fname)

    srtm = parseHgtZip(dat)
    print('Done', flush=True)
    return srtm

def parseHgtZip(dat):

    zip_file = ZipFile(io.BytesIO(dat), 'r')

    zip_file_name = zip_file.namelist()[0]
    hgt_string = zip_file.read(zip_file_name)
    zip_file.close()

    srtm = np.fromstring(string=hgt_string, dtype='int16').byteswap()
    srtm.shape = (3601, 3601)
    srtm = np.flipud(srtm)

    return srtm
