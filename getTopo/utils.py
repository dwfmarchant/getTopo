
import json
from os.path import expanduser

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

