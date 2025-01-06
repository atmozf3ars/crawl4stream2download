import os
import re
import time
import random
import hashlib
import requests
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import InvalidSessionIdException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def setup_selenium_with_existing_session():
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=C:/Users/Administrator/AppData/Local/Google/Chrome/User Data")
    options.add_argument("--profile-directory=Default")

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-application-cache")
    options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def extract_hyperlinks(file_name="site_map.txt"):
    hyperlinks = []
    try:
        with open(file_name, "r") as file:
            for line in file.readlines():
                link = line.strip()
                if link.startswith("http"):
                    hyperlinks.append(link)
    except Exception as e:
        print(f"Error reading site map: {e}")
    return hyperlinks

def find_media_links_with_selenium(driver, url, output_dir, temp_dir):
    media_links = []
    try:
        driver.get(url)
        time.sleep(5)  # Wait for the page to load
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Find all video links on the page
        for tag in soup.find_all("a", href=True):
            link = urljoin(url, tag["href"])
            if link.endswith(".m3u8") or link.endswith(".ts"):
                media_links.append(link)

        # Scan the source code for embedded video links
        for line in page_source.splitlines():
            if ".m3u8" in line or ".ts" in line:
                start = line.find("http")
                end = line.find(".m3u8") + 5 if ".m3u8" in line else line.find(".ts") + 3
                media_links.append(line[start:end])

        # Process all detected media links
        if media_links:
            print(f"Found {len(media_links)} media links on {url}.")
            for link in set(media_links):
                process_media_link(link, output_dir, temp_dir, url)
        else:
            print(f"No media links found on {url}.")

    except Exception as e:
        print(f"Error processing URL {url}: {e}")

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of a file."""
    hash_func = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
    except Exception as e:
        print(f"Error reading file for hash calculation: {e}")
        return None
    return hash_func.hexdigest()

def file_exists_by_hash(output_dir, temp_file_path):
    """Check if a file with the same hash already exists in the output directory."""
    new_file_hash = calculate_file_hash(temp_file_path)
    if not new_file_hash:
        return False

    for root, _, files in os.walk(output_dir):
        for file_name in files:
            existing_file_path = os.path.join(root, file_name)
            existing_file_hash = calculate_file_hash(existing_file_path)
            if existing_file_hash == new_file_hash:
                print(f"File with the same content already exists: {existing_file_path}")
                return True
    return False

def process_media_link(media_link, output_dir, temp_dir, original_url):
    parsed_url = urlparse(original_url)
    raw_name = f"{parsed_url.netloc}{parsed_url.path}"
    sanitized_name = re.sub(r'[\\/*?:"<>|]', '_', raw_name.strip("/"))

    if not sanitized_name:
        sanitized_name = "index"

    temp_file_path = os.path.normpath(os.path.join(temp_dir, f"temp_{sanitized_name}.mp4"))
    output_file = os.path.normpath(os.path.join(output_dir, sanitized_name + ".mp4"))

    if media_link.endswith(".m3u8"):
        download_m3u8(media_link, temp_file_path)
    elif media_link.endswith(".ts"):
        download_ts(media_link, temp_file_path)

    # Check if the temporary file was created
    if not os.path.exists(temp_file_path):
        print(f"Temporary file not found: {temp_file_path}. Skipping.")
        return

    # Check if the file already exists by hash
    if file_exists_by_hash(output_dir, temp_file_path):
        os.remove(temp_file_path)  # Clean up temporary file
        return

    # Rename the temporary file to final output name
    counter = 1
    unique_output_file = output_file
    while os.path.exists(unique_output_file):
        unique_output_file = os.path.normpath(os.path.join(output_dir, f"{sanitized_name}_{counter}.mp4"))
        counter += 1

    os.rename(temp_file_path, unique_output_file)
    print(f"Saved: {unique_output_file}")

def download_m3u8(link, output_file):
    command = [
        "C:/ffmpeg/bin/ffmpeg.exe",
        "-i", link,
        "-c:v", "copy",
        "-c:a", "aac",
        output_file
    ]
    try:
        print(f"Downloading {link} to {output_file} as MP4...")
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print(f"Saved: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to download {link}: {e.stderr.decode()}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")

def download_ts(link, output_file):
    try:
        print(f"Downloading {link} to {output_file}...")
        response = requests.get(link, stream=True, timeout=60)
        response.raise_for_status()
        with open(output_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        print(f"Saved: {output_file}")
    except Exception as e:
        print(f"Failed to download {link}: {e}")

def main():
    site_map_file = "site_map.txt"
    output_dir = os.path.normpath("I:/PROGRAMMING/MASTERCLASS/DOWNLOADS")
    temp_dir = os.path.normpath("I:/PROGRAMMING/MASTERCLASS/TEMP")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)

    links = extract_hyperlinks(site_map_file)
    print(f"Found {len(links)} links to process.")

    driver = None

    try:
        while links:
            try:
                # Restart driver if session becomes invalid
                if not driver or driver.session_id is None:
                    if driver:
                        driver.quit()
                    driver = setup_selenium_with_existing_session()

                # Pick a random link
                link = random.choice(links)
                links.remove(link)

                driver.get(link)
                time.sleep(3)  # Allow time for the page to load
                find_media_links_with_selenium(driver, driver.current_url, output_dir, temp_dir)
            except InvalidSessionIdException:
                print("Session invalid. Restarting driver.")
                if driver:
                    driver.quit()
                driver = setup_selenium_with_existing_session()
            except Exception as e:
                print(f"Error processing link {link}: {e}")
    except Exception as e:
        print(f"Critical error during processing: {e}")
    finally:
        if driver:
            driver.quit()
        print("Driver session ended. Cleanup complete.")

if __name__ == "__main__":
    main()
