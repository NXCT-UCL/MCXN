clear;

sampleFolder = 'D:\25_04_07\8_MuscleGFPD9_40kv_1p2um\';
inFolder = strcat(sampleFolder,'corrected_dyno\');
outFolder = strcat(sampleFolder, 'phase1000_dyno_filt\');
if ~exist(outFolder)
    mkdir(outFolder);
    disp(['Folder ', outFolder, ' created successfully.']);
else
    disp(['Folder ', outFolder, ' already exists.']);
end

im_names = dir([inFolder,'*.tif']);

num_proj = length(im_names);

bin_fact = 1;
lx = 4096;
ly = 4096;

E = 12;
R1 = 4.0769;
R2 = 64.5785-R1;
gamma = 1000;
px = 8e-3;

parfor idx = 1:num_proj

    fname = strcat(inFolder,im_names(idx).name);
    corrected = double(imread(fname));
    sample = double(loadRawImage(fname));
  
    phase = tie_hom(corrected, E, R1, R2, gamma, px);

    fname = strcat(outFolder,im_names(idx).name);
    imwrite2tif(phase, [], fname, 'single');

end