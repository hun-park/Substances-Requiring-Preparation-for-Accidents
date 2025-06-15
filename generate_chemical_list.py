import re
import csv
import pandas as pd
import pubchempy as pcp

CAS_RE = re.compile(r"^\d{2,7}-\d{2}-\d$")


def load_cas_accident(path: str) -> list[str]:
    df = pd.read_csv(path, skiprows=1)
    return df['CAS'].astype(str).str.extract(r"(\d{2,7}-\d{2}-\d)").dropna()[0].tolist()


def load_cas_toxic(path: str) -> list[str]:
    df = pd.read_csv(path)
    return df['CAS'].astype(str).str.extract(r"(\d{2,7}-\d{2}-\d)").dropna()[0].tolist()


def fetch_additional_cas(n: int, exclude: set[str]) -> list[str]:
    cas_list = []
    cid = 1
    while len(cas_list) < n:
        try:
            comp = pcp.Compound.from_cid(cid)
            if comp.synonyms:
                for syn in comp.synonyms:
                    if CAS_RE.match(syn) and syn not in exclude and syn not in cas_list:
                        cas_list.append(syn)
                        break
        except Exception:
            pass
        cid += 1
    return cas_list


def main(num_extra: int = 1000):
    accident_cas = load_cas_accident('유해물질 목록 - 사고대비물질.csv')
    toxic_cas = load_cas_toxic('유해물질 목록 - 유독물질.csv')

    categories: dict[str, set[str]] = {}
    for cas in accident_cas:
        categories.setdefault(cas, set()).add('Accident')
    for cas in toxic_cas:
        categories.setdefault(cas, set()).add('Toxic')

    records = []
    for cas, cats in categories.items():
        if cats == {'Accident'}:
            label = 'AccidentOnly'
        elif cats == {'Toxic'}:
            label = 'ToxicOnly'
        else:
            label = 'AccidentAndToxic'
        records.append({'CAS': cas, 'Category': label})

    existing = set(categories.keys())
    extra = fetch_additional_cas(num_extra, existing)
    for cas in extra:
        records.append({'CAS': cas, 'Category': 'Other'})

    with open('chemical_list.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['CAS', 'Category'])
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)


if __name__ == '__main__':
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    main(n)
