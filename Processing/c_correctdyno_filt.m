%%

clear;

detector = 'primeBSI';
th = 0.02;

sampleFolder = '..\';
inFolder = strcat(sampleFolder,'data\');
outFolder = strcat(sampleFolder, 'corrected_filt2\');
if ~exist(outFolder)
    mkdir(outFolder);
    disp(['Folder ', outFolder, ' created successfully.']);
else
    disp(['Folder ', outFolder, ' already exists.']);
end

param_file = strcat(sampleFolder,'scan_parameters.txt');

exp = num2str(read_param('exp',param_file));
num_proj = read_param('num_proj ',param_file);
ang_range = read_param('rotation_angle',param_file);
numFlatFr = read_param('numFlatFr',param_file);
interval_flat = read_param('flat_interval',param_file);

switch detector
    case 'moment'
        ly = 2048;
        lx = 2048;
        px = 4.5e-3;
        rect = [305,305,1439,1439];
        flip = 1;

    case 'primeBSI'
        ly = 1314;
        lx = 1314;
        px = 27.9e-3;
        rect = [200,200,917,917];
        flip = 0;
end

jitter_flag = 0;

ref_step = 120; %degrees
ref_step_proj = num_proj/ang_range*ref_step;
ref_positions = 0:ref_step_proj:num_proj;
load shifts.mat

% fname = strcat(sampleFolder, 'BP_map.tif');
% BP_map = double(imread(fname));
% BP_map = imcrop(BP_map, rect);

if jitter_flag
    jitter_vec = readmatrix(strcat(sampleFolder,'jitter.txt')); %%%%
    jitter_vec_px = jitter_vec/px; %%%%
else
    jitter_vec = zeros(1,num_proj);
    jitter_vec_px = jitter_vec/px; %%%%
end

dark_names = dir([inFolder,'Dark*']);
numDarks = length(dark_names);
darks = zeros(ly,lx,numDarks);
for idx = 1:numDarks
    fname = strcat(inFolder,dark_names(1).name);
    darks(:,:,idx) = double(imread(fname));
end
dark = mean(darks,3);
% dark = remove_hot_pixels(dark,0.1);

flat_idc = 0:interval_flat:(num_proj-1);
flats = zeros(ly,lx,length(flat_idc)+1);
for idx = 1:length(flat_idc)
    
    flat_idx = flat_idc(idx);
    imname = strcat('flat_',exp,'sec_',num2str(numFlatFr),'proj',num2str(flat_idx),'.tiff');
    fname = strcat(inFolder,imname);
    flats(:,:,idx) = dark-double(imread(fname));

end
% flat = remove_hot_pixels(flat,0.1);
imname = strcat('flat_',exp,'sec_',num2str(numFlatFr),'Fr_proj_end.tiff');
fname = strcat(inFolder,imname);
flats(:,:,end) = dark-double(imread(fname));
flat_end = flats(:,:,end);

parfor idx = 1:num_proj

    im_name = strcat('Im_', (exp), 'sec_proj', num2str(idx-1), '.tiff');
    fname = strcat(inFolder,im_name);
    sample = double(imread(fname));
    % sample = remove_hot_pixels(sample,0.1);
    
    % Remove Dark
    sample = dark-sample;
    sample = fillmissing(sample,'linear');
    
    % Find Flat
    flat_idx = ceil(idx/interval_flat);
    flat_idx_pct = 1-rem(idx-1,interval_flat)/interval_flat;
    flat = flat_idx_pct*flats(:,:,flat_idx) + (1-flat_idx_pct)*flats(:,:,flat_idx+1);

    % Correct warped sample image with unwarped flat
    corrected = sample./flat;

    if flip
        corrected = flipud(corrected);
    end

    % Correct bad pixels
    % corrected(BP_map == 255) = NaN;
    corrected(corrected == -Inf) = NaN;
    corrected(corrected == Inf) = NaN;
    corrected = fillmissing(corrected,'linear');
    corrected = remove_hot_pixels(corrected,th);

    % Jitter
    corrected = circshift(corrected,jitter_vec_px(idx),2); 

    % Warp sample image that has drifted
    shift_y = interp1(ref_positions, trany, idx-1);
    shift_x = interp1(ref_positions, tranx, idx-1);
    translationMatrix = eye(3);
    translationMatrix([3,6]) = [shift_x,shift_y];
    tform = affine2d(translationMatrix);
    outputView = imref2d(size(corrected)); % Define output view
    corrected = imwarp(corrected, tform, 'OutputView', outputView);

    % Crop
    corrected = imcrop(corrected,rect);

    % Save
    im_name = strcat('proj', num2str(idx), '.tif');
    fname = strcat(outFolder,im_name);
    imwrite2tif(corrected, [], fname, 'single');

end

%% End Projection

% Load and dark removal
im_name = strcat('Im_', num2str(exp), 'sec_proj_end.tiff');
fname = strcat(inFolder,im_name);
sample = double(imread(fname));
sample = dark-sample;
corrected = sample./flat_end;
if flip
    corrected = flipud(corrected);
end

% Remove bad pixels
% corrected(BP_map == 255) = NaN;
corrected(corrected == -Inf) = NaN;
corrected(corrected == Inf) = NaN;
corrected = fillmissing(corrected,'linear');
corrected = remove_hot_pixels(corrected,th);

% Jitter
corrected = circshift(corrected,jitter_vec_px(end),2);

% Warp
shift_y = trany(end);
shift_x = tranx(end);
translationMatrix = eye(3);
translationMatrix([3,6]) = [shift_x,shift_y];
tform = affine2d(translationMatrix);
outputView = imref2d(size(corrected)); % Define output view
warped = imwarp(corrected, tform, 'OutputView', outputView);

% Crop
warped = imcrop(warped,rect);

% Save
im_name = strcat('proj_end', '.tif');
fname = strcat(outFolder,im_name);
imwrite2tif(warped, [], fname, 'single');

%%

function img_filtered = remove_hot_pixels(img, threshold_multiplier)
    % Convert to double for precision
    img = double(img);
    
    % Compute local median using a 3x3 neighborhood
    median_filtered = medfilt2(img, [3, 3]);
    
    % Compute the absolute difference
    diff_img = abs(img - median_filtered);
    
    % Set threshold as a multiple of standard deviation
    threshold = threshold_multiplier * std(img(:));
    
    % Identify outliers (hot pixels)
    hot_pixel_mask = diff_img > threshold;
    
    % Replace hot pixels with median-filtered values
    img_filtered = img;
    img_filtered(hot_pixel_mask) = median_filtered(hot_pixel_mask);
    
    % Convert back to original type
    img_filtered = cast(img_filtered, class(img));
end