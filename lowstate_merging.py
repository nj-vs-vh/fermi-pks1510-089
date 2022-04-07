"""Merging several time epochs, specified by MET, into one fermipy config

This script reads time intervals (e.g. produced in lowstate_selection.ipynb),
extracts data for each one with lowstate_extraction.py helper module and
merges them into one config, ready for GTAnalysis
"""

import os
import subprocess
import yaml
pyamlVer = yaml.__version__

from fermipy.gtanalysis import GTAnalysis

from lowstate_extraction import extract_photons_data, BASE_CONFIG


EPOCHS_FILE = 'lowstate_MET_times.txt'  # from lowstate_selection.ipynb

LTCUBE_FINAL_FILE = 'ltcubes_merged.fits'
FT1_FILES_LIST = 'ft1_merged.lst'
CONFIG_FINAL_FILE = 'config_merged.yaml'


def join_ltcubes(outdirs):
    ltcubes_list = 'ltcubes_temp.lst'
    with open(ltcubes_list, 'w') as f:
        for od in outdirs:
            f.write(
                os.path.join(od, 'ltcube_00.fits') + '\n'
            )

    cmd = 'gtltsum infile1={} outfile={}'.format(
        ltcubes_list, LTCUBE_FINAL_FILE
    )
    print(subprocess.check_output(cmd, shell=True))


if __name__ == "__main__":
    outdirs = []
    with open(EPOCHS_FILE) as f:
        for line in f:
            start, end = [float(MET) for MET in line.split()]
            outdir = extract_photons_data(start, end)
            outdirs.append(outdir)

    # testing
    # outdirs = [
    #     '/home/njvh/Fermi/PKS1510-089/out_temp_from_239773400_to_242365400',
    #     '/home/njvh/Fermi/PKS1510-089/out_temp_from_244093400_to_252733400'
    # ]

    join_ltcubes(outdirs)  # generate joined ltcube from calculated

    # create list of photons (ft1) files, outputted by extractor
    with open(FT1_FILES_LIST, 'w') as f:
        for od in outdirs:
            f.write(
                os.path.join(od, 'ft1_00.fits') + '\n'
            )

    # modify base config to include merged files
    with open(BASE_CONFIG) as infile, \
            open(CONFIG_FINAL_FILE, 'w') as outfile:
        if int(pyamlVer[0]) >= 5 :
            config = yaml.load(infile, Loader=yaml.FullLoader)
        else : 
            config = yaml.load(infile)
        config['data']['evfile'] = os.path.join(os.getcwd(), FT1_FILES_LIST)
        config['data']['ltcube'] = os.path.join(os.getcwd(), LTCUBE_FINAL_FILE)
        config['fileio'] = {'outdir': 'out_merged/'}
        outfile.write('# Automatically merged from directories:\n')
        for outdir in outdirs:
            outfile.write('# {}\n'.format(outdir))
        outfile.write('\n')
        yaml.dump(config, outfile, indent=4)

    # some generic processing just for sanity check
    gta = GTAnalysis(CONFIG_FINAL_FILE, logging={'verbosity': 3})
    gta.setup()
    gta.free_source('4FGL J1512.8-0906', free=True, pars=['Index'])
    gta.free_source('4FGL J1512.8-0906', free=True, pars='norm')
    # Free Normalization of all Sources within 3 deg of ROI center
    gta.free_sources(distance=3.0, pars='norm')
    # Free all parameters of isotropic and galactic diffuse components
    gta.free_source('galdiff')
    gta.free_source('isodiff')
    gta.optimize()
    gta.print_roi()
    fit_res = gta.fit()
    print('Fit Quality: ', fit_res['fit_quality'])
    print(gta.roi['4FGL J1512.8-0906'])
