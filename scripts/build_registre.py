"""Compile les issues « registre » en registre RGPD + plan d'actions.

Sorties (dossier registre/) :
    REGISTRE.md        registre lisible (synthèse + fiches + plan d'actions)
    registre.csv       une ligne par activité de traitement
    plan_actions.csv   écarts détectés vs référentiel CNIL

Statut d'une fiche selon ses labels : "valide" -> Validée, sinon "À valider".
Les issues portant le label "archive" sont exclues.

Usage : python scripts/build_registre.py            (via gh CLI)
        python scripts/build_registre.py issues.json (export local)
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import subprocess
import sys

from common import ROOT, load_schema, parse_issue_body, questions

OUT_DIR = ROOT / "registre"
TODO_WORDS = ("à régulariser", "à corriger", "à formaliser", "à vérifier", "non réalisée",
              "non désigné", "à faire", "à compléter", "à mettre en place", "non vérifié",
              "– en cours")
PRIORITY_HIGH = {"hebergeur_hds", "sec_authentifier", "sec_habilitations", "aipd", "dpo_designe",
                 "contrat_art28", "transfert_hors_ue", "sec_sauvegarde"}


def load_issues() -> list[dict]:
    if len(sys.argv) > 1:
        return json.loads(open(sys.argv[1], encoding="utf-8").read())
    out = subprocess.run(["gh", "issue", "list", "--label", "registre", "--state", "all",
                          "--limit", "2000", "--json",
                          "number,title,body,state,labels,url,updatedAt"],
                         check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def detect_gaps(schema: dict, ans: dict) -> list[tuple[str, str, str]]:
    """-> [(priorité, thème, action)]"""
    gaps = []
    for f in questions(schema):
        prio = "Haute" if f["id"] in PRIORITY_HIGH else "Normale"
        val = ans.get(f["id"])
        if f["type"] == "checkboxes" and f.get("gap"):
            for opt in f["options"]:
                if opt not in (val or []):
                    gaps.append((prio, f["label"], f"Mettre en place : {opt}"))
        elif f["type"] == "dropdown" and isinstance(val, str):
            low = val.lower()
            if any(w in low for w in TODO_WORDS) or low.startswith("non –") or low == "non":
                if f["id"] in ("transfert_hors_ue", "si_partage"):
                    continue  # « Non » est ici la bonne réponse
                gaps.append((prio, f["label"], f"Réponse « {val} » : action requise"))
        elif f["type"] == "checkboxes" and f["id"] == "information":
            if any("Aucune" in v for v in (val or [])):
                gaps.append(("Haute", f["label"], "Mettre en place l'information des patients"))

    # Cohérence AIPD / DPO (référentiel §11 : groupe + SI partagé + ≥ 10 000 patients/an)
    if ans.get("si_partage") == "Oui" and ans.get("volume_patients") == "10 000 ou plus":
        if ans.get("aipd", "").startswith("Non requise"):
            gaps.append(("Haute", "AIPD", "AIPD nécessaire (SI partagé, ≥ 10 000 patients/an)"))
        if ans.get("dpo_designe", "").startswith("Non requis"):
            gaps.append(("Haute", "DPO", "DPO nécessaire (SI partagé, ≥ 10 000 patients/an)"))
    if ans.get("volume_patients") == "Ne sais pas":
        gaps.append(("Normale", "AIPD / DPO", "Évaluer la file active annuelle (seuil 10 000 patients)"))
    return gaps


def fmt(v) -> str:
    if isinstance(v, list):
        return "<br>".join(f"• {x}" for x in v) if v else "—"
    return (v or "—").replace("\n", "<br>")


def main() -> None:
    schema = load_schema()
    qs = questions(schema)
    fiches = []
    for issue in load_issues():
        labels = {lab["name"] for lab in issue.get("labels", [])}
        if "archive" in labels:
            continue
        ans = parse_issue_body(schema, issue["body"])
        fiches.append({"issue": issue, "ans": ans,
                       "statut": "Validée" if "valide" in labels else "À valider",
                       "gaps": detect_gaps(schema, ans)})
    fiches.sort(key=lambda x: (x["ans"].get("structure", ""), x["ans"].get("nom_traitement", "")))

    OUT_DIR.mkdir(exist_ok=True)
    today = dt.date.today().strftime("%d/%m/%Y")

    # ---- CSV registre
    with open(OUT_DIR / "registre.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["N° fiche", "Statut", "Lien"] + [f["label"] for f in qs] + ["Nb écarts"])
        for x in fiches:
            row = [x["issue"]["number"], x["statut"], x["issue"]["url"]]
            for f in qs:
                v = x["ans"].get(f["id"])
                row.append(" | ".join(v) if isinstance(v, list) else (v or ""))
            w.writerow(row + [len(x["gaps"])])

    # ---- CSV plan d'actions
    with open(OUT_DIR / "plan_actions.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["N° fiche", "Structure", "Traitement", "Priorité", "Thème", "Action",
                    "Responsable", "Échéance", "Fait le"])
        for x in fiches:
            for prio, theme, action in x["gaps"]:
                w.writerow([x["issue"]["number"], x["ans"].get("structure", ""),
                            x["ans"].get("nom_traitement", ""), prio, theme, action, "", "", ""])

    # ---- Markdown
    md = ["# FEMAS HDF – Registre des activités de traitement",
          "",
          f"_Registre des activités de traitement (art. 30 RGPD) – généré automatiquement le {today}._",
          "_Ce document doit pouvoir être présenté à la CNIL en cas de contrôle._",
          "",
          "## Synthèse", "",
          "| N° | Structure | Traitement | Responsable | Statut | Écarts | MAJ |",
          "|---|---|---|---|---|---|---|"]
    for x in fiches:
        a, i = x["ans"], x["issue"]
        md.append(f"| [#{i['number']}]({i['url']}) | {a.get('structure', '')} | {a.get('nom_traitement', '')} "
                  f"| {a.get('responsable', '')} | {x['statut']} | {len(x['gaps'])} | {a.get('date_maj', '')} |")
    if not fiches:
        md.append("| – | – | Aucune fiche | – | – | – | – |")

    md += ["", "## Fiches de traitement", ""]
    current = None
    for x in fiches:
        a, i = x["ans"], x["issue"]
        md += [f"### #{i['number']} – {a.get('nom_traitement', i['title'])}", "",
               f"Statut : **{x['statut']}** · [voir l'issue]({i['url']})", ""]
        for f in schema["fields"]:
            if f["type"] == "section":
                current = f["label"]
                md += [f"**{current}**", "", "| Rubrique | Réponse |", "|---|---|"]
                continue
            md.append(f"| {f['label']} | {fmt(a.get(f['id']))} |")
            nxt = schema["fields"].index(f) + 1
            if nxt >= len(schema["fields"]) or schema["fields"][nxt]["type"] == "section":
                md.append("")

    md += ["## Plan d'actions (écarts au référentiel CNIL)", ""]
    any_gap = False
    for x in fiches:
        if not x["gaps"]:
            continue
        any_gap = True
        md += [f"### #{x['issue']['number']} – {x['ans'].get('structure', '')} / "
               f"{x['ans'].get('nom_traitement', '')}", "",
               "| Priorité | Thème | Action |", "|---|---|---|"]
        for prio, theme, action in sorted(x["gaps"], key=lambda g: g[0] != "Haute"):
            md.append(f"| {prio} | {theme} | {action} |")
        md.append("")
    if not any_gap:
        md.append("Aucun écart détecté.")

    (OUT_DIR / "REGISTRE.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"{len(fiches)} fiche(s) compilée(s), "
          f"{sum(len(x['gaps']) for x in fiches)} action(s) au plan.")


if __name__ == "__main__":
    main()
