"""Crée le formulaire Jotform à partir de schema/registre.yml (API Jotform).

Usage :
    export JOTFORM_API_KEY=xxxxxxxx          # clé API avec droits "Full Access"
    export JOTFORM_API_BASE=https://eu-api.jotform.com   # compte hébergé UE (recommandé)
    python scripts/jotform_create_form.py

Affiche l'identifiant (JOTFORM_FORM_ID) et l'URL du formulaire créé.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request

from common import jotform_name, load_schema

API_BASE = os.environ.get("JOTFORM_API_BASE", "https://eu-api.jotform.com").rstrip("/")


def build_payload() -> dict:
    schema = load_schema()
    form = schema["form"]
    qs: dict[str, dict] = {}
    order = 0

    def add(q: dict) -> None:
        nonlocal order
        order += 1
        q["order"] = str(order)
        qs[str(order)] = q

    add({"type": "control_head", "text": form["title"], "headerType": "Large",
         "subHeader": "Registre des activités de traitement – art. 30 RGPD"})
    intro_html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank">\1</a>', form["intro"])
    intro_html = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", intro_html, flags=re.S)
    intro_html = (intro_html.replace("## ", "").replace("\n\n", "<br><br>").replace("\n", " "))
    add({"type": "control_text", "text": f"<p>{intro_html}</p>"})

    for f in schema["fields"]:
        t = f["type"]
        if t == "section":
            add({"type": "control_head", "text": f["label"], "headerType": "Default"})
            continue
        q = {"text": f["label"], "name": jotform_name(f["id"]),
             "required": "Yes" if f.get("required") else "No"}
        if f.get("description"):
            q["subLabel"] = f["description"]
            q["description"] = f["description"]
        if t == "input":
            q.update(type="control_textbox", hint=f.get("placeholder", ""))
        elif t == "textarea":
            q.update(type="control_textarea", hint=f.get("placeholder", ""))
        elif t == "date":
            q.update(type="control_datetime", format="ddmmyyyy", allowTime="No")
        elif t == "dropdown":
            q.update(type="control_dropdown", options="|".join(f["options"]),
                     emptyText="Choisir…")
        elif t == "checkboxes":
            q.update(type="control_checkbox", options="|".join(f["options"]))
            if f.get("each_required"):
                q["minSelection"] = str(len(f["options"]))
            if f.get("gap"):
                q["subLabel"] = (q.get("subLabel", "") +
                                 " Toute case non cochée sera inscrite au plan d'actions.").strip()
        add(q)

    add({"type": "control_button", "text": "Envoyer la fiche", "buttonAlign": "center"})
    return {"questions": qs, "properties": {"title": form["title"]}}


def main() -> None:
    key = os.environ.get("JOTFORM_API_KEY")
    payload = build_payload()
    if "--dry-run" in sys.argv or not key:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        if not key:
            print("\n(JOTFORM_API_KEY absente : aperçu uniquement)", file=sys.stderr)
        return
    req = urllib.request.Request(
        f"{API_BASE}/form",
        data=json.dumps(payload).encode("utf-8"),
        method="PUT",
        headers={"APIKEY": key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
    content = data.get("content", {})
    print("Formulaire créé !")
    print("JOTFORM_FORM_ID =", content.get("id"))
    print("URL             =", content.get("url"))


if __name__ == "__main__":
    main()
