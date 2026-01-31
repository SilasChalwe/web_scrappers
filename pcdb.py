import os
import time
import sqlite3
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- DATABASE SETUP ---
DB_PATH = "./scraper_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            category TEXT,
            section TEXT,
            kind TEXT,
            type TEXT,
            number TEXT,
            date TEXT,
            ecli TEXT,
            president TEXT,
            relator TEXT,
            pdf_path TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(doc, pdf_path):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO documents
        (id, category, section, kind, type, number, date, ecli, president, relator, pdf_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        doc['id'], doc['category'], doc['section'], doc['kind'], doc['type'],
        doc['number'], doc['date'], doc['ecli'], doc['president'], doc['relator'],
        pdf_path
    ))
    conn.commit()
    conn.close()

# --- HELPER FUNCTIONS ---
def construct_pdf_url(category, date_str, section, number, doc_type):
    db = "snciv" if category.upper() == "CIVILE" else "snpen"
    day, month, year = date_str.split('/')
    formatted_date = f"{year}{month}{day}"

    section_map = {
        "PRIMA": "s10", "SECONDA": "s20", "TERZA": "s30",
        "QUARTA": "s40", "QUINTA": "s50", "SESTA": "s60",
        "SETTIMA": "s70", "UNITE": "su0"
    }
    sec_code = section_map.get(section.upper(), "s00")
    t_code = "O" if "ORDINANZA" in doc_type.upper() else "S"
    if "INTERLOCUTORIA" in doc_type.upper(): t_code = "I"

    return f"https://www.italgiure.giustizia.it/xway/application/nif/clean/hc.dll?verbo=attach&db={db}&id=./{formatted_date}/{db}@{sec_code}@a{year}@n{number.zfill(5)}@t{t_code}.clean.pdf"

def scrape_cards(driver, label):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    cards = soup.find_all('div', class_='card')
    results = []

    for card in cards:
        def get_v(arg):
            found = card.find('span', {'data-arg': arg})
            return found.get_text(strip=True) if found else "N/A"

        doc_data = {
            "category": label,
            "id": get_v('id'),
            "section": get_v('szdec'),
            "kind": get_v('kind'),
            "type": get_v('tipoprov'),
            "number": get_v('numcard'),
            "date": get_v('datdep'),
            "ecli": get_v('ecli'),
            "president": get_v('presidente'),
            "relator": get_v('relatore')
        }

        doc_data["pdf_link"] = construct_pdf_url(
            doc_data["category"], doc_data["date"],
            doc_data["section"], doc_data["number"],
            doc_data["type"]
        )

        results.append(doc_data)
    return results

def download_pdf(url, save_path):
    try:
        r = requests.get(url, timeout=30, verify=False)  # ignore SSL
        r.raise_for_status()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(r.content)
        return True
    except Exception as e:
        print(f"    [!] Failed to download {url}: {e}")
        return False

# --- MAIN SCRAPER ---
def run_scraper(max_pages=5):
    init_db()
    options = Options()
    options.add_argument("-headless")
    service = Service(executable_path="/data/data/com.termux/files/usr/bin/geckodriver")
    driver = webdriver.Firefox(service=service, options=options)
    wait = WebDriverWait(driver, 30)

    try:
        driver.get("https://www.italgiure.giustizia.it/sncass/")
        label = "CIVILE"
        print(f">>> STARTING SCRAPER: {label}")

        # Click filter
        row_xpath = f"//div[@id='keylistContent[kind]']//tr[contains(., '{label}')]"
        filter_row = wait.until(EC.element_to_be_clickable((By.XPATH, row_xpath)))
        driver.execute_script("arguments[0].click();", filter_row)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card")))
        print("[OK] Filter clicked and results loaded.\n")

        # --- Collect metadata ---
        all_metadata = []
        page_num = 1
        while page_num <= max_pages:
            print(f"--- SCRAPING PAGE {page_num} ---")
            page_data = scrape_cards(driver, label)
            if not page_data:
                print("    [!] No data found on this page.")
                break

            # Show metadata per doc
            for idx, doc in enumerate(page_data, start=1 + (page_num-1)*len(page_data)):
                print(f"{idx}. {doc['id']} | {doc['number']} | {doc['date']} | {doc['type']}")

            all_metadata.extend(page_data)

            # Go to next page
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, "span.pagerArrow[title='pagina successiva']")
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(2)
            except:
                break
            page_num += 1

        print(f"\n[INFO] Collected metadata for {len(all_metadata)} documents.\n")

        # --- Download PDFs and save to DB ---
        for i, doc in enumerate(all_metadata, start=1):
            print(f"{i}. Downloading {doc['id']} -> {doc['pdf_link']}")
            save_path = f"./downloads/{doc['id']}.pdf"
            if download_pdf(doc['pdf_link'], save_path):
                print(f"    [OK] Saved to {save_path}")
                save_to_db(doc, save_path)
            else:
                print(f"    [FAIL] {doc['id']}")

    finally:
        driver.quit()
        print("\nProcess finished.")

if __name__ == "__main__":
    run_scraper(max_pages=5)
