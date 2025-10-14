function out = bin_stack(stack, bin, method)
% BIN_STACK  Bin a 2D or 3D array by integer factors.
%   out = BIN_STACK(stack, [bx,by])        % works for 2D -> returns 2D
%   out = BIN_STACK(stack, [bx,by,bz])     % works for 3D -> returns 3D
%   out = BIN_STACK(..., 'median')         % optional: use 'median' instead of 'mean'
%
% Notes:
% - Dimensions are cropped to the largest multiple of the bin factor.
% - 'mean' (default) uses averaging, 'median' uses median pooling.

    if nargin < 3 || isempty(method), method = 'mean'; end
    method = lower(method);
    bin = bin(:).';                 % row vector
    if numel(bin) < 3
        bin = [bin ones(1,3-numel(bin))];  % pad missing bin dims with 1
    end
    bx = bin(1); by = bin(2); bz = bin(3);
    if any([bx,by,bz] < 1) || any(mod([bx,by,bz],1) ~= 0)
        error('Bin factors must be positive integers.');
    end

    % Handle 2D case gracefully
    if ndims(stack) < 3
        stack = reshape(stack, size(stack,1), size(stack,2), 1);
        was2D = true;
    else
        was2D = false;
    end

    % Crop to integer multiples
    [nx, ny, nz] = size(stack);
    nx2 = floor(nx/bx)*bx;
    ny2 = floor(ny/by)*by;
    nz2 = floor(nz/bz)*bz;
    stack = stack(1:nx2, 1:ny2, 1:nz2);

    % Reshape into bin blocks
    stack = reshape(stack, bx, nx2/bx, by, ny2/by, bz, nz2/bz);

    % Apply binning method
    switch method
        case 'mean'
            out = squeeze(mean(mean(mean(stack,1),3),5));

        case 'median'
            % Median over each block — a bit slower but robust
            % Flatten block dimensions first
            out = squeeze(median(reshape(stack, [], nx2/bx, ny2/by, nz2/bz), 1));

        otherwise
            error('Unknown method "%s". Use "mean" or "median".', method);
    end

    % Restore dimensionality for 2D inputs
    if was2D
        out = reshape(out, size(out,1), size(out,2));
    end
end
