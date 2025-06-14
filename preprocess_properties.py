import pandas as pd
import re

INPUT_FILE = "cas_numbers_property_table_v2.csv"
OUTPUT_FILE = "cas_numbers_property_table_clean.csv"

temp_re = re.compile(r"(-?\d+(?:\.\d+)?)\s*\u00b0?\s*([FC])", re.IGNORECASE)
num_re = re.compile(r"(-?\d+(?:\.\d+)?)")

def parse_temp(value: str) -> float:
    """Parse temperature string and return Celsius value."""
    if pd.isna(value) or str(value).strip() == "":
        return float('nan')
    s = str(value)
    match = temp_re.search(s)
    if match:
        val = float(match.group(1))
        unit = match.group(2).upper()
        return (val - 32) * 5.0 / 9.0 if unit == 'F' else val
    num = num_re.search(s)
    return float(num.group(1)) if num else float('nan')

def main() -> None:
    df = pd.read_csv(INPUT_FILE)
    if 'BoilingPoint' in df.columns:
        df['BoilingPoint'] = df['BoilingPoint'].apply(parse_temp)
    if 'MeltingPoint' in df.columns:
        df['MeltingPoint'] = df['MeltingPoint'].apply(parse_temp)
    if 'Density' in df.columns:
        df = df.drop(columns=['Density'])
    df.to_csv(OUTPUT_FILE, index=False)

if __name__ == '__main__':
    main()
