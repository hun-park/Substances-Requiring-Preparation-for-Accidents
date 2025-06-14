from fetch_extended_properties import fetch_all
import csv
import sys


def main(limit: int | None = None):
    with open('chemical_list.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        cas_numbers = [row['CAS'] for row in reader]
        if limit is not None:
            cas_numbers = cas_numbers[:limit]

    fieldnames = ['CAS', 'MolecularWeight', 'BoilingPoint', 'MeltingPoint', 'log_kow']

    results = []
    for cas in cas_numbers:
        props = fetch_all(cas)
        props['CAS'] = cas
        results.append(props)

    with open('chemical_properties.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow({key: row.get(key, '') for key in fieldnames})


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(n)
