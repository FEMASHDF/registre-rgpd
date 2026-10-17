"""Génère .github/ISSUE_TEMPLATE/01-registre-traitement.yml depuis schema/registre.yml.

Usage : python scripts/generate_issue_form.py
"""
from __future__ import annotations

import yaml

from common import ROOT, load_schema

OUT = ROOT / ".github" / "ISSUE_TEMPLATE" / "01-registre-traitement.yml"


class _Literal(str):
    pass


def _literal_repr(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


yaml.add_representer(_Literal, _literal_repr)


def build() -> dict:
    schema = load_schema()
    form = schema["form"]
    body: list[dict] = [{"type": "markdown", "attributes": {"value": _Literal(form["intro"])}}]

    for f in schema["fields"]:
        t = f["type"]
        if t == "section":
            body.append({"type": "markdown", "attributes": {"value": f"---\n## {f['label']}"}})
            continue

        attrs: dict = {"label": f["label"]}
        if f.get("description"):
            attrs["description"] = f["description"]
        if f.get("placeholder") and t in ("input", "textarea", "date"):
            attrs["placeholder"] = f["placeholder"]

        if t in ("input", "date"):
            item = {"type": "input", "id": f["id"], "attributes": attrs}
        elif t == "textarea":
            item = {"type": "textarea", "id": f["id"], "attributes": attrs}
        elif t == "dropdown":
            attrs["options"] = f["options"]
            item = {"type": "dropdown", "id": f["id"], "attributes": attrs}
        elif t == "checkboxes":
            each = bool(f.get("each_required"))
            attrs["options"] = [{"label": o, "required": each} if each else {"label": o}
                                for o in f["options"]]
            if f.get("gap"):
                attrs["description"] = (attrs.get("description", "") +
                                        " Toute case non cochée sera inscrite au plan d'actions.").strip()
            item = {"type": "checkboxes", "id": f["id"], "attributes": attrs}
        else:
            raise ValueError(f"Type inconnu : {t}")

        # Les cases à cocher GitHub n'ont pas de "required" global : il est géré par option.
        if t != "checkboxes":
            item["validations"] = {"required": bool(f.get("required"))}
        body.append(item)

    return {
        "name": "Registre RGPD – fiche de traitement",
        "description": form["title"],
        "title": form["issue_title_prefix"],
        "labels": form["labels"],
        "body": body,
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    header = "# FICHIER GÉNÉRÉ – modifier schema/registre.yml puis relancer scripts/generate_issue_form.py\n"
    OUT.write_text(header + yaml.dump(build(), allow_unicode=True, sort_keys=False, width=1000),
                   encoding="utf-8")
    print(f"Écrit : {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
