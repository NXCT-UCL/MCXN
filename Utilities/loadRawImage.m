function imgData = loadRawImage(filename)
    % This function loads a 4096x4096, little-endian, 16-bit unsigned .raw image
    % Inputs:
    %   filename - the name of the .raw image file
    % Outputs:
    %   imgData - the image data as a 4096x4096 matrix

    % Open the raw file in binary read mode
    fid = fopen(filename, 'rb');

    % Check if file opened successfully
    if fid == -1
        error('Cannot open file: %s', filename);
    end

    % Read the data as 16-bit unsigned integers (uint16), little-endian format
    imgData = fread(fid, [4096, 4096], 'uint16', 0, 'ieee-le');

    % Close the file
    fclose(fid);
    
    imgData = imgData';
end
