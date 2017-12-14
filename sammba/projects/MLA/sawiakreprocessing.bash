#!/bin/bash

#bash /home/nadkarni/git/sammba-mri/sammba/projects/MLA/sawiakreprocessing.bash 2>&1 | tee /home/Pmamobipet/Tvx-Manips-MD_/MD_1701-Microcebe-Creation-Atlas/sawiakreprocessing/$(date +%Y%m%d_%H%M%S).log

projectdir=/home/Pmamobipet/Tvx-Manips-MD_/MD_1701-Microcebe-Creation-Atlas
startdir=$projectdir/sawiakreprocessing
cd $startdir

template=$startdir/template_lowres.nii.gz
atlas=$startdir/atlas_lowres.nii.gz

3dresample -dxyz 0.234375 0.234375 0.234375 -rmode Cu -prefix $template -input $projectdir/essai_JLP/Apr2Feb.nii.gz
3dresample -dxyz 0.234375 0.234375 0.234375 -rmode NN -prefix $atlas -input $projectdir/essai_JLP/Lemur-Atlas-Apr2Feb-cx-claustrum-label.nii
3dmask_tool -input atlas_lowres.nii.gz -prefix mask_dil1.nii.gz -dilate_input 1
3dmask_tool -input atlas_lowres.nii.gz -prefix mask_dil4.nii.gz -dilate_input 4

mkdir processed

anats=$(ls NIfTI)
for anat in $anats; do

	savedir=processed/$(echo $anat | sed 's/.nii.gz//g' | tr -cd [:alnum:]-_)
	mkdir $savedir
	
	cp NIfTI/$anat $savedir/anat.nii.gz
	
	cd $savedir

	3drefit -orient PSR -xorigin 15 -yorigin 15 -zorigin 15 -xdel 0.234375 -ydel 0.234375 -zdel 0.234375 anat.nii.gz
	
	if [ $anat == "Old-12Animals_2dseq-318AD-1.nii.gz" ]; then
		3drefit -orient SPR -xorigin 15 -yorigin 15 -zorigin 15 -xdel 0.234375 -ydel 0.234375 -zdel 0.234375 anat.nii.gz
	fi

	3dUnifize -prefix anat_Bc05.nii.gz -clfrac 0.5 anat.nii.gz
	3dUnifize -prefix anat_Bc02.nii.gz -clfrac 0.2 anat.nii.gz

	thresh=$(3dClipLevel anat_Bc05.nii.gz)
	printf -v thresh %.0f "$thresh"
	echo "brain/background threshold=$thresh"
	RATS_MM anat_Bc05.nii.gz anat_Bc05Bm.nii.gz -v 1800 -t $thresh
	3dcalc -a anat_Bc02.nii.gz -b anat_Bc05Bm.nii.gz -expr 'a*b' -prefix anat_BcBmBe.nii.gz

	3dAllineate -base $template -source anat_BcBmBe.nii.gz -prefix anat_BcBmBeAl.nii.gz \
		-1Dmatrix_save anat_BcBmBeAl.aff12.1D -cost nmi -conv 0.01 -twopass \
		-twoblur 2.2 -cmass -weight $startdir/mask_dil1.nii.gz -master $template
	cat_matvec -ONELINE anat_BcBmBeAl.aff12.1D -I > anat_BcBmBeAl_INV.aff12.1D
	3dAllineate -input anat_Bc02.nii.gz -master $template -prefix anat_BcAa.nii.gz -1Dmatrix_apply anat_BcBmBeAl.aff12.1D

	3dQwarp -base $template -source anat_BcAa.nii.gz -prefix anat_BcAaQw.nii.gz -nmi -iwarp -noneg -weight $startdir/mask_dil4.nii.gz -blur 0

	3dNwarpApply -nwarp anat_BcBmBeAl_INV.aff12.1D anat_BcAaQw_WARPINV.nii.gz -source $atlas -master anat_Bc02.nii.gz -ainterp NN -prefix atlas_Na1.nii.gz
	3dNwarpApply -nwarp anat_BcBmBeAl_INV.aff12.1D anat_BcAaQw_WARPINV.nii.gz -source $startdir/mask_dil1.nii.gz -master anat_Bc02.nii.gz -ainterp NN -prefix brainmask_dil1.nii.gz

	Atropos -a anat_Bc02.nii.gz -i KMeans[10] -x brainmask_dil1.nii.gz -o atropos.nii.gz -m 0
	3dcalc -a atropos.nii.gz -expr 'ispositive(a-7)' -prefix atroposCSF.nii.gz
	3dcalc -a atlas_Na1.nii.gz -b atroposCSF.nii.gz -expr 'a*((b-1)^2)' -prefix atroposatlas_Na1.nii.gz
	3dcalc -a brainmask_dil1.nii.gz -b atroposCSF.nii.gz -expr 'a*((b-1)^2)' -prefix atroposbrainmask_dil1.nii.gz

	cd $startdir

done
