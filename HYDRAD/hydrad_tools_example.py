"""
Example script for using hydrad_tools
"""
# Need this module because all physical quantities require units!
import astropy.units as u
from hydrad_tools.configure import Configure

# Load the default configuration
# Note that you could create this whole configuration yourself in Python just by creating a dictionary
config = Configure.load_config('/Users/willbarnes/Documents/work/codes/hydrad_tools/defaults.asdf')
# Run for 5000 s
config['general']['total_time'] = 5e3*u.s
config['initial_conditions']['heating_location'] = 50*u.Mm
config['initial_conditions']['heating_scale_height'] = 1e300*u.cm
# Configure a nanoflare heating profile
# Note that 'events' is a list so I could add as many events here as I want
config['heating']['events'] = [
    {
        'time_start': 0*u.s, 'rise_duration': 100*u.s, 'decay_duration': 100*u.s,'total_duration': 200*u.s,
        'location': 50*u.Mm, 'scale_height': 1e300*u.cm, 'rate': 0.1*u.erg/u.s/(u.cm**3)
    }
]

# Iterate over loop length
loop_lengths = [40,80,150]*u.Mm
for L in loop_lengths:
    # I don't strictly need to create a copy here, but it is safer to do so in Python
    tmp = config.copy()
    # Set the loop length
    tmp['general']['loop_length'] = L
    # Create object
    c = Configure(tmp)
    # This command creates a new directory tree, prints all needed config files, compiles and runs the initial conditions, and compiles HYDRAD
    # ~/Desktop is the directory where I want all my HYDRAD directories to go
    # hydrad_test_L{} is the name of my new directory; the {} gets replaced with the length value
    # base_path is the path to the clean copy of HYDRAD; this is ideally a fresh clone from GitHub
    c.setup_simulation(
        '/Users/willbarnes/Desktop/',
        base_path='/Users/willbarnes/Documents/work/codes/HYDRAD/',
        name=f'hydrad_test_L{L.value:.0f}'
    )
