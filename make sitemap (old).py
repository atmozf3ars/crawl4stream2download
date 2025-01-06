import os
import time
from collections import deque
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.common.by import By

def crawl_website(start_url, domain, max_tabs=15, batch_size=250, output_file="site_map.txt"):
    """
    Crawl all pages within `domain`, starting from `start_url`.
    - Uses a permanent main tab to preserve session.
    - Opens new tabs in batches (up to `max_tabs`) for parallel-ish loading.
    - Writes links to the output file every `batch_size` links.
    """
    options = webdriver.ChromeOptions()

    # Use a generic user data directory path for any Windows user
    user_data_dir = os.path.expanduser("~/AppData/Local/Google/Chrome/User Data")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--profile-directory=Default")
    driver = webdriver.Chrome(options=options)

    visited = set()
    queue = deque([start_url])
    links_buffer = []  # Buffer to store links before writing

    driver.get("about:blank")
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
            if url in visited:
                print(f"[DEBUG] Already visited, skipping: {url}")
                continue

            visited.add(url)
            print(f"[DEBUG] Opening new tab for: {url}")
            driver.execute_script(f"window.open('{url}','_blank');")
            new_tab_handles.append(driver.window_handles[-1])

        time.sleep(5)

        for handle in new_tab_handles:
            if handle in driver.window_handles:
                driver.switch_to.window(handle)
            else:
                print("[DEBUG] Tab was closed unexpectedly.")
                continue

            current_url = driver.current_url
            print(f"[DEBUG] Currently crawling: {current_url}")

            try:
                time.sleep(1)
                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href")
                    if not href:
                        continue

                    absolute_link = urljoin(current_url, href)
                    parsed = urlparse(absolute_link)

                    # Skip logout links or similar
                    if any(keyword in absolute_link.lower() for keyword in ["logout", "logoff", "signout"]):
                        print(f"[DEBUG] Skipping logout-related link: {absolute_link}")
                        continue

                    if (parsed.netloc == domain
                            and absolute_link not in visited):
                        print(f"[DEBUG] Found new link: {absolute_link}")
                        queue.append(absolute_link)
                        links_buffer.append(absolute_link)

                        if len(links_buffer) >= batch_size:
                            _write_links_to_file(links_buffer, output_file)
                            links_buffer.clear()

            except Exception as e:
                print(f"[ERROR] Error accessing {current_url}: {e}")

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
    return visited

def _write_links_to_file(links_list, filename):
    """
    Append the given list of links to the specified text file.
    """
    with open(filename, "a", encoding="utf-8") as f:
        for link in links_list:
            f.write(link + "\n")
    print(f"[DEBUG] Wrote {len(links_list)} links to {filename}")

if __name__ == "__main__":
    domain = input("Enter the domain to crawl (e.g., example.com): ").strip()
    start_url = f"{domain}/"

    MAX_TABS = 10
    BATCH_SIZE = 250
    OUTPUT_FILE = "site_map.txt"

    print("[DEBUG] Starting crawl...")
    all_links = crawl_website(start_url, domain, max_tabs=MAX_TABS, batch_size=BATCH_SIZE, output_file=OUTPUT_FILE)

    print(f"[DEBUG] Crawl completed. {len(all_links)} unique URLs found.")
