#!/bin/bash

export AFNI_DECONFLICT=OVERWRITE

rawdatadir=$(readlink -e $1)
savedir=$(readlink -e $2)
savename=$3
ZP=$4
isores=$5
saverawmeanvid=$6

find -L $rawdatadir -type d -name '*T2Lemur*.fid' | grep -v Mc147BCBB-01-s_2011042110-ptk_server_tasks/ptk_server_task_4 | sort > $savedir/rawdatadirs.txt
nlines=$(wc -l $savedir/rawdatadirs.txt | awk '{print $1}')

for ((a=1; a<=$nlines; a++)); do

	fiddir=$(head -n$a < $savedir/rawdatadirs.txt | tail -n1)
	newnifti=$(echo $fiddir | sed "s&$rawdatadir/&&g" | sed 's/\//__/g' | sed 's/.img//g' | tr -cd [:alnum:]-_)
	newniftidir=$savedir/$newnifti
	mkdir -p $newniftidir
	
	python -m VarianAgilentFIDtoNIfTI.py $fiddir $newniftidir/ZP.nii.gz $ZP
	3dresample -rmode Cubic -dxyz $isores $isores $isores -prefix $newniftidir/$savename -input $newniftidir/ZP.nii.gz
	3dZeropad -RL 256 -AP 256 -IS 256 -prefix $newniftidir/$savename $newniftidir/$savename
	
done

if [[ $saverawmeanvid == "yes" ]]; then
	3dTcat -prefix $savedir/raw_video.nii.gz $(find $savedir -name $savename)
	3dTstat -prefix $savedir/raw_mean.nii.gz $savedir/raw_video.nii.gz
fi
