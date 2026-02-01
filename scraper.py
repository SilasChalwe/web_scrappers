import os
import time
import shutil
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# try package-relative imports, fall back to plain imports when running script directly
try:
    from .utils import construct_pdf_url, parse_card_soup
    from .db import init_db, save_to_db
    from .downloader import download_pdf
except Exception:
    from utils import construct_pdf_url, parse_card_soup
    from db import init_db, save_to_db
    from downloader import download_pdf

DEFAULT_GECKO = os.environ.get("GECKODRIVER_PATH")  # may be None

def _find_geckodriver(provided_path):
    if provided_path and os.path.isfile(provided_path):
        return provided_path
    found = shutil.which("geckodriver")
    if found and os.path.isfile(found):
        return found
    return None

def scrape_cards_from_source(page_source, label):
    soup = BeautifulSoup(page_source, 'html.parser')
    cards = soup.find_all('div', class_='card')
    results = []
    for card in cards:
        meta = parse_card_soup(card, label)
        meta["pdf_link"] = construct_pdf_url(meta["category"], meta["date"], meta["section"], meta["number"], meta["type"])
        results.append(meta)
    return results

def run_scraper(max_pages=5, headless=True, gecko_path=DEFAULT_GECKO, start_url="https://www.italgiure.giustizia.it/sncass/"):
    init_db()
    options = Options()
    if headless:
        options.add_argument("-headless")

    gecko_exec = _find_geckodriver(gecko_path)
    if not gecko_exec:
        raise RuntimeError("geckodriver not found. Install geckodriver or set GECKODRIVER_PATH to the executable path.")

    service = Service(executable_path=gecko_exec)
    driver = webdriver.Firefox(service=service, options=options)
    wait = WebDriverWait(driver, 30)

    try:
        driver.get(start_url)
        label = "CIVILE"
        print(f">>> STARTING SCRAPER: {label}")

        row_xpath = f"//div[@id='keylistContent[kind]']//tr[contains(., '{label}')]"
        filter_row = wait.until(EC.element_to_be_clickable((By.XPATH, row_xpath)))
        driver.execute_script("arguments[0].click();", filter_row)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card")))

        all_metadata = []
        page_num = 1
        while page_num <= max_pages:
            print(f"--- SCRAPING PAGE {page_num} ---")
            page_data = scrape_cards_from_source(driver.page_source, label)
            if not page_data:
                print("    [!] No data found on this page.")
                break

            for idx, doc in enumerate(page_data, start=1 + (page_num-1)*len(page_data)):
                print(f"{idx}. {doc['id']} | {doc['number']} | {doc['date']} | {doc['type']}")

            all_metadata.extend(page_data)

            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, "span.pagerArrow[title='pagina successiva']")
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(2)
            except Exception:
                break
            page_num += 1

        print(f"\n[INFO] Collected metadata for {len(all_metadata)} documents.\n")

        for i, doc in enumerate(all_metadata, start=1):
            print(f"{i}. Downloading {doc['id']} -> {doc['pdf_link']}")
            save_path = os.path.join(".", "downloads", f"{doc['id']}.pdf")
            if download_pdf(doc['pdf_link'], save_path):
                print(f"    [OK] Saved to {save_path}")
                save_to_db(doc, save_path)
            else:
                print(f"    [FAIL] {doc['id']}")

    finally:
        driver.quit()
        print("\nProcess finished.")