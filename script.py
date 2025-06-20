from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# Instellingen
CLUB_NAAM = "O-0519 Sferos VBK Deinze"
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless=new")  # Headless mode aanzetten
chrome_options.add_argument("--window-size=1920,1080")  # Optioneel: schermgrootte instellen
chrome_options.add_argument("--disable-gpu")  # Aanbevolen bij headless
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

prefs = {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": False
}
chrome_options.add_experimental_option("prefs", prefs)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    driver.get("https://www.volleyscores.be/")
    print("Pagina geladen")

    try:
        akkoord_knop = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//input[@type='button' and @value='Akkoord' and contains(@class, 'btn-success')]")
            )
        )
        akkoord_knop.click()
        print("Cookies geaccepteerd")
    except Exception:
        print("Geen cookies-popup gevonden of al geaccepteerd")

    zoekbalk = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "searcher"))
    )
    zoekbalk.clear()
    zoekbalk.send_keys(CLUB_NAAM)
    print(f"Club '{CLUB_NAAM}' ingevoerd in zoekveld")

    wedstrijd_knop = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class, 'markedlink') and contains(., 'Alle wedstrijden van')]")
        )
    )
    print("Clubpagina geladen")

    try:
        wedstrijd_knop.click()
        print("Wedstrijdknop aangeklikt")
    except Exception as e:
        print(f"Normale klik faalde, probeer JavaScript-click: {e}")
        driver.execute_script("arguments[0].click();", wedstrijd_knop)
        print("Wedstrijdknop via JavaScript aangeklikt")

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@onclick, 'getMatchesFile')]"))
    )
    driver.execute_script("getMatchesFile();")
    print("Download gestart")

    start_tijd = time.time()
    gedownload = False
    while time.time() - start_tijd < 90:
        bestanden = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith('.xls') or f.endswith('.xlsx')]
        if bestanden:
            print(f"Download voltooid: {bestanden[-1]}")
            gedownload = True
            break
        time.sleep(2)
    if not gedownload:
        print("Download timeout - controleer handmatig")

except Exception as e:
    print(f"Fout opgetreden: {str(e)}")
    driver.save_screenshot("volley_error.png")
    print("Screenshot opgeslagen als volley_error.png")

finally:
    driver.quit()
    print("Browser gesloten")
