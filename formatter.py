import pandas as pd

# Inlezen van het CSV-bestand met correcte delimiter
df = pd.read_csv('./downloads/volley_scores.csv', delimiter=';')

# Gewenste kolomvolgorde en mapping
output_columns = [
    'Start date', 'start time', 'meet up', 'end data', 'end time',
    'match type', 'home team', 'away team', 'description', 'place'
]

# Functie om de rijen om te zetten naar het gewenste formaat
def transform_row(row):
    return {
        'Start date': row['Datum'],
        'start time': row['Uur'],
        'meet up': '',  # Geen data beschikbaar
        'end data': row['Datum'],  # Geen aparte einddatum, dus gelijk aan start
        'end time': row['Uur'],    # Geen aparte eindtijd, dus gelijk aan start
        'match type': row['Reeks'],
        'home team': row['Thuis'],
        'away team': row['Bezoekers'],
        'description': '',         # Geen data beschikbaar
        'place': row['Sporthall']
    }

# Voor elke unieke waarde in 'Reeks' een apart bestand aanmaken
for reeks in df['Reeks'].dropna().unique():
    df_reeks = df[df['Reeks'] == reeks]
    # Omzetten naar het gewenste formaat
    transformed = df_reeks.apply(transform_row, axis=1, result_type='expand')
    # Opslaan als CSV, spaties en speciale tekens vervangen in bestandsnaam
    safe_reeks = reeks.replace(' ', '_').replace('/', '_').replace('-', '_')
    filename = f"{safe_reeks}.csv"
    transformed.to_csv(filename, index=False, columns=output_columns)
    print(f"Aangemaakt: {filename}")

print("Klaar!")
