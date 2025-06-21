import pandas as pd
import os
from pathlib import Path
from datetime import datetime, timedelta
import glob

# === CONFIGURATIE ===
ENDTIME_DELTA_HOURS = 2  # Standaard eindtijd na starttijd

# Normale wedstrijdconfiguratie
MEET_UP_DELTAS = {
    "Nationale 3 Heren A": 1.5,
    "HEREN PROMO 3B": 1.0,
    "Interfederale Beker Heren": 1.5,
    # ... andere reguliere teams
}
DEFAULT_MEET_UP_DELTA = 1.0

# Cupwedstrijdconfiguratie (apart)
CUP_MEET_UP_DELTAS = {
    "BEKER TROFEE WALRAEVE": 1.0,
    "PROVINCIALE BEKER HEREN": 1.5,
    "JEUGDBEKER JONGENS U19": 0.5,
    "JEUGDBEKER JONGENS U17": 0.75,
    "JEUGDBEKER JONGENS U15": 1.0,
    "JEUGDBEKER JONGENS U13": 1.25,
    "JEUGDBEKER JONGENS U11": 1.5,
    # Voeg nieuwe bekerwedstrijden toe
}
DEFAULT_CUP_MEET_UP_DELTA = 1.25

output_dir = './matches'
os.makedirs(output_dir, exist_ok=True)

# --- Dynamisch het juiste bestand zoeken ---
search_pattern = './downloads/www_volleyscores_be_*.xls'
xls_files = glob.glob(search_pattern)
if not xls_files:
    raise FileNotFoundError(f"Geen bestand gevonden met patroon {search_pattern}")

# Neem het nieuwste bestand
input_path = max(xls_files, key=os.path.getctime)
print(f"Gevonden bestand: {input_path}")

# Lees Excel-bestand
try:
    df = pd.read_excel(input_path, engine='xlrd')
    print("XLS-bestand succesvol gelezen")
    df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
    vereiste_kolommen = {'reeks', 'datum', 'uur', 'thuis', 'bezoekers', 'sporthall'}
    if not vereiste_kolommen.issubset(set(df.columns)):
        ontbrekend = vereiste_kolommen - set(df.columns)
        raise KeyError(f"Ontbrekende kolommen: {', '.join(ontbrekend)}")
except Exception as e:
    print(f"Fout bij lezen XLS: {e}")
    raise

def is_cup_match(reeks):
    cup_keywords = ["beker", "cup", "jeugdbeker", "trofee", "bekerwedstrijd"]
    return any(keyword in reeks.lower() for keyword in cup_keywords)

def transform_row(row):
    reeks = str(row['reeks']).strip()
    start_date = row['datum']
    start_time = row['uur']

    # Bepaal configuratie op basis van wedstrijdtype
    if is_cup_match(reeks):
        meet_up_delta = CUP_MEET_UP_DELTAS.get(reeks, DEFAULT_CUP_MEET_UP_DELTA)
    else:
        meet_up_delta = MEET_UP_DELTAS.get(reeks, DEFAULT_MEET_UP_DELTA)

    # Bereken meet-up tijd
    try:
        start_dt = datetime.strptime(f"{start_date} {start_time}", "%d/%m/%Y %H:%M")
        meet_up_dt = start_dt - timedelta(hours=meet_up_delta)
        meet_up_time = meet_up_dt.strftime("%H:%M")
    except:
        meet_up_time = ""

    # Bereken eindtijd
    try:
        end_dt = start_dt + timedelta(hours=ENDTIME_DELTA_HOURS)
        end_time = end_dt.strftime("%H:%M")
    except:
        end_time = ""

    # Bepaal matchtype
    thuis_team = str(row['thuis']).strip()
    uit_team = str(row['bezoekers']).strip()
    match_type = "Home match" if "Sferos VBK" in thuis_team else "Away match"

    return {
        'Start date': start_date,
        'start time': start_time,
        'meet up': meet_up_time,
        'end data': start_date,
        'end time': end_time,
        'match type': match_type,
        'home team': thuis_team,
        'away team': uit_team,
        'description': '',
        'place': str(row['sporthall']).strip()
    }

for reeks in df['reeks'].dropna().unique():
    df_reeks = df[df['reeks'] == reeks]
    transformed_data = [transform_row(row) for _, row in df_reeks.iterrows()]
    transformed = pd.DataFrame(transformed_data)
    safe_reeks = reeks.replace(' ', '_').replace('/', '_').replace('-', '_')
    output_path = os.path.join(output_dir, f"{safe_reeks}.xlsx")
    transformed.to_excel(output_path, index=False)
    print(f"Aangemaakt: {output_path}")

print("Verwerking voltooid! Bestanden staan in de map 'matches'")
