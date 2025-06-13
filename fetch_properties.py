import csv
import pubchempy as pcp

# Input and output file names
input_file = 'cas_numbers_table.csv'
output_file = 'cas_numbers_property_table.csv'

# List of property names we want from PubChem
properties = ['MolecularWeight', 'BoilingPoint', 'MeltingPoint', 'Density']

with open(input_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    cas_numbers = [row['CAS'] for row in reader]

results = []
for cas in cas_numbers:
    try:
        compound = pcp.get_compounds(cas, 'name')[0]
        results.append({
            'CAS': cas,
            'MolecularWeight': compound.molecular_weight,
            'BoilingPoint': compound.boiling_point,
            'MeltingPoint': compound.melting_point,
            'Density': compound.density,
        })
    except Exception as e:
        print(f"Failed to fetch data for {cas}: {e}")

with open(output_file, 'w', newline='', encoding='utf-8') as out:
    writer = csv.DictWriter(out, fieldnames=['CAS'] + properties)
    writer.writeheader()
    for row in results:
        writer.writerow(row)
