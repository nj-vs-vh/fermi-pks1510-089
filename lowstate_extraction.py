"""
Extraction of specific time interval from large Fermi data set.

Module automates config creation and runs fermitools utils.
"""

import os
import yaml
pyamlVer = yaml.__version__
import datetime

from fermipy.gtanalysis import GTAnalysis


BASE_CONFIG = '/home/njvh/Fermi_data/PKS1510-089/config_5day_binning.yaml'


def set_base_config(newbaseconfig):
    """
    To change base config from outside
    """
    global BASE_CONFIG
    BASE_CONFIG = newbaseconfig


def prepare_temp_config(tmin, tmax, outdir=None, find_directory=False):
    with open(BASE_CONFIG) as file:
        if int(pyamlVer[0]) >= 5 :
            config = yaml.load(file, Loader=yaml.FullLoader)
        else : 
            config = yaml.load(file)

    if outdir is None:
        outdir = 'out_temp_from_{}_to_{}'.format(int(tmin), int(tmax))
    outdir = os.path.join(os.getcwd(), outdir)
    if os.path.exists(outdir):
        if not find_directory:
            raise OSError('Outdir \'{}\' already exists!'.format(outdir))
        version = 2
        while os.path.exists(outdir + '_v{}'.format(version)):
            version += 1
        outdir = outdir + '_v{}'.format(version)
    os.mkdir(outdir)

    config['fileio'] = dict()
    config['fileio']['outdir'] = outdir
    config['selection']['tmin'] = tmin
    config['selection']['tmax'] = tmax

    config_path = os.path.join(outdir, 'temp_config.yaml')

    with open(config_path, 'w') as f:
        f.write(
            '# Automatically created from \'{}\' on {}\n\n'
            .format(BASE_CONFIG, datetime.datetime.now())
        )
        yaml.dump(config, f, indent=4)

    return config_path, outdir


def extract_photons_data(tmin, tmax, outdir=None, find_directory=False):
    """Perform GTAnalysis setup with custom tmin and tmax.
    For details see PKS notebook"""
    config_path, outdir = prepare_temp_config(
        tmin, tmax, outdir, find_directory
    )

    gta = GTAnalysis(config_path, logging={'verbosity': 3})
    gta.setup()

    return outdir


if __name__ == "__main__":
    # config_path, outdir = prepare_temp_config(0, 0)
    # with open(config_path) as f:
    # if int(pyamlVer[0]) >= 5 :
    #        print(yaml.load(file, Loader=yaml.FullLoader))
    #    else : 
    #       print(yaml.load(file))
    extract_photons_data(244093400.0, 252733400.0)
