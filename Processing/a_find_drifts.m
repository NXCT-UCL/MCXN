clear;

sampleFolder = '..\';
inFolder = strcat(sampleFolder, 'data\');
refFolder = strcat(sampleFolder, 'pre_scan\');

param_file = strcat(sampleFolder,'scan_parameters.txt');

exp = num2str(read_param('exp',param_file));
num_proj = read_param('num_proj ',param_file);
ang_range = read_param('rotation_angle',param_file);
extra_proj = read_param('extra_proj',param_file);

detector = 'moment';

ref_step = 20; %degrees
num_refs = ang_range/ref_step;

angles = linspace(0,ang_range,num_proj+1);
angles = angles(1:end-1);
ref_positions = find(~rem(angles,ref_step));

jitter_flag = 1;

switch detector
    case 'moment'
        ly = 2048;
        lx = 2048;
        px = 4.5e-3;
        rect = [305,305,1439,1439];
        flip = 1;
        jitter_dir = -1;

    case 'primeBSI'
        ly = 1314;
        lx = 1314;
        px = 27.9e-3;
        rect = [200,200,917,917];
        flip = 0;
        jitter_dir = 1;
end

% boundary addition
rect = rect + [50,50,-100,-100];

%%

if jitter_flag
    jitter_vec = readmatrix(strcat(sampleFolder,'jitter.txt')); %%%%
    jitter_vec_px = jitter_dir*round(jitter_vec/px); %%%%
    jitter_vec_px(end) = 0;
else
    jitter_vec_px = zeros(1,num_proj);
end

%% Load flat and darks

dark_names = dir([inFolder,'Dark*']);
numDarks = length(dark_names);
darks = zeros(ly,lx,numDarks);
for idx = 1:numDarks
    fname = strcat(inFolder,dark_names(1).name);
    darks(:,:,idx) = double(imread(fname));
end
dark = mean(darks,3);

flat_names = dir([inFolder,'flat*']);
numFlats = length(flat_names);
flats = zeros(ly,lx,numFlats);
for idx = 1:numFlats
    fname = strcat(inFolder,flat_names(1).name);
    flats(:,:,idx) = double(imread(fname));
end
flat = mean(flats,3);

%% Load all images - only the first frame of the full scan 

ref_images = zeros(lx,ly,num_refs);
mov_images = zeros(lx,ly,num_refs);

for idx = 1:num_refs
    
    angle = (idx-1)*ref_step;
    im_name = strcat('Im_', num2str(angle), '.tiff');
    fname = strcat(refFolder, im_name);
    ref_images(:,:,idx) = double(imread(fname));

    proj_nm = ref_positions(idx);
    im_name = strcat('Im_proj',num2str(proj_nm-1), '.tiff');
    fname = strcat(inFolder, im_name);
    mov_images(:,:,idx) = double(imread(fname));

end


%%
ref_images = (-ref_images+dark)./(dark-flat);
mov_images = (-mov_images+dark)./(dark-flat);

ref_images = fillmissing(ref_images,'linear');
mov_images = fillmissing(mov_images,'linear');

if flip 
    ref_images = flipud(ref_images);
    mov_images = flipud(mov_images);
end

%% jitter

for idx = 1:num_refs
    
    proj_nm = ref_positions(idx);
    mov_images(:,:,idx) = circshift(mov_images(:,:,idx),jitter_vec_px(proj_nm),2); %%%%%

end

%%

tranx = zeros(1,num_refs);
trany = zeros(1,num_refs);

parfor idx = 1:num_refs

    % Read the reference and target images
    fixedImage = ref_images(:,:,idx);   % Reference image
    movingImage = mov_images(:,:,idx); % Image to be registered

    fixedImage = imcrop(fixedImage,rect);
    movingImage = imcrop(movingImage,rect);
    
    % rm outliers
    fixedImage(fixedImage == -Inf) = 1;
    fixedImage(fixedImage == Inf) = 1;
    movingImage(movingImage == -Inf) = 1;
    movingImage(movingImage == Inf) = 1;

    % match histogram
    % movingImage = imhistmatch(movingImage, fixedImage);
    
    % Apply Gaussian blur to both images
    fixedImageBlurred = imgaussfilt(fixedImage, 8);
    movingImageBlurred = imgaussfilt(movingImage, 8);
    
    % Define the optimizer and metric for the registration process
    [optimizer, metric] = imregconfig('monomodal');
    optimizer.MaximumStepLength = 2.250000e-03;
    
    % Perform the registration using translation transformation on blurred images
    tform = imregtform(movingImageBlurred, fixedImageBlurred, 'translation', optimizer, metric);
    
    % Apply the transformation to the original moving image
    registeredImage = imwarp(movingImage, tform, 'OutputView', imref2d(size(fixedImage)));
    
    % % Display the results
    % figure;
    % imshow(fixedImageBlurred);
    % title('Fixed Image');
    % 
    % figure;
    % imshow(registeredImage);
    % title('Registered Image');


    translationY = tform.T(3,2);
    translationX = tform.T(3,1);
    fprintf('Translation in X direction: %.2f pixels\n', translationX);
    fprintf('Translation in Y direction: %.2f pixels\n', translationY);

    tranx(idx) = translationX;
    trany(idx) = translationY;
    
    % waitforbuttonpress;
end

%% end

if extra_proj

im_name = strcat('Im_proj_end.tiff');
fname = strcat(inFolder, im_name);
proj_end = double(imread(fname));

proj_end = (-proj_end+dark)./(dark-flat);

proj_end = fillmissing(proj_end,'linear');

if flip 
    proj_end = flipud(proj_end);
end

proj_end = circshift(proj_end,jitter_vec_px(end),2);

% Read the reference and target images
fixedImage = ref_images(:,:,1);   % Reference image
movingImage = proj_end; % Image to be registered

fixedImage = imcrop(fixedImage,rect);
movingImage = imcrop(movingImage,rect);

% rm outliers
fixedImage(fixedImage == -Inf) = 1;
fixedImage(fixedImage == Inf) = 1;
movingImage(movingImage == -Inf) = 1;
movingImage(movingImage == Inf) = 1;

% match histogram
% movingImage = imhistmatch(movingImage, fixedImage);

% Apply Gaussian blur to both images
fixedImageBlurred = imgaussfilt(fixedImage, 8);
movingImageBlurred = imgaussfilt(movingImage, 8);

% Define the optimizer and metric for the registration process
[optimizer, metric] = imregconfig('monomodal');
optimizer.MaximumStepLength = 2.250000e-03;

% Perform the registration using translation transformation on blurred images
tform = imregtform(movingImageBlurred, fixedImageBlurred, 'translation', optimizer, metric);

% Apply the transformation to the original moving image
registeredImage = imwarp(movingImageBlurred, tform, 'OutputView', imref2d(size(fixedImage)));

% Display the results
figure;
imshow(fixedImageBlurred);
title('Fixed Image');

figure;
imshow(registeredImage);
title('Registered Image');

%
translationY = tform.T(3,2);
translationX = tform.T(3,1);
fprintf('Translation in X direction: %.2f pixels\n', translationX);
fprintf('Translation in Y direction: %.2f pixels\n', translationY);

tranx(end+1) = translationX;
trany(end+1) = translationY;

end

%%
figure;
plot([angles(ref_positions),360], tranx, 'DisplayName', 'Horizontal');
hold on;
plot([angles(ref_positions),360], trany, 'DisplayName', 'Vertical');
grid on; legend('Show');
ylabel('Drift (px)');
xlabel('Angle (deg)');

save shifts.mat tranx trany