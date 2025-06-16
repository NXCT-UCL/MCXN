clear;

sampleFolder = 'D:\25_04_07\8_MuscleGFPD9_40kv_1p2um\';
inFolder = strcat(sampleFolder, 'data\');
refFolder = strcat(sampleFolder, 'pre_scan\');

exp = '3';
numFr = 64;
ly = 4096;
lx = 4096;
px = 8e-3;

ref_step = 9; %degrees
num_proj = 4000;
ang_range = 360;
num_refs = ang_range/ref_step;

angles = linspace(0,ang_range,num_proj+1);
angles = angles(1:end-1);
ref_positions = find(~rem(angles,ref_step));

%%

jitter_vec = readmatrix(strcat(sampleFolder,'jitter.txt')); %%%%
jitter_vec_px = jitter_vec/px; %%%%

%% Load flat and darks

dark_names = dir([inFolder,'Dark*']);
numDarks = length(dark_names);
darks = zeros(ly,lx,numDarks);
for idx = 1:numDarks
    fname = strcat(inFolder,dark_names(1).name);
    darks(:,:,idx) = double(loadRawImage(fname));
end
dark = mean(darks,3);

flat_names = dir([inFolder,'flat*']);
numFlats = length(flat_names);
flats = zeros(ly,lx,numFlats);
for idx = 1:numFlats
    fname = strcat(inFolder,flat_names(1).name);
    flats(:,:,idx) = double(loadRawImage(fname));
end
flat = mean(flats,3);

%%

ref_images = zeros(lx,ly,num_refs);
mov_images = zeros(lx,ly,num_refs);

for idx = 1:num_refs
    
    angle = (idx-1)*ref_step;
    im_name = strcat('Im_', num2str(angle), '.raw');
    fname = strcat(refFolder, im_name);
    ref_images(:,:,idx) = double(loadRawImage(fname));

    proj_nm = ref_positions(idx);
    im_name = strcat('Im_', num2str(exp), 'sec_proj',num2str(proj_nm-1), '.raw');
    fname = strcat(inFolder, im_name);
    mov_images(:,:,idx) = double(loadRawImage(fname));

end


%%
ref_images = (-ref_images+dark)./(dark-flat);
mov_images = (-mov_images+dark)./(dark-flat);

ref_images = fillmissing(ref_images,'linear');
mov_images = fillmissing(mov_images,'linear');

ref_images = flipud(ref_images);
mov_images = flipud(mov_images);

%% jitter

for idx = 1:num_refs
    
    proj_nm = ref_positions(idx);
    mov_images(:,:,idx) = circshift(mov_images(:,:,idx),jitter_vec_px(proj_nm),2); %%%%%

end

%% start and end

im_name = strcat('Im_', num2str(exp), 'sec_proj0.raw');
fname = strcat(inFolder, im_name);
proj_start = double(loadRawImage(fname));

im_name = strcat('Im_', num2str(exp), 'sec_proj_end.raw');
fname = strcat(inFolder, im_name);
proj_end = double(loadRawImage(fname));

proj_start = (-proj_start+dark)./(dark-flat);
proj_end = (-proj_end+dark)./(dark-flat);

proj_start = fillmissing(proj_start,'linear');
proj_end = fillmissing(proj_end,'linear');

proj_start = flipud(proj_start);
proj_end = flipud(proj_end);

proj_start = circshift(proj_start,jitter_vec_px(1),2);
proj_end = circshift(proj_end,jitter_vec_px(end),2);

%%

tranx = zeros(1,num_refs);
trany = zeros(1,num_refs);

parfor idx = 1:num_refs

    % Read the reference and target images
    fixedImage = ref_images(:,:,idx);   % Reference image
    movingImage = mov_images(:,:,idx); % Image to be registered
    
    % rm outliers
    fixedImage(fixedImage == -Inf) = 1;
    fixedImage(fixedImage == Inf) = 1;
    movingImage(movingImage == -Inf) = 1;
    movingImage(movingImage == Inf) = 1;

    % match histogram
    movingImage = imhistmatch(movingImage, fixedImage);
    
    % Apply Gaussian blur to both images
    fixedImageBlurred = imgaussfilt(fixedImage, 2);
    movingImageBlurred = imgaussfilt(movingImage, 2);
    
    % Define the optimizer and metric for the registration process
    [optimizer, metric] = imregconfig('monomodal');
    
    % Perform the registration using translation transformation on blurred images
    tform = imregtform(movingImageBlurred, fixedImageBlurred, 'translation', optimizer, metric);
    
    % Apply the transformation to the original moving image
    registeredImage = imwarp(movingImage, tform, 'OutputView', imref2d(size(fixedImage)));
    
    % % Display the results
    % figure;
    % imshow(fixedImage);
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
%%
% Read the reference and target images
fixedImage = proj_start;   % Reference image
movingImage = proj_end; % Image to be registered

% rm outliers
fixedImage(fixedImage == -Inf) = 1;
fixedImage(fixedImage == Inf) = 1;
movingImage(movingImage == -Inf) = 1;
movingImage(movingImage == Inf) = 1;

% match histogram
movingImage = imhistmatch(movingImage, fixedImage);

% Apply Gaussian blur to both images
fixedImageBlurred = imgaussfilt(fixedImage, 2);
movingImageBlurred = imgaussfilt(movingImage, 2);

% Define the optimizer and metric for the registration process
[optimizer, metric] = imregconfig('monomodal');

% Perform the registration using translation transformation on blurred images
tform = imregtform(movingImageBlurred, fixedImageBlurred, 'translation', optimizer, metric);

% Apply the transformation to the original moving image
registeredImage = imwarp(movingImage, tform, 'OutputView', imref2d(size(fixedImage)));

% Display the results
figure;
imshow(fixedImage);
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
%%
figure;
plot([angles(ref_positions),360], tranx, 'DisplayName', 'Horizontal');
hold on;
plot([angles(ref_positions),360], trany, 'DisplayName', 'Vertical');
grid on; legend('Show');
ylabel('Drift (px)');
xlabel('Angle (deg)');

save shifts.mat tranx trany