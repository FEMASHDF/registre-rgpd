"""Importe les réponses Jotform comme issues GitHub (format identique à l'Issue Form).

Variables d'environnement :
    JOTFORM_API_KEY, JOTFORM_FORM_ID, JOTFORM_API_BASE (défaut eu-api)
    GH_TOKEN (fourni par GitHub Actions), GITHUB_REPOSITORY
Les doublons sont évités grâce au marqueur <!-- jotform-submission:ID --> dans chaque issue.
"""
from __future__ import annotations

import json
import os
import subprocess
import urllib.parse
import urllib.request

from common import JOTFORM_MARKER, JOTFORM_MARKER_RE, jotform_name, load_schema, questions, render_issue_body

API_BASE = os.environ.get("JOTFORM_API_BASE", "https://eu-api.jotform.com").rstrip("/")


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def existing_submission_ids() -> set[str]:
    out = gh("issue", "list", "--label", "source:jotform", "--state", "all",
             "--limit", "2000", "--json", "body")
    return {m for i in json.loads(out) for m in JOTFORM_MARKER_RE.findall(i["body"] or "")}


def fetch_submissions(form_id: str, key: str) -> list[dict]:
    params = urllib.parse.urlencode({"limit": 1000, "orderby": "created_at",
                                     "filter": json.dumps({"status:ne": "DELETED"})})
    req = urllib.request.Request(f"{API_BASE}/form/{form_id}/submissions?{params}",
                                 headers={"APIKEY": key})
    with urllib.request.urlopen(req) as resp:
        return json.load(resp).get("content", [])


def to_answers(schema: dict, submission: dict) -> dict:
    by_name = {a.get("name"): a for a in submission.get("answers", {}).values()}
    answers: dict = {}
    for f in questions(schema):
        a = by_name.get(jotform_name(f["id"]), {})
        raw = a.get("answer")
        if f["type"] == "checkboxes":
            if isinstance(raw, dict):
                raw = list(raw.values())
            answers[f["id"]] = [str(x) for x in (raw or [])] if isinstance(raw, list) else (
                [s.strip() for s in str(raw).split("\n") if s.strip()] if raw else [])
        elif f["type"] == "date":
            answers[f["id"]] = a.get("prettyFormat") or (raw if isinstance(raw, str) else "")
        else:
            answers[f["id"]] = raw if isinstance(raw, str) else (a.get("prettyFormat") or "")
    return answers


def ensure_labels(labels: list[str]) -> None:
    for lab in labels:
        subprocess.run(["gh", "label", "create", lab, "--force"], capture_output=True)


def main() -> None:
    key, form_id = os.environ["JOTFORM_API_KEY"], os.environ["JOTFORM_FORM_ID"]
    schema = load_schema()
    labels = schema["form"]["labels"] + ["source:jotform"]
    ensure_labels(labels)
    done = existing_submission_ids()
    created = 0
    for sub in reversed(fetch_submissions(form_id, key)):  # plus anciennes d'abord
        sid = str(sub["id"])
        if sid in done:
            continue
        answers = to_answers(schema, sub)
        title = (f"{schema['form']['issue_title_prefix']}"
                 f"{answers.get('structure', '?')} – {answers.get('nom_traitement', '?')}")
        body = render_issue_body(schema, answers, JOTFORM_MARKER.format(sid))
        args = ["issue", "create", "--title", title, "--body", body]
        for lab in labels:
            args += ["--label", lab]
        print(gh(*args).strip())
        created += 1
    print(f"{created} nouvelle(s) fiche(s) importée(s) depuis Jotform.")


if __name__ == "__main__":
    main()
