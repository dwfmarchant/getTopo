
import json
from os.path import expanduser
from http.cookiejar import CookieJar
import io
import zipfile
import urllib
import sys
import numpy as np
import pyproj

URL = 'http://e4ftl01.cr.usgs.gov/SRTM/SRTMGL1.003/2000.02.11/'

def getCredentials():
    creds = json.load(open(expanduser('~/.gettoporc'), 'r'))
    return creds

def getFname(lat, lon):
    
    if lat < 0: 
        fname = 'S'
    else: 
        fname = 'N'
    
    fname += '{:02d}'.format(abs(int(lat)))
    
    if lon < 0: 
        fname += 'W'
    else: 
        fname += 'E'

    fname += '{:03d}'.format(abs(int(lon)))
    
    fname += '.SRTMGL1.hgt.zip'
    return fname

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

def downloadSRTM_LL(lat_min, lat_max, lon_min, lon_max):

    lons = np.r_[int(np.floor(lon_min)):int(np.floor(lon_max)+1)]
    lats = np.r_[int(np.floor(lat_min)):int(np.floor(lat_max).max()+1)]
    tiles_lon, tiles_lat = np.meshgrid(lons, lats)

    hgt_dict = {}
    print('Need {} tiles...'.format(tiles_lon.size))
    sys.stdout.flush()
    for lon, lat in zip(tiles_lon.flat, tiles_lat.flat):
        hgt_dict[(lon, lat)] = downloadSRTMtile(lat, lon)

    hgt = np.ndarray((0, lons.size*3600+1))
    for ilat in lats:
        hgt_r = np.ndarray((3600+1, 0))
        for ilon in lons:
            hgt_r = np.hstack([hgt_r, hgt_dict[(ilon, ilat)][:, :-1]])
        hgt_r = np.hstack([hgt_r, hgt_dict[(lons[-1], ilat)][np.newaxis, -1].T])
        hgt = np.vstack([hgt, hgt_r[:-1, :]])
    hgt = np.vstack([hgt, hgt_r[-1, :]])

    x_ll = np.linspace(lons.min(), lons.max()+1, lons.size*3600 + 1)
    y_ll = np.linspace(lats.min(), lats.max()+1, lats.size*3600 + 1)

    lon_ind0 = np.where(x_ll >= lon_min)[0][0]
    lon_ind1 = np.where(x_ll <= lon_max)[0][-1]
    lat_ind0 = np.where(y_ll >= lat_min)[0][0]
    lat_ind1 = np.where(y_ll <= lat_max)[0][-1]

    y_ll_trim = y_ll[lat_ind0:lat_ind1+1]
    x_ll_trim = x_ll[lon_ind0:lon_ind1+1]
    hgt_trim = hgt[lat_ind0:lat_ind1+1, lon_ind0:lon_ind1+1]

    return x_ll_trim, y_ll_trim, hgt_trim

def downloadSRTM_UTM(xmin, xmax, ymin, ymax, utm_zone, utm_datum='WGS84', south=False):

    proj_latlong = pyproj.Proj(proj='latlong', datum='WGS84')
    proj_utm = pyproj.Proj(proj="utm", zone=utm_zone, datum=utm_datum, south=south)

    utm_box = np.c_[[xmin, xmin, xmax, xmax, xmin],
                    [ymin, ymax, ymax, ymin, ymin]]

    box_lon, box_lat = pyproj.transform(proj_utm, proj_latlong, utm_box[:, 0], utm_box[:, 1])

    lon_min = np.min(box_lon)
    lon_max = np.max(box_lon)
    lat_min = np.min(box_lat)
    lat_max = np.max(box_lat)

    x_ll, y_ll, hgt = downloadSRTM_LL(lat_min, lat_max, lon_min, lon_max)
    x_ll, y_ll = np.meshgrid(x_ll, y_ll)

    x_utm, y_utm = pyproj.transform(proj_latlong, proj_utm, x_ll, y_ll)

    return x_utm, y_utm, hgt

