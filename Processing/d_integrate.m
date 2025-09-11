clear;

sampleFolder = '..\';
inFolder = strcat(sampleFolder,'corrected\');
outFolder = strcat(sampleFolder, 'phase\');
if ~exist(outFolder)
    mkdir(outFolder);
    disp(['Folder ', outFolder, ' created successfully.']);
else
    disp(['Folder ', outFolder, ' already exists.']);
end

im_names = dir([inFolder,'*.tif']);

num_proj = length(im_names);

E = 13;
R1 = 6;
R2 = 60-R1;
gamma = 300;
px = 4.5e-3;

parfor idx = 1:num_proj

    fname = strcat(inFolder,im_names(idx).name);
    corrected = double(imread(fname));
    sample = double(imread(fname));
  
    phase = tie_hom(corrected, E, R1, R2, gamma, px);

    fname = strcat(outFolder,im_names(idx).name);
    imwrite2tif(phase, [], fname, 'single');

end