# -*- coding: utf-8 -*-

#this file may claim to provide functionality for converting all Varian/Agilent
#FID files to NIfTI-1 format, but in reality it was just dirtily worked up for
#some single-volume fsems data we have, acquired by parallel imaging (SENSE
#encoding?)

#%%
import numpy as np
import sys
import nmrglue
import nibabel

def rotate_affine(angle, axis):
    """
    rotate an affine matrix by the given angle in degrees about the given axis
    x, y or z used for orientation correction
    https://en.wikipedia.org/wiki/Rotation_formalisms_in_three_dimensions#Euler_angles_.28_z-y.E2.80.99-x.E2.80.B3_intrinsic.29_.E2.86.92_Rotation_matrix
    """
    a = angle * np.pi / 180
    s = np.sin(a)
    c = np.cos(a)
    if axis == 'x':
        return np.matrix([[ 1,  0,  0,  0],
                          [ 0,  c, -s,  0],
                          [ 0,  s,  c,  0],
                          [ 0,  0,  0,  1]])
    if axis == 'y':
        return np.matrix([[ c,  0,  s,  0],
                          [ 0,  1,  0,  0],
                          [-s,  0,  c,  0],
                          [ 0,  0,  0,  1]])
    if axis == 'z':
        return np.matrix([[ c, -s,  0,  0],
                          [ s,  c,  0,  0],
                          [ 0,  0,  1,  0],
                          [ 0,  0,  0,  1]])

#%%

def varianagilent_fsems_to_nifti(fiddir, savefilename, fftzpsize):
    """
    Reads the .fid directory of an fsems protocol (it only uses the procpar and
    fid itself) and converts to NIfTI-1 format at a destination of your
    choosing, with k-space reconstructed to whatever square matrix size you
    wish. Allowing for rectangular matrix sizes is not difficult in principle,
    though I suspect in practice it would be a pain, so is not implemented.
    There's no proper feedback on potential errors (of which there are a lot).
    No idea what it would do faced with multi-volume data.
    """
    
    #%%

    dic, data = nmrglue.varian.read(fiddir, as_2d = 1)
    
    #%%
    
    pss = np.array([float(value) for value in dic['procpar']['pss']['values']])
    pssorder = pss.argsort()
    
    pelist = np.array([int(value) for value in dic['procpar']['pelist']['values']])
    peorder = np.argsort(pelist - min(pelist))
    
    #%%
    
    nro = int(dic['np']/2) #number of readout lines
    npe = pelist.size #number of phase encodes. in the procpar I think this is nv
    #so (better?) alternative is maybe int(dic['procpar']['nv']['values'][0])
    ETL = int(dic['procpar']['etl']['values'][0]) #echo train length
    nslices = pss.size #number of slices
    nsegments = int(npe / ETL)
    nblocks = dic['nblocks']
    ntraces = dic['ntraces']
    
    seqcon = str(dic['procpar']['seqcon']['values'][0]) #code for looping order
    
    nrozp = int((fftzpsize - nro) / 2)
    npezp = int((fftzpsize - npe) / 2)
    
    #%%
    
    #it would take a book of comments to explain the following loops, and
    #especially the linepicker. I am not even sure if they are that well
    #conceived. the basic idea is to use the parameter information from the
    #procpar to figure out how to undo the FSE arrangement of k-space, the
    #slice select looping order, and also the 'blocking' order (can't remember
    #what this really is). a 2D fourier transform to whatever (square) matrix
    #size required is then carried out. the loop structure (given by seqcon
    #code) is, however, flexible, and I can't be bothered accounting for all
    #possible seqcon values
    
    if seqcon == 'nccnn':
        rawarray = np.empty((fftzpsize, fftzpsize, nslices, nblocks))
        for block in range(nblocks): #for us block is a sensiivity element
            for newslicen, slicen in zip(range(nslices), pssorder):
                #block and slice are not tiled or repeated as we only want one of each
                linepicker = (np.repeat(np.arange(nsegments), ETL) * nslices * ETL) + (
                             block * ntraces) + (
                             slicen * ETL) + (
                             np.tile(range(ETL), nsegments))
                linepicker = [int(x) for x in linepicker]
                kspace = np.pad(data[linepicker][peorder], (nrozp, npezp),
                                'constant', constant_values = (0, 0))
                rawarray[:, :, newslicen, block] = np.absolute(np.fft.fftshift(np.fft.fft2(kspace)))

    if seqcon == 'ncsnn':
        rawarray = np.empty((fftzpsize, fftzpsize, nslices, int(ntraces/nblocks)))
        reps = int(ntraces/nblocks)
        for rep in range(reps): #rep is prob a sensiivity element for us
            for newslicen, slicen in zip(range(nslices), pssorder):
                #linepicker = (slicen * ntraces) + np.arange(0, int(ntraces/reps)) + rep * nslices
                #linepicker = (slicen * ntraces) + np.arange(0, ntraces, ETL) + rep
                #linepicker = np.arange(0,len(data),ntraces) + slicen + (rep * nslices)
                linepicker = np.arange(0,len(data),ntraces) + slicen * (np.repeat(reps, nslices)) + rep

                linepicker = [int(x) for x in linepicker]
                kspace = np.pad(data[linepicker], (nrozp, npezp),
                                'constant', constant_values = (0, 0))
                #rawarray[:, :, newslicen, rep] = np.absolute(np.fft.fftshift(np.fft.fft2(kspace)))
                rawarray[:, :, newslicen, rep] = np.absolute(kspace)
    
    #rawarray = np.average(rawarray, axis = 3)

    



    #%%
    #the x, y, z, ro, pe and slice relationships are prob all fucked here
    
    dx = float(dic['procpar']['lro']['values'][0]) * 10 / fftzpsize #in cm not mm!
    dy = float(dic['procpar']['lpe']['values'][0]) * 10 / fftzpsize #in cm not mm!
    dz = float(dic['procpar']['thk']['values'][0])
    
    affine = np.matrix(
        [[dx,  0,  0, 0],
         [ 0, dz,  0, 0],
         [ 0,  0, dy, 0],
         [ 0,  0,  0, 1]])
    
    affine = affine * rotate_affine(270, 'x') * rotate_affine(180, 'y') * rotate_affine(180, 'z')
    
    header = nibabel.Nifti1Header()
    header.set_xyzt_units('mm', 'msec')
    header.set_data_dtype(np.int16)
    img = nibabel.Nifti1Image(rawarray, affine, header = header)
    img.to_filename(savefilename)


#%%
fiddir = sys.argv[1]
savefilename = sys.argv[2]
fftzpsize = int(sys.argv[3])
varianagilent_fsems_to_nifti(fiddir, savefilename, fftzpsize)
