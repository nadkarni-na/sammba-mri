# -*- coding: utf-8 -*-
"""
Created on Thu Dec 07 13:58:36 2017

@author: nn241023
"""

import numpy as np
import os
import nibabel

#%%

sourcedir = u'Y://Tvx-Manips-MD_/MD_1005-SPM-Mouse-SteveSawiak-------------' + \
            u'Publi-2014/Analyses-Article-2014/100302-Donnée-Initialement-' + \
            u'donnée-a-Steve'

savedir = "Y://Tvx-Manips-MD_/MD_1701-Microcebe-Creation-Atlas/sawiakreprocessing/NIfTI"

twodseqfilelist = [
    'Young-7Animals/2dseq-103A-1',
    'Young-7Animals/2dseq-934GD-2',
    'Young-7Animals/2dseq-911ND-1',
    'Young-7Animals/2dseq-121A-1',
    'Young-7Animals/2dseq-978F-1',
    'Young-7Animals/2dseq-985B-1',
    'Young-7Animals/2dseq-941J-1',
    'Middle-Aged_11Animals/2dseq-967-1',
    'Middle-Aged_11Animals/2dseq-964B-1',
    'Middle-Aged_11Animals/2dseq-921BAB-1',
    'Middle-Aged_11Animals/2dseq-831ILD-1',
    'Middle-Aged_11Animals/2dseq-943ACA-1',
    'Middle-Aged_11Animals/2dseq-901AED-1',
    'Middle-Aged_11Animals/2dseq-913BCG-1bis',
    'Middle-Aged_11Animals/2dseq-893AAB-1',
    'Middle-Aged_11Animals/2dseq-911KH-1',
    'Middle-Aged_11Animals/2dseq-896AF-1',
    'Middle-Aged_11Animals/2dseq-911FF-1',
    'Old-12Animals/2dseq-920AA-1',
    'Old-12Animals/2dseq-318AD-1',
    'Old-12Animals/2dseq-950A-1',
    'Old-12Animals/2dseq-326AD-2',
    'Old-12Animals/2dseq-342ADC-1',
    'Old-12Animals/2dseq-831ILA-2',
    'Old-12Animals/2dseq-932AA-1',
    'Old-12Animals/2dseq-871CDC-1',
    'Old-12Animals/2dseq-911J-2',
    u'Old-12Animals/2dseq-90µ2-1',
    'Old-12Animals/2dseq-883C-4',
    'Old-12Animals/2dseq-520HHEC-1']

#%%
    
for twodseqfile in twodseqfilelist:
    rawfile = os.path.join(sourcedir, twodseqfile)
    rawarray = np.fromfile(rawfile, dtype = '>u4')
    rawarray = np.reshape(rawarray, (128, 128, 128))
    img = nibabel.Nifti1Image(rawarray, np.eye(4, dtype=int))
    img.to_filename(os.path.join(savedir, twodseqfile.replace('/','_') + '.nii.gz'))

