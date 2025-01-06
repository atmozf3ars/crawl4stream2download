import os
import hashlib

def calculate_file_hash(file_path, chunk_size=8192):
    """Calculate the hash of a file using SHA-256."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)
    return sha256.hexdigest()

def find_duplicate_files():
    """Find duplicate files in the current folder based on their hash values."""
    file_hashes = {}
    duplicates = []

    current_folder = os.getcwd()

    for file_name in os.listdir(current_folder):
        if file_name.lower().endswith('.mp4'):
            file_path = os.path.join(current_folder, file_name)
            file_hash = calculate_file_hash(file_path)

            if file_hash in file_hashes:
                duplicates.append(file_path)
            else:
                file_hashes[file_hash] = file_path

    return duplicates

def remove_duplicates(duplicates):
    """Remove all duplicate files."""
    for duplicate in duplicates:
        try:
            os.remove(duplicate)
            print(f"Removed: {duplicate}")
        except Exception as e:
            print(f"Error removing {duplicate}: {e}")

if __name__ == "__main__":
    print("Scanning for duplicate files in the current folder...")
    duplicates = find_duplicate_files()

    if duplicates:
        print(f"Found {len(duplicates)} duplicate files.")
        remove_duplicates(duplicates)
    else:
        print("No duplicate files found.")
