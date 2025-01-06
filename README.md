# WEBSITE SCRAPER, LINK EXTRACTER, VIDEO/STREAM DOWNLOADER

## Overview

This project is a simple toolkit designed for web scraping, link extraction, and media downloading. It includes various utilities to crawl websites, extract site maps, clean and deduplicate links, and download media files like videos. The scripts are modular and can be customized for different web automation and scraping tasks.

## Features

- **Website Crawling and Link Extraction**: Crawl websites to gather all accessible links and store them in a sitemap.
- **Sitemap Cleanup**: Filter out unwanted links and retain only secure (`https`) links.
- **Duplicate Removal**: Identify and remove duplicate files in a specified folder.
- **Media Download**: Extract and download video files from a list of URLs or directly from embedded links on web pages.

## Prerequisites

- Python 3.8+
- Google Chrome installed
- ChromeDriver compatible with your Chrome version
- [Selenium](https://pypi.org/project/selenium/)
- [BeautifulSoup](https://pypi.org/project/beautifulsoup4/)
- [Requests](https://pypi.org/project/requests/)
- [WebDriver Manager](https://pypi.org/project/webdriver-manager/)
- [FFmpeg](https://ffmpeg.org/) (for media file downloads)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/website-scraping-toolkit.git
   cd website-scraping-toolkit
   ```

2. Install required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Ensure FFmpeg is installed and added to your system's PATH.

## Usage

### 1. Website Crawling

To crawl a website and generate a sitemap:

```bash
python grab_every_link_on_a_site.py
```

Follow the prompts to input the starting URL and other preferences.

### 2. Sitemap Cleanup

To clean up the generated sitemap and retain only `https` links:

```bash
python clean_up_site_map.py
```

### 3. Remove Duplicate Files

To find and remove duplicate media files in the current directory:

```bash
python remove_duplicates.py
```

### 4. Download Media Files

To extract and download media files (e.g., `.m3u8`, `.ts`) from links in the sitemap:

```bash
python download_videos.py
```

Ensure that `site_map.txt` contains valid URLs.

## File Descriptions

- **grab_every_link_on_a_site.py**: Crawls websites to gather links and generate a sitemap.
- **make_sitemap.py**: A simpler version of the crawler to build sitemaps.
- **clean_up_site_map.py**: Filters the sitemap to include only `https` links.
- **remove_duplicates.py**: Identifies and deletes duplicate files based on their hash values.
- **download_videos.py**: Downloads media files from extracted links using Selenium and FFmpeg.

## Notes

- Some scripts require dynamic content to load fully. Adjust the sleep timers as needed for your use case.
- Media downloading requires FFmpeg for `.m3u8` and `.ts` file support.
- Ensure compliance with website terms of service and copyright laws when scraping.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for new features or bug fixes.

## License

This project is licensed under the [MIT License](LICENSE).
