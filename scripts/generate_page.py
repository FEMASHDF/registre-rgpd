"""Met à jour docs/index.html (page GitHub Pages) depuis schema/registre.yml.

La page fonctionne entièrement dans le navigateur : les réponses ne sont envoyées
nulle part ; le registre Excel est produit localement. Seuls le nom et le type de
la structure sont transmis au formulaire Jotform de suivi d'utilisation.

Le script remplace, dans docs/index.html, le contenu situé entre les marqueurs
/*SCHEMA*/ ... /*FIN_SCHEMA*/ et /*USAGE*/ ... /*FIN_USAGE*/.

Usage : python scripts/generate_page.py
"""
from __future__ import annotations

import json
import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "docs" / "index.html"
USAGE = {  # formulaire Jotform « Suivi d'utilisation » (compte FEMAS HDF, hébergé UE)
    "formId": "262895568192373",
    "submitUrl": "https://eu-submit.jotform.com/submit/262895568192373/",
    "fields": {"structure": "q2_structure", "type": "q3_typestructure"},
}


def inject(html: str, tag: str, value) -> str:
    data = json.dumps(value, ensure_ascii=False)
    return re.sub(rf"/\*{tag}\*/.*?/\*FIN_{tag}\*/", lambda m: f"/*{tag}*/{data}/*FIN_{tag}*/",
                  html, count=1, flags=re.S)


def main() -> None:
    schema = yaml.safe_load((ROOT / "schema" / "registre.yml").read_text(encoding="utf-8"))
    html = PAGE.read_text(encoding="utf-8")
    html = inject(html, "SCHEMA", schema)
    html = inject(html, "USAGE", USAGE)
    PAGE.write_text(html, encoding="utf-8")
    print(f"Mis à jour : {PAGE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
