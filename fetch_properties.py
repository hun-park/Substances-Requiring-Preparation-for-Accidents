import csv
import pubchempy as pcp

# Input and output file names
input_file = 'cas_numbers_table.csv'
output_file = 'cas_numbers_property_table.csv'

# List of property names available from PubChem
properties = [
    'MolecularFormula',
    'MolecularWeight',
    'XLogP',
    'ExactMass',
    'TPSA',
]

with open(input_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    cas_numbers = [row['CAS'] for row in reader]

results = []
for cas in cas_numbers:
    try:
        props = pcp.get_properties(','.join(properties), cas, 'name')
        if props:
            entry = {'CAS': cas}
            # Remove CID returned from PubChem
            for key in properties:
                entry[key] = props[0].get(key, '')
            results.append(entry)
        else:
            print(f"No data found for {cas}")
    except Exception as e:
        print(f"Failed to fetch data for {cas}: {e}")

with open(output_file, 'w', newline='', encoding='utf-8') as out:
    writer = csv.DictWriter(out, fieldnames=['CAS'] + properties)
    writer.writeheader()
    for row in results:
        writer.writerow(row)
