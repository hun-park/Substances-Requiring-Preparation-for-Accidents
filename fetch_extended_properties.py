import csv
import os
import requests
from bs4 import BeautifulSoup
import pubchempy as pcp

try:
    from chemspipy import ChemSpider
except ImportError:  # ChemSpiPy may not be installed
    ChemSpider = None

# ChemSpider API configuration
CS_API_KEY = os.getenv('CHEMSPIDER_API_KEY') or os.getenv('CHEMSPIDER_TOKEN')
if CS_API_KEY and ChemSpider:
    cs_client = ChemSpider(CS_API_KEY)
else:
    cs_client = None

def _find_first_string(obj):
    """Recursively search PubChem PUG-View JSON for the first string value."""
    if isinstance(obj, dict):
        if 'StringWithMarkup' in obj:
            return obj['StringWithMarkup'][0].get('String')
        for v in obj.values():
            result = _find_first_string(v)
            if result:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = _find_first_string(item)
            if result:
                return result
    return None


def _pug_view_value(cid: int, heading: str):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON?heading={heading.replace(' ', '%20')}"
    try:
        r = requests.get(url, timeout=30)
        if r.ok:
            j = r.json()
            return _find_first_string(j)
    except Exception:
        pass
    return None

def get_pubchem_data(cas: str):
    data = {}
    try:
        cids = pcp.get_cids(cas, 'name')
        if not cids:
            return data
        cid = cids[0]
        comp = pcp.Compound.from_cid(cid)
        if comp.molecular_weight:
            data['MolecularWeight'] = comp.molecular_weight
        if comp.xlogp is not None:
            data['log_kow'] = comp.xlogp
        bp = _pug_view_value(cid, 'Boiling Point')
        mp = _pug_view_value(cid, 'Melting Point')
        dens = _pug_view_value(cid, 'Density')
        if bp:
            data['BoilingPoint'] = bp.strip()
        if mp:
            data['MeltingPoint'] = mp.strip()
        if dens:
            data['Density'] = dens
    except Exception as e:
        print(f"PubChem lookup failed for {cas}: {e}")
    return data

def get_chemspider_data(cas: str):
    if not cs_client:
        return {}
    data = {}
    try:
        results = cs_client.search(cas)
        if results:
            comp = results[0]
            if getattr(comp, 'molecular_weight', None) and 'MolecularWeight' not in data:
                data['MolecularWeight'] = comp.molecular_weight
            if hasattr(comp, 'logp') and comp.logp is not None:
                data['log_kow'] = comp.logp
    except Exception as e:
        print(f"ChemSpider lookup failed for {cas}: {e}")
    return data


def get_nist_data(cas: str):
    url = f"https://webbook.nist.gov/cgi/cbook.cgi?ID={cas}&Mask=4&Units=SI"
    data = {}
    try:
        r = requests.get(url, timeout=30)
        if not r.ok:
            return data
        soup = BeautifulSoup(r.text, 'html.parser')
        for tr in soup.select('tr.exp'):
            tds = tr.find_all('td')
            if len(tds) < 3:
                continue
            label = tds[0].get_text(strip=True)
            value = tds[1].get_text(strip=True)
            units = tds[2].get_text(strip=True)
            if 'Tboil' in label and 'BoilingPoint' not in data:
                data['BoilingPoint'] = f"{value} {units}".strip()
            elif 'Tfus' in label and 'MeltingPoint' not in data:
                data['MeltingPoint'] = f"{value} {units}".strip()
    except Exception as e:
        print(f"NIST lookup failed for {cas}: {e}")
    return data

def merge_data(*dicts):
    result = {}
    for d in dicts:
        for k, v in d.items():
            if v and k not in result:
                result[k] = v
    return result

def fetch_all(cas: str):
    return merge_data(
        get_pubchem_data(cas),
        get_chemspider_data(cas),
        get_nist_data(cas),
    )

def main():
    with open('cas_numbers_table.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        cas_numbers = [row['CAS'] for row in reader]

    fieldnames = [
        'CAS',
        'MolecularWeight',
        'BoilingPoint',
        'MeltingPoint',
        'Density',
        'log_kow',
    ]

    results = []
    for cas in cas_numbers:
        props = fetch_all(cas)
        props['CAS'] = cas
        results.append(props)

    with open('cas_numbers_property_table_v2.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow({key: row.get(key, '') for key in fieldnames})

if __name__ == '__main__':
    main()
