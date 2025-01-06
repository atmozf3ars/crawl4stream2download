import os
import time
import sys
from collections import deque
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from tkinter import Tk, messagebox

import logging
logging.basicConfig(level=logging.CRITICAL)
logging.getLogger('tensorflow').setLevel(logging.CRITICAL)
logging.getLogger('selenium').setLevel(logging.CRITICAL)

def validate_url(url):
    """Ensure the URL is well-formed and includes a protocol."""
    if not urlparse(url).scheme:
        url = "http://" + url
    return url

def crawl_website(start_url, domain, crawl_only_domain, max_tabs=15, batch_size=250, output_file="site_map.txt"):
    """
    Crawl all pages starting from `start_url`, with an option to limit crawling to the domain.
    - Uses a permanent main tab to preserve session.
    - Opens new tabs in batches (up to `max_tabs`) for parallel-ish loading.
    - Writes links to the output file every `batch_size` links.
    """
    options = webdriver.ChromeOptions()

    # Use a generic user data directory path for any Windows user
    user_data_dir = os.path.expanduser("~/AppData/Local/Google/Chrome/User Data")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-application-cache")
    options.page_load_strategy = 'eager'

    try:
        driver = webdriver.Chrome(options=options)
    except WebDriverException as e:
        print(f"[ERROR] Could not initialize WebDriver: {e}")
        return 0

    visited = set()
    queue = deque([start_url])
    links_buffer = []  # Buffer to store links before writing

    try:
        driver.get(start_url)
    except WebDriverException as e:
        print(f"[ERROR] Could not load start URL: {e}")
        driver.quit()
        return 0

    main_window = driver.current_window_handle

    while queue:
        urls_this_round = []
        for _ in range(max_tabs):
            if not queue:
                break
            url = queue.popleft()
            urls_this_round.append(url)

        new_tab_handles = []
        for url in urls_this_round:
            try:
                print(f"[DEBUG] Opening new tab for: {url}")
                driver.execute_script(f"window.open('{url}','_blank');")
                new_tab_handles.append(driver.window_handles[-1])
            except WebDriverException as e:
                print(f"[ERROR] Could not open new tab for {url}: {e}")
                continue

        time.sleep(2)

        for handle in new_tab_handles:
            if handle in driver.window_handles:
                driver.switch_to.window(handle)
            else:
                print("[DEBUG] Tab was closed unexpectedly.")
                continue

            current_url = driver.current_url
            print(f"[DEBUG] Currently crawling: {current_url}")

            try:
                time.sleep(3)  # Wait for dynamic content to load
                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href")
                    if not href:
                        continue

                    absolute_link = urljoin(current_url, href)
                    parsed = urlparse(absolute_link)

                    # Allow only HTTP and HTTPS protocols to be visited
                    if parsed.scheme not in ["http", "https"]:
                        print(f"[DEBUG] Logging unsupported protocol link: {absolute_link}")
                        links_buffer.append(absolute_link)
                        continue

                    # Skip logout links or similar
                    if any(keyword in absolute_link.lower() for keyword in ["logout", "logoff", "signout"]):
                        print(f"[DEBUG] Skipping logout-related link: {absolute_link}")
                        continue

                    # Respect the domain-only crawling preference
                    if crawl_only_domain and parsed.netloc != domain:
                        print(f"[DEBUG] Skipping external link: {absolute_link}")
                        continue

                    if absolute_link not in visited:
                        print(f"[DEBUG] Found new link: {absolute_link}")
                        queue.append(absolute_link)
                        links_buffer.append(absolute_link)

                visited.add(current_url)  # Mark as visited only after processing

                if len(links_buffer) >= batch_size:
                    _write_links_to_file(links_buffer, output_file)
                    links_buffer.clear()

            except NoSuchElementException as e:
                print(f"[ERROR] Could not find links on {current_url}: {e}")
            except WebDriverException as e:
                print(f"[ERROR] Error during crawling: {e}")

        for handle in new_tab_handles:
            if handle in driver.window_handles:
                driver.switch_to.window(handle)
                driver.close()

        if main_window in driver.window_handles:
            driver.switch_to.window(main_window)
        else:
            print("[WARNING] Main tab was closed; ending session to avoid logout.")
            break

    if links_buffer:
        _write_links_to_file(links_buffer, output_file)
        links_buffer.clear()

    driver.quit()
    return len(visited)

def _write_links_to_file(links_list, filename):
    """
    Append the given list of links to the specified text file.
    """
    with open(filename, "a", encoding="utf-8") as f:
        for link in links_list:
            f.write(link + "\n")
    print(f"[DEBUG] Wrote {len(links_list)} links to {filename}")

if __name__ == "__main__":
    start_url = input("Enter the starting URL to crawl (e.g., https://example.com): ").strip()
    start_url = validate_url(start_url)
    domain = urlparse(start_url).netloc

    crawl_only_domain = input("Do you want to crawl within the domain only? (Y/N): ").strip().lower() == 'y'

    MAX_TABS = 10
    BATCH_SIZE = 100
    OUTPUT_FILE = f"{domain}.txt"

    print("[DEBUG] Starting crawl...")
    total_links = crawl_website(start_url, domain, crawl_only_domain, max_tabs=MAX_TABS, batch_size=BATCH_SIZE, output_file=OUTPUT_FILE)

    print(f"[DEBUG] Crawl completed. {total_links} unique URLs found.")
pause
