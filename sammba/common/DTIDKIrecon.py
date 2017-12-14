# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 17:31:50 2017

@author: nadka
"""
#%%

import os
import nibabel as ni
import numpy as np

#%%

def DTIDKI_proc_fixer(NIfTIdir):

#%%

    NIfTIdir = os.path.abspath(NIfTIdir)
    nc = open(os.path.join(NIfTIdir, 'namechanges.txt'))

#%%

    nclines = nc.readlines()
    plines = [ncline.split(' ')[-1] for ncline in nclines]
    nlines = [ncline.split(' ')[0] for ncline in nclines]
    ncDTIDKIs = [nlines[i] for i,x in enumerate(plines) if 'DTIDKI' in x]
    ncDTIDKI_bfs = [ncDTIDKI.split('__')[-1] for ncDTIDKI in ncDTIDKIs]
    ncDTIDKI_nxs = [plines[6][8:-1] for i,x in enumerate(plines) if 'DTIDKI' in x]

#%%

    DTIDKI_toproc = []
    
    filenames = os.listdir(NIfTIdir)
    
    for filename in filenames:
        if any('__' + bf + '.nii.gz' in filename for bf in ncDTIDKI_bfs):
            DTIDKI_toproc.append(filename)
    
    for filename in DTIDKI_toproc:
        bf = filename.split('__')[-1][:-7]
        filename_n = ncDTIDKI_nxs[ncDTIDKI_bfs.index(bf)]
    
#%%
        filenii = ni.load(os.path.join(NIfTIdir, filename))
        
        niiarray = filenii.get_data()
        newniiarray = niiarray.reshape(np.array(niiarray.shape)[[0,1,3,2]], order='F')
        newniiarray = np.transpose(newniiarray, (0,1,3,2))
        newfilenii = ni.Nifti1Image(newniiarray, filenii.affine)
        newfilename = 'DTIDKIproc_n' + filename_n + '.nii.gz'
        newfilenii.to_filename(os.path.join(NIfTIdir, newfilename))

