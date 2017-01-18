#imports
import os
import logging
logging.basicConfig(level=logging.INFO)

# set chianti env variable...should be done already?!
os.environ['XUVTOP'] = '/usr/local/ssw/packages/chianti/dbase'

import astropy.units as u
import numpy as np
import sunpy.map
import astropy.units as u
from ChiantiPy.tools import util as ch_tools_util

import synthesizAR
from synthesizAR.atomic import EquilibriumEmissionModel,ChIon
from synthesizAR.model_ext import EbtelInterface,PowerLawScaledWaitingTimes
from synthesizAR.instruments import InstrumentHinodeEIS,InstrumentSDOAIA

# root directory for everything
ar_root = '/data/datadrive2/ar_viz/synthesizar_v01demo/'

# reload objects
field = synthesizAR.Skeleton.restore(os.path.join(ar_root,'checkpoint'))
emiss_model = EquilibriumEmissionModel.restore(os.path.join(ar_root,'checkpoint_emiss_model'))

# make instruments
aia = InstrumentSDOAIA([0,9900]*u.s,
                       response_function_file='/home/wtb2/Documents/research_notebook/FieldLineViz/aia_tresponse_raw.dat')
eis = InstrumentHinodeEIS('/home/wtb2/Documents/Forward_Model/instruments/Hinode_EIS/',[0,9900]*u.s)
# remove unneeded channels
new_channels = []
for channel in eis.channels:
    for wvl in emiss_model.wavelengths:
        if channel['response']['x'][0] <= wvl <= channel['response']['x'][-1]:
            new_channels.append(channel)
            break
eis.channels = new_channels

# make observer object
observer = synthesizAR.Observer(field,[aia,eis],ds=field._convert_angle_to_length(0.3*u.arcsec))
observer.build_detector_files(ar_root)
# calculate counts
observer.calculate_detector_counts()
# bin counts
observer.bin_detector_counts(ar_root,apply_psf=[True,False])
