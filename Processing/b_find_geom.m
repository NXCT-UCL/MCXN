clear;

sampleFolder = '..\..\8_geom\';
flatFolder = '..\';

dx = 0.1;
dz = 1;
dx_str = num2str(dx);
dx_str(dx_str == '.') = 'p';
dz_str = num2str(dz);
dz_str(dz_str == '.') = 'p';

detector = 'moment';
Mag = 2; % rough guess

switch detector
    case 'moment'
        px = 4.5e-3;
        rect = [305,305,1439,1439];

    case 'primeBSI'
        px = 27.9e-3;
        rect = [200,200,917,917];
end

guess_dx = -dx/(px/Mag);

ff = dir([flatFolder,'data/*dark*']);
fname = strcat(flatFolder,'data\',ff(1).name);
dark = double(imread(fname));
dark = imcrop(dark,rect);

ff = dir([flatFolder,'data/*Flat*']);
fname = strcat(flatFolder,'data\',ff(2).name);
flat = double(imread(fname));
flat = imcrop(flat,rect);
flat = flat-dark;

fname = strcat(sampleFolder,'Im_Pos_x0_z0.tiff');
im00 = double(imread(fname));
im00 = imcrop(im00,rect);
im00 = (im00-dark)./flat;

fname = strcat(sampleFolder,'Im_Pos_x',dx_str,'_z0.tiff');
im10 = double(imread(fname));
im10 = imcrop(im10,rect);
im10 = (im10-dark)./flat;

fname = strcat(sampleFolder,'Im_Pos_x0_z',dz_str,'.tiff');
im01 = double(imread(fname));
im01 = imcrop(im01,rect);
im01 = (im01-dark)./flat;

fname = strcat(sampleFolder,'Im_Pos_x',dx_str,'_z',dz_str,'.tiff');
im11 = double(imread(fname));
im11 = imcrop(im11,rect);
im11 = (im11-dark)./flat;

%%

tform1 = transltform2d([1,0,guess_dx;0,1,0;0,0,1]);

fixedImage = im00;
movingImage = im10;

% Apply Gaussian blur to both images
fixedImageBlurred = imgaussfilt(fixedImage, 5);
movingImageBlurred = imgaussfilt(movingImage, 5);

% Define the optimizer and metric for the registration process
[optimizer, metric] = imregconfig('monomodal');

% Perform the registration using translation transformation on blurred images
tform = imregtform(movingImageBlurred, fixedImageBlurred, 'translation', optimizer, metric, InitialTransformation=tform1);

% Apply the transformation to the original moving image
registeredImage = imwarp(movingImage, tform, 'OutputView', imref2d(size(fixedImage)));

figure;
imshowpair(fixedImage,registeredImage);

dpx_M1 = abs(tform.A(7));

%%

tform1 = transltform2d([1,0,guess_dx;0,1,0;0,0,1]);

fixedImage = im01;
movingImage = im11;

% Apply Gaussian blur to both images
fixedImageBlurred = imgaussfilt(fixedImage, 5);
movingImageBlurred = imgaussfilt(movingImage, 5);

% Define the optimizer and metric for the registration process
[optimizer, metric] = imregconfig('monomodal');

% Perform the registration using translation transformation on blurred images
tform = imregtform(movingImageBlurred, fixedImageBlurred, 'translation', optimizer, metric, InitialTransformation=tform1);

% Apply the transformation to the original moving image
registeredImage = imwarp(movingImage, tform, 'OutputView', imref2d(size(fixedImage)));

figure;
imshowpair(fixedImage,registeredImage);

dpx_M2 = abs(tform.A(7));

%%

% dpx_M1 = 225;%%%%
% dpx_M2 = 123;%%%%

M1 = dpx_M1/dx*px;
M2 = dpx_M2/dx*px;

disp('Mag:');
disp(M1);
disp(M2);

Z_so = M2*dz/(M1-M2);
Z_sd = M1*Z_so;

disp('Z_so:');
disp(Z_so)
disp('Z_sd:');
disp(Z_sd);

%%

ang_left = 99.26;
ang_right = 83.02;

rot_phi_ang = ((90-abs(ang_left))+(90-abs(ang_right)))/2;
rot_phi = tand(rot_phi_ang);

disp('rot_phi:');
disp(rot_phi);