library(ggplot2)
library(readxl)

anatROIs = function(anatfile){
  afnitbl = read.table(text = system2("/usr/lib/afni/bin/3dhistog",
                                      c("-int", anatfile),
                                      stdout = TRUE, stderr = FALSE), 
                       col.names = c("label", "count", "CumFreq"))
  afnitbl$CumFreq = NULL
  afnitbl$fname = anatfile
  afnitbl$volume = afnitbl$count * 0.234375 ^ 3
  afnitbl
}

anatomydir = "/home/Pmamobipet/Tvx-Manips-MD_/MD_1701-Microcebe-Creation-Atlas/sawiakreprocessing/processed"

brains = lapply(grep("atropos", list.files(anatomydir, pattern = 'brainmask_dil1.nii.gz', full.names = T, recursive = T), value=TRUE, invert=TRUE), anatROIs)
atlases = lapply(grep("atropos", list.files(anatomydir, pattern = 'atlas_Na1.nii.gz', full.names = T, recursive = T), value=TRUE, invert=TRUE), anatROIs)
atroposCSF = lapply(list.files(anatomydir, pattern = 'atroposCSF.nii.gz', full.names = T, recursive = T), anatROIs)
atroposbrains = lapply(list.files(anatomydir, pattern = 'atroposbrainmask_dil1.nii.gz', full.names = T, recursive = T), anatROIs)
atroposatlases = lapply(list.files(anatomydir, pattern = 'atroposatlas_Na1.nii.gz', full.names = T, recursive = T), anatROIs)
brains = do.call(rbind, brains)
atlases = do.call(rbind, atlases)
atroposCSF = do.call(rbind, atroposCSF)
atroposbrains = do.call(rbind, atroposbrains)
atroposatlases = do.call(rbind, atroposatlases)
brains$type = "whole"
atlases$type = "regional"
atroposCSF$type = "CSF"
atroposbrains$type = "atrbrain"
atroposatlases$type = "atrreg"

allhistog = rbind(brains, atlases, atroposCSF, atroposbrains, atroposatlases)

#whole brain will be given region Right hippocampus in the code below LOL

labelfile = "/home/Pmamobipet/Tvx-Manips-MD_/MD_1704_RsLemurs/atlas/Region_pour_python.xlsx"
labeltable = read_xlsx(labelfile)
names(labeltable) = c("label", "blah2", "blah3", "blah4", "side", "blah6", "blah7", "region")
merged = merge(allhistog, labeltable)
s = strsplit(basename(dirname(merged$fname)), "Animals_2dseq-")
merged$animalname = sapply(s, "[[", 2)
merged$group = sapply(s, "[[", 1)
merged$group = gsub("Young-7", "Y", merged$group)
merged$group = gsub("Middle-Aged_11", "M", merged$group)
merged$group = gsub("Old-12", "O", merged$group)
merged$group = factor(merged$group, levels = c("Y","M","O"))

animals = read_xls(paste("/home/Pmamobipet/Tvx-Manips-MD_/",
                         "MD_1005-SPM-Mouse-SteveSawiak-------------Publi-2014/",
                         "Analyses-Article-2014/",
                         "100302-Donnée-Initialement-donnée-a-Steve/Animals.xls",
                         sep = ""))
names(animals) = c("animalname", "age", "stage", "opthamology")
animals = subset (animals, select=c("animalname", "age", "stage", "opthamology"))
animals = na.omit(animals)
animals$animalname = gsub("950 A (Male)", "950A-1", animals$animalname, fixed=TRUE)
animals$animalname = gsub("831 ILA-2 (Male)", "831ILA-2", animals$animalname, fixed=TRUE)
animals$animalname = gsub("871  CDC (Female)", "871CDC-1", animals$animalname, fixed=TRUE)
animals$animalname = gsub("893AAB", "893AAB-1", animals$animalname, fixed=TRUE)
animals$animalname = gsub("896AF", "896AF-1", animals$animalname, fixed=TRUE)
animals$animalname = gsub("901AED", "901AED-1", animals$animalname, fixed=TRUE)
animals$animalname = gsub("90µ2-1", "902-1", animals$animalname, fixed=TRUE)
animals$animalname = gsub("911FF", "911FF-1", animals$animalname, fixed=TRUE)
animals$animalname = gsub("913BCG", "913BCG-1bis", animals$animalname, fixed=TRUE)
animals$animalname = gsub("932AA (Male)", "932AA-1", animals$animalname, fixed=TRUE)
animals$animalname = gsub("964B", "964B-1", animals$animalname, fixed=TRUE)
animals$animalname = gsub("967A", "967A-1", animals$animalname, fixed=TRUE)
merged$animalname = gsub("967-1", "967A-1", merged$animalname, fixed=TRUE)

merged = merge(animals, merged)

qplot(group, volume, data=subset(merged,
                                 type == "atrreg" & region == "Left hippocampus"),
      geom="boxplot", outlier.shape=NA, ymin=0) + 
  geom_point(position=position_jitter(width=0.2))

qplot(group, volume, data=subset(merged, type == "atrbrain" & region != "Clear Label"),
      geom="boxplot", outlier.shape=NA, ymin=0) + 
  geom_point(position=position_jitter(width=0.2))

qplot(group, volume, data=subset(merged, type == "CSF" & region != "Clear Label"),
      geom="boxplot", outlier.shape=NA, ymin=0) + 
  geom_point(position=position_jitter(width=0.2)) +
geom_text(aes(label = animalname))

qplot(age, volume, data=subset(merged,
                                 type == "atrbrain" & region != "Clear Label"),
      ymin=0)




a = qplot(group, volume, data = regional, geom = "boxplot", outlier.shape=NA) +
  geom_jitter(width = 0.2) +
  facet_wrap(~region, scales = "free_y")

pdf(file = "anat.pdf", width = 15* sqrt(2), height = 15)
a
dev.off()

for (regionname in labeltable$region) {
  capture.output(regionname, file = "grouptests.txt", append = TRUE)
  capture.output(t.test(volume ~ group, data = subset(regional, region == regionname)), file = "grouptests.txt", append = TRUE)
  capture.output(wilcox.test(volume ~ group, data = subset(regional, region == regionname)), file = "grouptests.txt", append = TRUE)  
}


png("whole.png", width = 10, height = 10, units = "cm", res = 300)
  qplot(group, volume, data = whole, geom = "boxplot", outlier.shape = NA) +
    geom_jitter(aes(colour = Sex), width = 0.2) +
    ylab(expression(volume ~ (mm ^ {3}))) +
    ggtitle("whole brain volume")
dev.off()

png("basalforebrain.png", width = 10, height = 5, units = "cm", res = 300)
qplot(group, volume, data = subset(regional, label %in% c(24, 25)),
      geom = "boxplot", outlier.shape = NA) +
    geom_jitter(aes(colour = Sex), width = 0.2) +
    facet_wrap(~name) +
    ylab(expression(volume ~ (mm ^ {3}))) +
    ggtitle("basal forebrain volume")
dev.off()  

png("putamen.png", width = 10, height = 5, units = "cm", res = 300)
qplot(group, volume, data = subset(regional, label %in% c(34, 35)),
      geom = "boxplot", outlier.shape = NA) +
  geom_jitter(aes(colour = Sex), width = 0.2) +
  facet_wrap(~name) +
  ylab(expression(volume ~ (mm ^ {3}))) +
  ggtitle("putamen volume")
dev.off()  


