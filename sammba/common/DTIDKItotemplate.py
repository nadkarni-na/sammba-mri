# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 14:55:30 2017

@author: nadka
"""
#%%

import os
import subprocess
import glob

#%%

#get a proper pythoner to check this, am sure it's a disaster waiting to happen
def spco(*popenargs, **kwargs):
    x = subprocess.check_output(stderr=subprocess.STDOUT, *popenargs, **kwargs)
    return x


#%%

def DTIDKI_to_template(DTIDKI_nx, DTIDKI_A0n, anat_nx, template, tmpdir, scale,
                       registerfunctional, rminterfiles, brainvol, Urad,
                       logfile):

#%%

    DTIDKI_nx = os.path.abspath(DTIDKI_nx)
    DTIDKI_nx_stem = DTIDKI_nx[:-7]
    DTIDKI_nx_A0nx = DTIDKI_nx_stem + '_A0' + DTIDKI_A0n
    sink1 = spco(['3dcalc',
                  '-a', DTIDKI_nx_stem + '.nii.gz[' + DTIDKI_A0n + ']',
                  '-expr', 'a',
                  '-prefix', DTIDKI_nx_A0nx + '.nii.gz'])
    DTIDKI_nx_A0nxMn = DTIDKI_nx_A0nx + 'Mn'
    sink2 = spco(['3dTstat',
                  '-prefix', DTIDKI_nx_A0nxMn + '.nii.gz',
                  DTIDKI_nx_A0nx + '.nii.gz'])
    DTIDKI_nx_A0nxMnUn = DTIDKI_nx_A0nxMn + 'Un'
    sink3 = spco(['3dUnifize',
                  '-prefix', DTIDKI_nx_A0nxMnUn + '.nii.gz',
                  '-Urad', str(Urad),
                  DTIDKI_nx_A0nxMn + '.nii.gz[0]'])

#%%    

    #logging
    with open(logfile, 'a') as myfile:
        myfile.write("%s\n" % sink1)
        myfile.write("%s\n" % sink2)
        myfile.write("%s\n" % sink3)

#%%

    #bash script
    nx = os.path.basename(DTIDKI_nx_stem)[7:]
    imfilearray = os.path.join(DTIDKI_nx[:-7] + '_imfilearray.txt')
    with open(imfilearray, 'w') as myfile:
        myfile.write('DTIDKI_' + nx + '_A0' + DTIDKI_A0n + 'MnUn ' +
                     'DTIDKI_' + nx +
                     ' DTIDKIproc_' + nx)

    startdir = os.path.abspath(os.path.curdir)
    sink4 = spco(['perslice_registration_subpipeline.bash',
                  os.path.dirname(DTIDKI_nx), 'anat_n' + str(anat_nx) + '_Un',
                  imfilearray, 'atlas_Na1', 'yes', template, rminterfiles,
                  tmpdir, str(scale), registerfunctional, str(brainvol),
                  startdir])

#%%

    with open(logfile, 'a') as myfile:
        myfile.write("%s\n" % sink4)

#%%

def DTIDKI_to_template_looper(NIfTIdir, anat_nx, DTIDKI_A0n, template, tmpdir,
                              scale, registerfunctional, rminterfiles,
                              brainvol, Urad, logfile):

    all_DTIDKI_nx = glob.glob(os.path.join(NIfTIdir, 'DTIDKI_n[0-9].nii.gz'))

    for DTIDKI_nx in all_DTIDKI_nx:
        DTIDKI_to_template(DTIDKI_nx, DTIDKI_A0n, anat_nx, template, tmpdir,
                           scale, registerfunctional, rminterfiles, brainvol,
                           Urad, logfile)
