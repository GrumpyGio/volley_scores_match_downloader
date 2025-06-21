import pandas as pd
import os
from pathlib import Path
from datetime import datetime, timedelta

# === CONFIGURATIE ===
ENDTIME_DELTA_HOURS = 2  # Aantal uren na starttijd
INPUT_PATH = './downloads/www_volleyscores_be_20250621.xls'
OUTPUT_DIR = './matches'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Lees Excel-bestand met dynamische kolomdetectie
try:
    df = pd.read_excel(INPUT_PATH, engine='xlrd', header=0)
    print("Excel-bestand succesvol gelezen")
    
    # Normaliseer kolomnamen: verwijder spaties, maak kleine letters
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    # Toon beschikbare kolommen voor debugging
    print("Beschikbare kolommen:", df.columns.tolist())
    
    # Controleer vereiste kolommen
    vereiste_kolommen = {'reeks', 'datum', 'uur', 'thuis', 'bezoekers', 'sporthall'}
    if not vereiste_kolommen.issubset(set(df.columns)):
        ontbrekend = vereiste_kolommen - set(df.columns)
        raise KeyError(f"Ontbrekende kolommen: {', '.join(ontbrekend)}")

except Exception as e:
    print(f"Fout bij lezen: {e}")
    raise

# Verzamel clubnamen die met "Sferos VBK" beginnen
clubnamen = set()
for kolom in ['thuis', 'bezoekers']:
    clubnamen.update(
        str(naam).strip()
        for naam in df[kolom].unique()
        if 'sferos vbk' in str(naam).lower()
    )
print(f"Gevonden clubnamen: {', '.join(clubnamen)}")

# Transformeer rij naar gewenst formaat
def transform_row(row):
    # Bepaal matchtype
    thuis_team = str(row['thuis']).strip()
    uit_team = str(row['bezoekers']).strip()
    match_type = "Home match" if any(club in thuis_team for club in clubnamen) else "Away match"
    
    # Bereken eindtijd
    try:
        start_dt = datetime.strptime(f"{row['datum']} {row['uur']}", "%d/%m/%Y %H:%M")
        eind_tijd = (start_dt + timedelta(hours=ENDTIME_DELTA_HOURS)).strftime("%H:%M")
    except:
        eind_tijd = ""
    
    return {
        'Start date': row['datum'],
        'start time': row['uur'],
        'meet up': '',
        'end data': row['datum'],
        'end time': eind_tijd,
        'match type': match_type,
        'home team': thuis_team,
        'away team': uit_team,
        'description': '',
        'place': str(row['sporthall']).strip()
    }

# Verwerk per reeks
for reeks in df['reeks'].dropna().unique():
    subset = df[df['reeks'] == reeks]
    getransformeerd = pd.DataFrame([transform_row(row) for _, row in subset.iterrows()])
    
    # Genereer bestandsnaam
    veilige_naam = reeks.replace(' ', '_').replace('/', '_').replace('-', '_')
    uitvoerpad = os.path.join(OUTPUT_DIR, f"{veilige_naam}.xlsx")
    
    # Opslaan
    getransformeerd.to_excel(uitvoerpad, index=False)
    print(f"Aangemaakt: {uitvoerpad}")

print("Verwerking voltooid! Bestanden staan in de map 'matches'")
