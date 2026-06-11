#!/usr/bin/env python3
import sys
import requests
from urllib.parse import urlparse

url = sys.argv[1]
sku = url.rstrip("/").split("/")[-1].replace("-1.75mm-1000g", "")

base = "https://printonion.com"

candidates = [
    f"{base}/api/products/{sku}",
    f"{base}/api/product/{sku}",
    f"{base}/api/filament/{sku}",
    f"{base}/api/filaments/{sku}",
    f"{base}/api/products?sku={sku}",
    f"{base}/api/products?slug={sku}",
    f"{base}/api/product?sku={sku}",
    f"{base}/api/product?slug={sku}",
]

headers = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",
    "Referer": url,
}

print(f"Testing SKU/slug: {sku}\n")

for api_url in candidates:
    try:
        r = requests.get(api_url, headers=headers, timeout=10)
        print(api_url)
        print("Status:", r.status_code)
        print("Content-Type:", r.headers.get("content-type"))

        text = r.text[:500]
        print(text)
        print("-" * 80)

    except Exception as e:
        print(api_url)
        print("ERROR:", e)
        print("-" * 80)
