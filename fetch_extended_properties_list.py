from fetch_extended_properties import fetch_all
import csv
import sys


def load_accident_info() -> dict[str, str]:
    """Return mapping of CAS to introduction year for accident-prevention substances."""
    info = {}
    with open('유해물질 목록 - 사고대비물질.csv', newline='', encoding='utf-8') as f:
        f.readline()  # skip empty line
        reader = csv.DictReader(f)
        for row in reader:
            cas = row.get('CAS')
            year = row.get('도입연도', '')
            if cas:
                info[cas] = year
    return info


def load_toxic_set() -> set[str]:
    """Return set of CAS numbers listed as toxic substances."""
    toks = set()
    with open('유해물질 목록 - 유독물질.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cas = row.get('CAS')
            if cas and cas != '#N/A':
                toks.add(cas)
    return toks


def main(limit: int | None = None):
    accident_info = load_accident_info()
    toxic_set = load_toxic_set()

    fieldnames = [
        'CAS',
        'MolecularWeight',
        'BoilingPoint',
        'MeltingPoint',
        'log_kow',
        '분류',
        '도입연도',
    ]

    results = []
    for cas in cas_numbers:
        props = fetch_all(cas)
        props['CAS'] = cas
        if cas in accident_info:
            props['분류'] = '사고대비물질'
            props['도입연도'] = accident_info[cas]
        elif cas in toxic_set:
            props['분류'] = '유독물질'

        results.append(props)

    with open('chemical_properties.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow({key: row.get(key, '') for key in fieldnames})


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(n)
