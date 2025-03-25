import csv  
from datetime import datetime

# Archivos de entrada/salida
input_csv = "forex_factory_catalog.csv"
output_csv = "forex_factory_cleaned.csv"

with open(input_csv, 'r', encoding='utf-8') as infile, \
     open(output_csv, 'w', newline='', encoding='utf-8') as outfile:

    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    writer.writeheader()

    for row in reader:
        # Limpiar datetime: "2007-01-01T01:00:00+01:00" → "2007-01-01 01:00:00"
        original_date = row['datetime']
        clean_date = original_date.replace('T', ' ').split('+')[0]
        row['datetime'] = clean_date

        # Normalizar impacto (Bajo, Medio, Alto → 1, 2, 3)  
        original_impact = row['impact']
        #clean_impact = original_impact.lower().replace('low impact expected', '1').replace('medium impact expected', '2').replace('high impact expected', '3').replace('holiday', '0').strip()
        clean_impact = original_impact.lower().replace('low', '1').replace('medium', '2').replace('high', '3').replace('holiday', '0').strip()
        row['impact'] = clean_impact

        writer.writerow(row)

print("¡CSV limpiado correctamente!")