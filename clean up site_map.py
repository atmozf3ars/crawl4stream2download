def keep_only_https_lines(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Filter out lines that don't contain 'https://'
    filtered_lines = [line for line in lines if 'https://' in line]
    
    # Write the remaining lines back to the file
    with open(file_path, 'w') as file:
        file.writelines(filtered_lines)

# Specify the path to your file
file_path = 'site_map.txt'
keep_only_https_lines(file_path)
