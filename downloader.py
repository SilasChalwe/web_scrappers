import os
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_pdf(url, save_path, timeout=30, verify=False):
    try:
        r = requests.get(url, timeout=timeout, verify=verify)
        r.raise_for_status()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(r.content)
        return True
    except Exception as e:
        print(f"    [!] Failed to download {url}: {e}")
        return False