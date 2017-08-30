# getTopo
Python tool for downloading SRTM topography data

Using getTopo requires a NASA Earthdata Login username and password.  Visit [here](https://urs.earthdata.nasa.gov/users/new) to get one.

## Setup instructions

You need to setup a .gettoporc file prior to using.  This file should have the following format:
```json
{
  "username":"yourusername",
  "password":"yourpassword",
  "download_location":"~/Documents/SRTM/"
}
```
and it needs to be placed in your home directory, ie, the output of:
  
  ```python
  from os.path import expanduser
  print(expanduser("~")
  ```
