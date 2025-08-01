clear;

sampleFolder = '..\';
inFolder = strcat(sampleFolder,'corrected_filt2\');
outFolder = strcat(sampleFolder, 'phase_filt2\');
if ~exist(outFolder)
    mkdir(outFolder);
    disp(['Folder ', outFolder, ' created successfully.']);
else
    disp(['Folder ', outFolder, ' already exists.']);
end

im_names = dir([inFolder,'*.tif']);

num_proj = length(im_names);

bin_fact = 1;
lx = 1440;
ly = 1440;

E = 15;
R1 = 9.7571;
R2 = 33.3470-R1;
gamma = 1000;
px = 4.5e-3;

parfor idx = 1:num_proj

    fname = strcat(inFolder,im_names(idx).name);
    corrected = double(imread(fname));
    sample = double(imread(fname));
  
    phase = tie_hom(corrected, E, R1, R2, gamma, px);

    fname = strcat(outFolder,im_names(idx).name);
    imwrite2tif(phase, [], fname, 'single');

end