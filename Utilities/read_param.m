function value = read_param(paramName, filePath)
% READ_PARAM  Reads a parameter value from a scan_parameters.txt file.
%   value = READ_PARAM(paramName, filePath) reads the specified parameter 
%   from the given text file. The function ignores comments starting with '#'.

    % Open file
    fid = fopen(filePath, 'r');
    if fid == -1
        error('Could not open file: %s', filePath);
    end

    value = []; % Default if not found

    % Read line-by-line
    while ~feof(fid)
        line = strtrim(fgetl(fid));
        % Skip empty lines and comment lines
        if isempty(line) || startsWith(line, '#')
            continue;
        end
        % Check if the line starts with the param name
        if startsWith(line, paramName)
            tokens = regexp(line, '=', 'split');
            if numel(tokens) < 2
                fclose(fid);
                error('Malformed line for parameter "%s".', paramName);
            end
            valueStr = strtrim(tokens{2});
            % Remove trailing comments
            valueStr = regexprep(valueStr, '#.*', '');
            % Try converting to number, if possible
            numericVal = str2double(valueStr);
            if isnan(numericVal)
                value = strtrim(valueStr); % Return as string
            else
                value = numericVal; % Return as number
            end
            break;
        end
    end

    fclose(fid);

    % If not found
    if isempty(value)
        error('Parameter "%s" not found in file: %s', paramName, filePath);
    end
end
