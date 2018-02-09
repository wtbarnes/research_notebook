"""
Convert flux transport code .sav file to SunPy map
"""
import datetime

import numpy as np
import scipy.io
import scipy.interpolate
import matplotlib.pyplot as plt
import astropy.units as u
import sunpy.map
import sunpy.sun.constants
import sunpy.cm
import sunpy


def sav_to_synoptic_map(filename, res_lon=0.1, res_lat=0.1):
    """
    Convert Alison's sav file format to a synoptic map
    """
    # Read in data
    tmp = scipy.io.readsav(filename)
    # Convert coordinates to lat/lon in degrees
    lon_data = np.array(tmp['phis'],dtype=np.float64)*180/np.pi
    lat_data = (np.array(tmp['thetas'],dtype=np.float64) - np.pi/2.)*180/np.pi
    flux_data = np.array(tmp['fluxs'],dtype=np.float64)
    # Create grid
    lon,lat = np.arange(0, 360, res_lon), np.arange(-90, 90, res_lat)
    lon_grid,lat_grid = np.meshgrid(lon,lat)
    # Interpolate to grid
    flux_grid = scipy.interpolate.griddata(np.stack([lon_data, lat_data],axis=1),
                                           flux_data, (lon_grid,lat_grid),
                                           method='cubic', fill_value=0.)
    # Build header
    header = sunpy.util.metadata.MetaDict({
        'crpix1': lon.shape[0]/2,
        'crpix2': lat.shape[0]/2,
        'crval1': (lon[-1]-lon[0])/2 + lon[0],
        'crval2': (lat[-1]-lat[0])/2 + lat[0],
        'cdelt1': np.diff(lon)[0],
        'cdelt2': np.diff(lat)[0],
        'cunit1': 'degree',
        'cunit2': 'degree',
        'wcsname': 'Carrington Heliographic',
        'content': 'Carrington synoptic chart of simulated flux transport'
    })
    lim = max(flux_grid.max(),np.fabs(flux_grid.min()))
    
    return sunpy.map.Map(flux_grid, header, plot_settings={'cmap':'hmimag','norm':plt.Normalize(vmin=-lim,vmax=lim)})


def sav_to_hpc_map(sav_filename, distance=None, sav_key='magimage', sav_placeholder=1e4, pad=None):
    """
    Convert Alison's sav file format to a SunPy map
    """
    data = scipy.io.readsav(sav_filename)[sav_key].astype(np.float64)
    data = np.where(data==sav_placeholder, np.nan,data)
    n2,n1 = data.shape
    if pad is not None:
        data = np.pad(data, pad, 'constant', constant_values=np.nan)
    if distance is None:
        distance = sunpy.sun.constants.au
    scale_1 = 2.*sunpy.sun.constants.radius/distance*(180/np.pi*3600*u.arcsec)/(n1*u.pixel)
    scale_2 = 2.*sunpy.sun.constants.radius/distance*(180/np.pi*3600*u.arcsec)/(n2*u.pixel)
    map_meta = sunpy.util.metadata.MetaDict({
        'bunit':'Gauss',
        'ctype1':'HPLN-TAN',
        'ctype2':'HPLT-TAN',
        'wcsname':'Helioprojective-cartesian',
        'crlt_obs':0.,
        'date-obs':datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        'cdelt1':scale_1.value,
        'cdelt2':scale_2.value,
        'crval1':0,
        'crval2':0,
        'crpix1':data.shape[1]/2,
        'crpix2':data.shape[0]/2,
        'cunit1':'arcsec',
        'cunit2':'arcsec',
        'dsun_obs':distance.value,
        'dsun_ref':distance.value,
        'rsun_ref':sunpy.sun.constants.radius.value,
        'rsun_obs':sunpy.sun.constants.radius.value/distance.value*(180/np.pi*3600)
    })
    plot_settings = {'cmap':'hmimag', 'vmin':-5000, 'vmax':5000}
    return sunpy.map.GenericMap(data, map_meta, plot_settings=plot_settings)

