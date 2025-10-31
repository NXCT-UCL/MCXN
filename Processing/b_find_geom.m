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

method = 'reg'; %'xcorr' or 'reg'
max_sft = 65; %

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

switch method
    case 'xcorr'
        
        %%%%%
        fixedImage = medfilt2(im00);
        movingImage = medfilt2(im10);
        movingImage = circshift(movingImage,round(guess_dx),2);
        
        edge_px = round(abs(guess_dx))+2;
        fixedImage = fixedImage(edge_px:end-edge_px, edge_px:end-edge_px);
        movingImage = movingImage(edge_px:end-edge_px, edge_px:end-edge_px);
        
        [xmap,p] = calc_limited_xcorr_1d(fixedImage,movingImage, max_sft);
        
        x_vec = -max_sft:max_sft;
        x_trans = interp1(1:(2*max_sft+1),x_vec,p);
        tform = transltform2d([1,0,-x_trans;0,1,0;0,0,1]);
        registeredImage = imwarp(movingImage, tform, 'OutputView', imref2d(size(movingImage)));
        
        figure;
        imshowpair(fixedImage,registeredImage);
        
        dpx_M1 = abs(round(guess_dx)-x_trans);
        
        %%%%%
        fixedImage = medfilt2(im01);
        movingImage = medfilt2(im11);
        movingImage = circshift(movingImage,round(guess_dx),2);
        
        edge_px = round(abs(guess_dx))+2;
        fixedImage = fixedImage(edge_px:end-edge_px, edge_px:end-edge_px);
        movingImage = movingImage(edge_px:end-edge_px, edge_px:end-edge_px);
        
        [xmap,p] = calc_limited_xcorr_1d(fixedImage,movingImage, max_sft);
        
        x_vec = -max_sft:max_sft;
        x_trans = interp1(1:(2*max_sft+1),x_vec,p);
        tform = transltform2d([1,0,-x_trans;0,1,0;0,0,1]);
        registeredImage = imwarp(movingImage, tform, 'OutputView', imref2d(size(movingImage)));
        
        figure;
        imshowpair(fixedImage,registeredImage);
        
        dpx_M2 = abs(round(guess_dx)-x_trans);

    case 'reg'

        %%%%%
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
        
        %%%%%
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
end

%%

% Manually define pixel movement
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

%%
function peak = subpixel_quadratic_min_1d(cost_vec)
    % Refine the integer minimum of a 1D cost map to subpixel precision
    % using a quadratic fit around the 3-point neighborhood.

    [~, x0] = min(cost_vec);

    % Edge case: can't refine if on the border
    if x0 == 1 || x0 == length(cost_vec)
        peak = x0;
        return;
    end

    % Values around the minimum
    f_minus = cost_vec(x0-1);
    f0 = cost_vec(x0);
    f_plus = cost_vec(x0+1);

    % Fit parabola: f(x) = a*x^2 + b*x + c
    % Using offsets [-1,0,1]
    A = [1 -1 1;
         0  0 1;
         1  1 1];
    y = [f_minus; f0; f_plus];
    coeffs = A \ y;

    a = coeffs(1);
    b = coeffs(2);

    % Subpixel offset relative to x0
    if abs(2*a) > 1e-12
        dx = -b / (2*a);
    else
        dx = 0;
    end

    % Limit refinement to max 1 pixel
    if abs(dx) > 1
        dx = sign(dx);
    end

    peak = x0 + dx;
end


function [xcorr_vec, peak] = calc_limited_xcorr_1d(im1, im2, max_shift)
    % Using cross correlation (actually SSD here) to find horizontal shift
    % between two images, limited to +/- max_shift pixels.
    % im1, im2: same size images
    
    % normalise images
    im1 = im1 - mean(im1(:));
    im1 = im1 ./ max(im1(:));
    im2 = im2 - mean(im2(:));
    im2 = im2 ./ max(im2(:));

    xcorr_vec = zeros(1, 2*max_shift+1);

    % Loop over horizontal shifts only
    for x = -max_shift:max_shift
        % Translate im1 horizontally by x pixels
        im_t = imtranslate(im1, [x, 0], 'FillValues', 0);
        
        % Compute mean squared error
        diff = im_t - im2;
        diff = diff(2*max_shift+1:end-2*max_shift, 2*max_shift+1:end-2*max_shift);
        xcorr_vec(x + max_shift + 1) = mean(diff(:).^2);
    end

    % Subpixel refinement (1D quadratic)
    peak = subpixel_quadratic_min_1d(xcorr_vec);
end
