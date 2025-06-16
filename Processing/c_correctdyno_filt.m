
sampleFolder = 'D:\25_04_07\8_MuscleGFPD9_40kv_1p2um\';
inFolder = strcat(sampleFolder,'data\');
outFolder = strcat(sampleFolder, 'corrected_dyno\');
if ~exist(outFolder)
    mkdir(outFolder);
    disp(['Folder ', outFolder, ' created successfully.']);
else
    disp(['Folder ', outFolder, ' already exists.']);
end

num_proj = 4000;
ang_range = 360;

exp = '3';
numFr = 64;
bin_fact = 1;
lx = 4096;
ly = 4096;
interval_flat = 100;

rect = [48,48,3999,3999];

E = 12;
R1 = 4.0769;
R2 = 64.5785-R1;
gamma = 100;
px = 8e-3;

ref_step = 9; %degrees
ref_step_proj = num_proj/ang_range*ref_step;
ref_positions = 0:ref_step_proj:num_proj;
load shifts.mat

fname = strcat(sampleFolder, 'BP_map_STD.tif');
BP_map = double(imread(fname));
BP_map = imcrop(BP_map, rect);

jitter_vec = readmatrix(strcat(sampleFolder,'jitter.txt')); %%%%
jitter_vec_px = jitter_vec/px; %%%%

dark_names = dir([inFolder,'Dark*']);
numDarks = length(dark_names);
darks = zeros(ly,lx,numDarks);
for idx = 1:numDarks
    fname = strcat(inFolder,dark_names(1).name);
    darks(:,:,idx) = double(loadRawImage(fname));
end
dark = mean(darks,3);
% dark = remove_hot_pixels(dark,0.1);

flat_names = dir(fullfile(inFolder,'flat*'));
flats = zeros(ly,lx,length(flat_names));
for idx = 1:length(flat_names)
    
    fname = strcat(inFolder,flat_names(idx).name);
    flats(:,:,idx) = dark-double(loadRawImage(fname));

end
% flat = remove_hot_pixels(flat,0.1);
flat_end = flats(:,:,end);

parfor idx = 1:num_proj

    im_name = strcat('Im_', (exp), 'sec_proj', num2str(idx-1), '.raw');
    fname = strcat(inFolder,im_name);
    sample = double(loadRawImage(fname));
    % sample = remove_hot_pixels(sample,0.1);

    sample = dark-sample;
    sample = fillmissing(sample,'linear');
    
    flat_idx = ceil(idx/interval_flat);
    flat_idx_pct = 1-rem(idx-1,interval_flat)/interval_flat;

    flat = flat_idx_pct*flats(:,:,flat_idx) + (1-flat_idx_pct)*flats(:,:,flat_idx+1);
    
    corrected = sample./flat;
    corrected = imcrop(corrected,rect);
    corrected = flipud(corrected);
    
    corrected = remove_hot_pixels(corrected,1);

    corrected(BP_map == 255) = NaN;
    corrected(corrected == -Inf) = NaN;
    corrected(corrected == Inf) = NaN;
    
    corrected = fillmissing(corrected,'linear');
    
    % phase = tie_hom(corrected, E, R1, R2, gamma, px);
    phase = corrected;

    phase = circshift(phase,jitter_vec_px(idx),2); %%%%%

    shift_y = interp1(ref_positions, trany, idx);
    shift_x = interp1(ref_positions, tranx, idx);
    translationMatrix = eye(3);
    translationMatrix([3,6]) = [shift_x,shift_y];
    tform = affine2d(translationMatrix);
    outputView = imref2d(size(phase)); % Define output view
    warped = imwarp(phase, tform, 'OutputView', outputView);

    im_name = strcat('proj', num2str(idx), '.tif');
    fname = strcat(outFolder,im_name);
    imwrite2tif(warped, [], fname, 'single');

end

% End Proj
im_name = strcat('Im_', num2str(exp), 'sec_proj_end.raw');
fname = strcat(inFolder,im_name);
sample = double(loadRawImage(fname));
sample = dark-sample;
corrected = sample./flat_end;
corrected = imcrop(corrected,rect);
corrected = flipud(corrected);
corrected = fillmissing(corrected,'linear');
% phase = tie_hom(corrected, E, R1, R2, gamma, px);
phase = corrected;
phase = circshift(phase,jitter_vec_px(end),2);
scale_fact = (num_proj-num_proj/2)/num_proj;
drift_y = trany(end);
drift_x = tranx(end);
shift_y = scale_fact*drift_y;
shift_x = scale_fact*drift_x;
translationMatrix = eye(3);
translationMatrix([3,6]) = [shift_x,shift_y];
tform = affine2d(translationMatrix);
outputView = imref2d(size(phase)); % Define output view
warped = imwarp(phase, tform, 'OutputView', outputView);
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