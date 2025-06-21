import pandas as pd
import os
from pathlib import Path

# Configuratiepaden
input_path = './downloads/www_volleyscores_be_20250621.xls'
output_dir = './matches'

# Uitvoermap aanmaken
os.makedirs(output_dir, exist_ok=True)

# Bestand lezen als Excel met juiste engine
try:
    df = pd.read_excel(input_path, engine='openpyxl')
    print("XLS-bestand succesvol gelezen met openpyxl engine")
except Exception as e:
    print(f"Fout bij lezen XLS: {e}")
    print("Probeer alternatieve engine...")
    try:
        df = pd.read_excel(input_path, engine='xlrd')
        print("XLS-bestand gelezen met xlrd engine")
    except:
        raise ValueError("Kon Excel-bestand niet lezen. Controleer bestandsformaat.")

# Kolomnamen controleren en corrigeren
if 'Reeks' not in df.columns:
    if 'reeks' in [c.lower() for c in df.columns]:
        df = df.rename(columns={c: 'Reeks' for c in df.columns if c.lower() == 'reeks'})
    else:
        raise KeyError("Kolom 'Reeks' niet gevonden in bestand. Beschikbare kolommen: " + ", ".join(df.columns))

# Transformatiemapping
output_columns = [
    'Start date', 'start time', 'meet up', 'end data', 'end time',
    'match type', 'home team', 'away team', 'description', 'place'
]

def transform_row(row):
    return {
        'Start date': row['Datum'],
        'start time': row['Uur'],
        'meet up': '',
        'end data': row['Datum'],
        'end time': row['Uur'],
        'match type': row['Reeks'],
        'home team': row['Thuis'],
        'away team': row['Bezoekers'],
        'description': '',
        'place': row['Sporthall']
    }

# Verwerking per teamcategorie
for reeks in df['Reeks'].dropna().unique():
    # Filteren op teamcategorie
    df_reeks = df[df['Reeks'] == reeks]
    
    # Transformeren naar gewenst formaat
    transformed_data = [transform_row(row) for _, row in df_reeks.iterrows()]
    transformed = pd.DataFrame(transformed_data)
    
    # Bestandsnaam veilig maken
    safe_reeks = reeks.replace(' ', '_').replace('/', '_').replace('-', '_')
    output_path = os.path.join(output_dir, f"{safe_reeks}.xlsx")
    
    # Opslaan als Excel
    transformed.to_excel(output_path, index=False, columns=output_columns)
    print(f"Aangemaakt: {output_path}")

print("Verwerking voltooid! Bestanden staan in de map 'matches'")
