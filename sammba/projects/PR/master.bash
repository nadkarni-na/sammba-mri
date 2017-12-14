PATH=$PATH:/home/nadkarni/git/sammba-mri/sammba/common
PATH=$PATH:/home/nadkarni/git/sammba-mri/sammba/projects/MLA
export PATH

mkdir test
mkdir test/bf3
mkdir test/bf5
mkdir test/bf7
mkdir test/bf9

cp 20171109_101609_MSME_MIRCen_RatBrain_atlas_fixedSIAP_bf3.nii.gz test/bf3/anat.nii.gz
cp 20171109_110206_MSME_MIRCen_RatBrain_atlas_fixedSIAP_bf5.nii.gz test/bf5/anat.nii.gz
cp 20171109_113517_MSME_MIRCen_RatBrain_atlas_fixedSIAP_bf7.nii.gz test/bf7/anat.nii.gz
cp 20171109_120835_MSME_MIRCen_RatBrain_atlas_fixedSIAP_bf9.nii.gz test/bf9/anat.nii.gz

bash MRIT2_PRextrcen.bash test 1800 18.3 70 80 0.6 0.2
bash MRIT3_shr.bash test test/UnBmBeCC_mean.nii.gz 1 0.01 2
bash MRIT3_shr.bash $savedir $savedir/shr1_mean.nii.gz 2 $conv $twoblur
bash MRIT4_aff.bash $savedir $savedir/shr2_meanhead.nii.gz 2 3 $conv $twoblur $savedir/shr2_count.nii.gz

3dmask_tool -frac 0.5 -inputs $savedir/aff3_video.nii.gz -prefix $savedir/aff3_frac05mask.nii.gz
3dcalc -a $savedir/aff3_meanhead.nii.gz -expr 'step(2-(x+6.7)*(x+6.7)-(y+3.7)*(y+3.7)-(z-7.65)*(z-7.65))' -prefix $savedir/rightcolliculus.nii.gz
3dcalc -a $savedir/aff3_meanhead.nii.gz -expr 'step(2-(x-6.5)*(x-6.5)-(y+3.7)*(y+3.7)-(z-7.65)*(z-7.65))' -prefix $savedir/leftcolliculus.nii.gz
3dmask_tool -union -inputs $savedir/aff3_frac05mask.nii.gz $savedir/rightcolliculus.nii.gz $savedir/leftcolliculus.nii.gz -prefix $savedir/aff3_unionmask.nii.gz
3dmask_tool -dilate_inputs 5 -inputs $savedir/aff3_unionmask.nii.gz -prefix $savedir/aff3_unionmaskdil5.nii.gz
weight=$savedir/aff3_unionmaskdil5.nii.gz

bash MRIT5_Qw.bash $savedir $savedir/aff3_meanhead.nii.gz $weight UnCC.nii.gz UnBmBeCCAl2UnCCAl3.aff12.1D 0 2 1
bash MRIT5_Qw.bash $savedir $savedir/Qw1_meanhead.nii.gz $weight UnCC.nii.gz UnCCQw1_WARP.nii.gz 3 5 2
bash MRIT5_Qw.bash $savedir $savedir/Qw2_meanhead.nii.gz $weight UnCC.nii.gz UnCCQw2_WARP.nii.gz 6 7 3
bash MRIT6_Qw.bash $savedir $savedir/Qw3_meanhead.nii.gz $weight UnCC.nii.gz UnCCQw3_WARP.nii.gz 8 11 4

