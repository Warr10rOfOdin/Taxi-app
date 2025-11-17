# kontant_edits.py
import os
import json
from datetime import datetime

EDIT_PATH = os.path.join(os.path.dirname(__file__), "skift_edits.json")

def load_kontant_edits():
    try:
        with open(EDIT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_kontant_edits(edits):
    with open(EDIT_PATH, "w", encoding="utf-8") as f:
        json.dump(edits, f, indent=2, ensure_ascii=False)

def upsert_kontant_edit(loyve, skiftnr, amount, note):
    edits = load_kontant_edits()
    found = False
    for e in edits:
        if e["loyve"] == loyve and e["skiftnr"] == skiftnr:
            e["amount"] = amount
            e["note"] = note
            e["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            found = True
    if not found:
        edits.append({
            "loyve": loyve,
            "skiftnr": skiftnr,
            "amount": amount,
            "note": note,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    save_kontant_edits(edits)

def delete_kontant_edit(loyve, skiftnr):
    edits = load_kontant_edits()
    edits = [e for e in edits if not (e["loyve"] == loyve and e["skiftnr"] == skiftnr)]
    save_kontant_edits(edits)

def get_edit(loyve, skiftnr):
    for e in load_kontant_edits():
        if e["loyve"] == loyve and e["skiftnr"] == skiftnr:
            return e
    return None

def get_edits_for_keys(keys):
    # keys: set of (loyve, skiftnr) for relevant file
    return [e for e in load_kontant_edits() if (e["loyve"], e["skiftnr"]) in keys]
