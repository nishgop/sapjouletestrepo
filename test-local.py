#!/usr/bin/env python3
"""
Local test script for SAP Icon Extractor Agent tools.
No BTP account or deployment needed.

Run:
    pip install requests Pillow imagehash langchain-core
    python test-local.py
"""

import json
import os
import sys
import tempfile

PASS = 0
FAIL = 0

TMP = tempfile.mkdtemp()
os.environ["ICON_CATALOG_PATH"] = os.path.join(TMP, "catalog.json")
ICONS_DIR = os.path.join(TMP, "icons")

def check(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        print(f"  ✅ PASS: {label}")
        PASS += 1
    else:
        print(f"  ❌ FAIL: {label}" + (f" — {detail}" if detail else ""))
        FAIL += 1

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "assets/sap-icon-extractor-agent/app"))

try:
    from tools.search_google_images import search_google_images
    from tools.read_catalog import read_catalog
    from tools.update_catalog import update_catalog
    print("✅ Tools imported\n")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 1: Search
print("▶ Test 1: Search Google Images")
results = search_google_images.invoke({"query": "SAP UI5 icons", "max_results": 10})
check("returns a list", isinstance(results, list))
check("found URLs", len(results) > 0, f"got {len(results)}")
if results:
    print(f"     → Found {len(results)} URLs. First: {results[0]['url'][:80]}")

# Test 2: Empty catalog
print("\n▶ Test 2: Empty catalog")
catalog = read_catalog.invoke({})
check("catalog is list", isinstance(catalog, list))
check("starts empty", len(catalog) == 0)

# Test 3: Add icon
print("\n▶ Test 3: Add icon to catalog")
r = update_catalog.invoke({
    "filename": "sap-logo.png",
    "source_url": "https://example.com/sap-logo.png",
    "perceptual_hash": "abcd1234",
    "discovered_at": "2026-10-01T12:00:00Z",
    "tags": ["sap", "logo"]
})
check("icon added", r.get("added") == True, str(r))

# Test 4: Deduplication
print("\n▶ Test 4: Deduplication")
r2 = update_catalog.invoke({
    "filename": "sap-logo.png",
    "source_url": "https://example.com/sap-logo.png",
    "perceptual_hash": "abcd1234",
    "discovered_at": "2026-10-01T12:00:00Z",
    "tags": []
})
check("duplicate rejected", r2.get("added") == False)

# Test 5: Catalog persists
print("\n▶ Test 5: Catalog persists")
catalog = read_catalog.invoke({})
check("1 entry in catalog", len(catalog) == 1, f"got {len(catalog)}")
check("correct URL stored", catalog[0]["source_url"] == "https://example.com/sap-logo.png")

print(f"\n{'='*40}")
print(f" Results: {PASS} passed, {FAIL} failed")
print(f"{'='*40}")
sys.exit(0 if FAIL == 0 else 1)
