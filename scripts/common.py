"""Outils communs : lecture du schéma et format du corps des issues."""
from __future__ import annotations

import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schema" / "registre.yml"
NO_RESPONSE = "_No response_"
JOTFORM_MARKER = "<!-- jotform-submission:{} -->"
JOTFORM_MARKER_RE = re.compile(r"<!-- jotform-submission:(\d+) -->")


def load_schema() -> dict:
    with open(SCHEMA_PATH, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def questions(schema: dict) -> list[dict]:
    """Champs à saisir (hors titres de section)."""
    return [f for f in schema["fields"] if f["type"] != "section"]


def jotform_name(field_id: str) -> str:
    """Nom de champ Jotform : lettres/chiffres uniquement."""
    return re.sub(r"[^a-zA-Z0-9]", "", field_id)


def render_issue_body(schema: dict, answers: dict, marker: str = "") -> str:
    """Produit un corps d'issue au format identique à celui d'un Issue Form GitHub.

    answers : {field_id: str | list[str]}
    """
    parts = []
    for f in questions(schema):
        value = answers.get(f["id"])
        if f["type"] == "checkboxes":
            chosen = set(value or [])
            lines = [f"- [{'X' if o in chosen else ' '}] {o}" for o in f["options"]]
            # options libres saisies dans Jotform mais absentes du schéma
            lines += [f"- [X] {o}" for o in (value or []) if o not in f["options"]]
            text = "\n".join(lines)
        else:
            text = (value or "").strip() if isinstance(value, str) else ", ".join(value or [])
            text = text or NO_RESPONSE
        parts.append(f"### {f['label']}\n\n{text}")
    body = "\n\n".join(parts)
    return f"{body}\n\n{marker}".strip() + "\n"


def parse_issue_body(schema: dict, body: str) -> dict:
    """Relit un corps d'issue (Issue Form ou synchro Jotform) -> {field_id: valeur}."""
    by_label = {f["label"].strip(): f for f in questions(schema)}
    result: dict = {}
    sections = re.split(r"^### +", body or "", flags=re.M)
    for sec in sections[1:]:
        label, _, content = sec.partition("\n")
        f = by_label.get(label.strip())
        if not f:
            continue
        content = JOTFORM_MARKER_RE.sub("", content).strip()
        if f["type"] == "checkboxes":
            result[f["id"]] = re.findall(r"^- \[[xX]\] +(.+?)\s*$", content, flags=re.M)
        else:
            result[f["id"]] = "" if content == NO_RESPONSE else content
    return result
