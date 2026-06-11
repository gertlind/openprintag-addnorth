#!/usr/bin/env python3

import sys
from pathlib import Path
import yaml

if len(sys.argv) != 2:
    print("Usage: python test.py <country_code>")
    sys.exit(1)

country = sys.argv[1].upper()

brands_dir = Path("openprinttag-database/data/brands")

matches = []

for yaml_file in brands_dir.glob("*.yaml"):
    with open(yaml_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    countries = [c.upper() for c in data.get("countries_of_origin", [])]

    if country in countries:
        matches.append(data.get("name", yaml_file.stem))

for brand in sorted(matches):
    print(brand)

print(f"\nFound {len(matches)} brands from {country}")
