# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 17:26:06 2017

@author: nn241023
"""

#%%

import os
import random
from time import gmtime, strftime
import pandas as pd
import shutil

startdir = os.path.abspath(os.path.curdir)
#commonPATH = '/mnt/c/Users/nadka/OneDrive/Downloads/git/git/sammba-mri/sammba/common'
commonPATH = '/home/nadkarni/git/sammba-mri/sammba/common'
os.chdir(commonPATH)

import PVEnDCMtoNIfTI
import IDprotocoltypes
import pipelinedefs
import DTIDKIrecon
import DTIDKItotemplate

os.chdir(startdir)
#afniPATH = '/usr/lib/afni/bin'
#antsPATH = '/usr/lib/ants'
#RATSPATH = '/mnt/c/Users/nadka/OneDrive/Downloads/gittmp/RATS/extracted/distribution'

#os.environ['PATH'] += ':' + afniPATH + ':' + antsPATH + ':' + RATSPATH + ':' + commonPATH
os.environ['PATH'] += ':' + commonPATH
os.environ['AFNI_DECONFLICT'] = 'OVERWRITE'

#%%

projectdir = '/home/Promane/2014-ROMANE/5_Experimental-Plan-Experiments-Results/mouse/Laura'
projectxlsx = os.path.join(projectdir, 'mousedb.xlsx')
analysisdir = os.path.join(projectdir, 'analysis20171128')
templatedir = '/home/Promane/2014-ROMANE/5_Experimental-Plan-Experiments-Results/mouse/MRIatlases/MIC40C57/20170223'
brain = os.path.join(templatedir, 'brain100.nii.gz')
atlas = os.path.join(templatedir, 'labels100.nii.gz')
mask = os.path.join(templatedir, 'mask100.nii.gz')
head = os.path.join(templatedir, 'head100.nii.gz')
headweight = os.path.join(templatedir, 'mask100dil7.nii.gz')
basetype = 'head'
dofolderoverwrite = 'no'
tmpdir = os.path.join('/volatile', 'tmpanaldir_' + str(random.randrange(100000, 1000000)))
registerfunctional = 'no'
Urad = 18.3
brainvol = 400
scale = 0.1
protocol_dict = {
    'anat':['__T2_TurboRARE__', '__T2_TurboRARE_3D__', 'T1_FLASH_3D'],
    'DTIDKI':['Diffusion_weight_EPI_']}
dcmdump_path = '/usr/bin/dcmdump'
SIAPfix = 'yes'
logfile = os.path.join(projectdir, 'analysis20171128', strftime("%Y%m%d_%H%M%S", gmtime()) + '_log.txt')
rminterfiles = 'yes'

#%%
def pipeline(PVdir, NIfTIdir, brain, atlas, mask, head, headweight, basetype,
             tmpdir, registerfunctional, Urad, brainvol, scale, infotab,
             logfile):

    PVEnDCMtoNIfTI.recursive_EnDCMs_to_NIIs(dcmdump_path, PVdir, NIfTIdir, SIAPfix)
    IDprotocoltypes.ID_protocol_types(protocol_dict, NIfTIdir)
    
    try:
        anat_nx = int(infotab.anat.tolist()[0])
    except:
        anat_nx = 0
    biascorrector = 'Un'

    pipelinedefs.anat_to_template(NIfTIdir, anat_nx, tmpdir, biascorrector,
                                  brainvol, scale, brain, atlas, mask, head,
                                  headweight, basetype, Urad, logfile)

#%%

if not os.path.exists(analysisdir):
    os.mkdir(analysisdir)
os.mkdir(tmpdir)

#%%

MRIsessions = pd.read_excel(projectxlsx, sheetname=1)
PVdirs = [str(x) for x in MRIsessions.PVdir.tolist()]

#%%

for PVdir in PVdirs:
    infotab = MRIsessions[(MRIsessions.PVdir == PVdir)]
    NIfTIdir = os.path.join(analysisdir, os.path.basename(PVdir))
    if not os.path.exists(NIfTIdir):
        os.mkdir(NIfTIdir)
        pipeline(PVdir, NIfTIdir, brain, atlas, mask, head, headweight,
                 basetype, tmpdir, registerfunctional, Urad, brainvol, scale,
                 infotab, logfile)

#%%

shutil.rmtree(tmpdir)

