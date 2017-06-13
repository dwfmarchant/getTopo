"""
Tools for interpolating topography data
"""
import numpy as np
from scipy.interpolate import griddata


def interp2pts(xTopo, yTopo, zTopo, x, y):
    """
    Interpolate to points
    Usage:
        zInterp = interp2pts(xTopo, yTopo, zTopo, x, y)
    """
    xTopo = xTopo.flatten()
    yTopo = yTopo.flatten()
    zTopo = zTopo.flatten()

    ind = (xTopo > (x.min()-100.)) & (xTopo < (x.max()+100.)) &\
          (yTopo > (y.min()-100.)) & (yTopo < (y.max()+100.))

    xTopo = xTopo[ind]
    yTopo = yTopo[ind]
    zTopo = zTopo[ind]

    zInterp = griddata(np.c_[xTopo, yTopo], zTopo, np.c_[x, y])
    return zInterp
