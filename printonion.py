#!/usr/bin/env python3

from pathlib import Path
import sys
import requests
import yaml

API_URL = "https://printonion.com/api/products"
OUTPUT_DIR = Path("output_printonion")
BRAND = "printonion"

MATERIAL_PROPERTIES = {
    "petg": {
        "density": 1.27,
        "min_print_temperature": 225,
        "max_print_temperature": 260,
        "min_bed_temperature": 0,
        "max_bed_temperature": 80,
    },
}


def color_rgba(hex_color):
    if not hex_color:
        return None

    hex_color = hex_color.strip()

    if not hex_color.startswith("#"):
        hex_color = "#" + hex_color

    if len(hex_color) == 7:
        hex_color += "ff"

    return hex_color.lower()


def load_products():
    r = requests.get(
        API_URL,
        headers={"Accept": "application/json"},
        timeout=30,
    )

    r.raise_for_status()

    data = r.json()

    if not data.get("success"):
        raise RuntimeError("PrintOnion API returned success=false")

    return data.get("data", [])


def product_to_yaml(product):
    material = (product.get("material") or "").lower()
    title = product.get("title") or product.get("sku")

    item = {
        "brand": {
            "slug": BRAND
        },
        "name": title,
        "class": "FFF",
        "type": material.upper(),
        "abbreviation": material.upper(),
    }

    rgba = color_rgba(product.get("color_hex"))
    if rgba:
        item["primary_color"] = {
            "color_rgba": rgba
        }

    if product.get("image_url"):
        item["photos"] = [
            {
                "url": product["image_url"],
                "type": "unspecified"
            }
        ]

    item["properties"] = MATERIAL_PROPERTIES.get(material, {})

    return item


def main():
    wanted_material = sys.argv[1].lower() if len(sys.argv) > 1 else None

    OUTPUT_DIR.mkdir(exist_ok=True)

    products = load_products()

    written = 0

    for product in products:
        sku = product.get("sku")
        material = (product.get("material") or "").lower()

        if not sku:
            continue

        if wanted_material and material != wanted_material:
            continue

        if material not in MATERIAL_PROPERTIES:
            continue

        yaml_data = product_to_yaml(product)

        out_file = OUTPUT_DIR / f"{BRAND}-{sku}.yaml"

        out_file.write_text(
            yaml.safe_dump(
                yaml_data,
                sort_keys=False,
                allow_unicode=True,
            ),
            encoding="utf-8",
        )

        print(f"Skapad: {out_file.name}")
        written += 1

    print()
    print(f"Skapade filer: {written}")
    print(f"Output folder: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()