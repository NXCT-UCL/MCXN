function im = tie_hom(im_in, E, R1, R2, gamma, px)
    % Inputs:
    % im_in: input image - flat field normalised 
    % E: energy in keV
    % R1: distance from source to sample (mm)
    % R2: distance from sample to detector (mm)
    % gamma: delta/beta ratio for homogeneous object
    % px: pixel size (mm)

    % convert energy (keV) to wavenumber (1/m)
    lambda = 12.398 / E;
    lambda = lambda * 1e-10;
    k = 2 * pi / lambda;

    % convert units to m
    px = px * 1e-3;
    R1 = R1 * 1e-3;
    R2 = R2 * 1e-3;

    % magnification
    M = (R1 + R2) / R1;

    % frequency space on sample plane
    px = px/M;

    % top of equation - FFT of I_norm
    imfft = fft2(im_in);
    imfft = fftshift(imfft);

    % create frequency grid
    [Y, X] = size(im_in);
    
    % Created K-space
    if X == 1
        kx = 0;
        ky = (-Y / 2 : Y / 2 - 1) * 2 * pi / (px * Y);
    elseif Y == 1
        kx = (-X / 2 : X / 2 - 1) * 2 * pi / (px * X);
        ky = 0;
    else
        kx = (-X / 2 : X / 2 - 1) * 2 * pi / (px * X);
        ky = (-Y / 2 : Y / 2 - 1) * 2 * pi / (px * Y);
    end

    [kx, ky] = meshgrid(kx, ky);
    kk = sqrt(kx.^2 + ky.^2);
    kk_sq = kk.^2;

    % Create filter
    filter = (kk_sq * R2 * gamma) / (2 * k  *M) + 1;

    % filter image as paganin equation
    im = ifftshift(imfft ./ filter);
    im = ifft2(im);

    im = abs(im);

    % Convert to phase
    im = -log(im) * gamma / (2);
end
