import re
import sys
from pathlib import Path
import yaml
from playwright.sync_api import sync_playwright


DB_ROOT = Path("openprinttag-database")
MATERIALS_DIR = DB_ROOT / "data" / "materials" / "addnorth"
OUTPUT_DIR = Path("output")


def slugify(value):
    value = value.lower()
    value = value.replace("å", "a").replace("ä", "a").replace("ö", "o")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def fetch_page(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=60000)

        title = page.title()
        text = page.locator("body").inner_text()

        browser.close()

    return title, text


def get_slug_from_title(title):
    # Example: PETG - Black - add:north
    m = re.search(r"^(.*?)\s*-\s*(.*?)\s*-\s*add:north", title, re.I)
    if not m:
        raise ValueError(f"Could not parse title: {title}")

    material = m.group(1).strip()
    color = m.group(2).strip()

    return f"addnorth-{slugify(material)}-{slugify(color)}"


def extract_properties(text):
    props = {}

    m = re.search(r"Densitet\s+([0-9]+[.,]?[0-9]*)", text, re.I)
    if m:
        props["density"] = float(m.group(1).replace(",", "."))

    m = re.search(r"Print temperatur\s+(\d+)\s*[-–]\s*(\d+)\s*°?\s*C", text, re.I)
    if m:
        props["min_print_temperature"] = int(m.group(1))
        props["max_print_temperature"] = int(m.group(2))

    m = re.search(r"Bed temperatur\s+No\s*\(or up to\s*(\d+)\s*°?\s*C\)", text, re.I)
    if m:
        props["min_bed_temperature"] = 0
        props["max_bed_temperature"] = int(m.group(1))

    return props


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(path, data):
    OUTPUT_DIR.mkdir(exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def enrich(url):
    title, text = fetch_page(url)

    print(f"Title: {title}")

    slug = get_slug_from_title(title)
    yaml_path = MATERIALS_DIR / f"{slug}.yaml"

    print(f"Slug: {slug}")
    print(f"YAML: {yaml_path}")

    if not yaml_path.exists():
        raise FileNotFoundError(f"Could not find YAML file: {yaml_path}")

    scraped_props = extract_properties(text)

    print("\nFound on webpage:")
    for key, value in scraped_props.items():
        print(f"  {key}: {value}")

    data = load_yaml(yaml_path)
    data.setdefault("properties", {})

    print("\nChanges:")
    changed = False

    for key, value in scraped_props.items():
        old_value = data["properties"].get(key)

        if old_value in (None, "", {}):
            data["properties"][key] = value
            print(f"  + {key}: {value}")
            changed = True
        else:
            print(f"  = {key}: already has {old_value}")

    output_path = OUTPUT_DIR / f"{slug}.yaml"

    if changed:
        save_yaml(output_path, data)
        print(f"\nSaved: {output_path}")
    else:
        print("\nNo changes needed.")

def load_urls():
    urls = []
    with open("filament_urls.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue
            urls.append(line)
    return urls

def main():
    print("Starting enrich_yaml.py")
    if len(sys.argv) == 2:
        enrich(sys.argv[1])
        return
    if len(sys.argv) == 1:
        urls = load_urls()
        print(f"Found {len(urls)} URLs")
        for url in urls:
            print("=" * 60)
            print(url)
            print("=" * 60)
            try:
                enrich(url)
            except Exception as e:
                print(f"ERROR: {e}")
            print()
        return
    print('Usage: python enrich_yaml.py "URL"')
    sys.exit(1)

if __name__ == "__main__":
    main()
