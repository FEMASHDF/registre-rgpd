# FEMAS HDF – Registre RGPD en ligne

Formulaire **GitHub** + formulaire **Jotform** permettant aux équipes des structures
(MSP, cabinets de groupe, professionnels libéraux) de compléter le **registre des
activités de traitement (art. 30 RGPD)**. Le registre et le plan d'actions sont
compilés automatiquement.

Le questionnaire reprend les obligations décrites par la CNIL :
[RGPD et professionnels de santé libéraux](https://www.cnil.fr/fr/rgpd-et-professionnels-de-sante-liberaux-ce-que-vous-devez-savoir)
et le [référentiel « cabinets médicaux et paramédicaux »](https://www.cnil.fr/sites/default/files/atoms/files/referentiel_-_cabinet.pdf).

## 👉 Pour les MSP : créer votre registre en 3 minutes

Ce dépôt est un **modèle**. Chaque structure crée **son propre dépôt privé** : ses fiches
et son registre ne sont visibles que par elle (et par FEMAS HDF si elle l'invite).

1. Connectez-vous à GitHub (compte gratuit), puis cliquez sur **Use this template → Create a new repository**.
2. Nom : `registre-rgpd-<nom-de-la-msp>` · Visibilité : **Private** · **Create repository**.
3. Dans votre nouveau dépôt, onglet **Actions** : si un bandeau le demande, cliquez sur
   *I understand my workflows, go ahead and enable them*, puis lancez une fois
   **Compiler le registre RGPD → Run workflow** (crée les labels).
4. **Remplir** : onglet **Issues → New issue → Registre RGPD – fiche de traitement**
   (une fiche par activité de traitement). Invitez vos collègues : *Settings → Collaborators*.
5. **Télécharger le registre** : dossier `registre/` → **`registre.xlsx`** → bouton de
   téléchargement (↓). Le fichier Excel contient 3 onglets : *Synthèse*, *Registre*, *Plan d'actions*.
   Il est régénéré automatiquement à chaque fiche créée ou modifiée.
6. (Option) Pour être accompagné, invitez **FEMASHDF** en collaborateur.

Valider une fiche : remplacer le label `a-valider` par `valide`. Retirer un traitement : label `archive`.

---

## Fonctionnement

```
 Équipe avec compte GitHub ──► Issue Form « Registre RGPD »  ─┐
                                                              ├─► issues label « registre »
 Équipe sans compte GitHub ──► Formulaire Jotform ──(import ──┘        │
                                horaire, Action)                       ▼
                                          Action « Compiler le registre »
                                          ► registre/registre.xlsx (Excel)
                                          ► registre/REGISTRE.md
                                          ► registre/registre.csv
                                          ► registre/plan_actions.csv
```

* **Une fiche = une activité de traitement** (dossier patient, RDV, télétransmission,
  comptabilité, télémédecine, coordination, RH…).
* Les deux formulaires sont générés depuis une **source unique** : `schema/registre.yml`.
* Chaque case de sécurité ou d'obligation non cochée devient une **action** du plan
  (priorité haute pour HDS, authentification, habilitations, art. 28, AIPD/DPO…).
* Contrôle AIPD / DPO automatique : groupe + SI partagé + ≥ 10 000 patients/an (référentiel §11).
* Un second formulaire GitHub sert de **registre des violations de données** (art. 33.5).

### Couverture du référentiel CNIL

| § référentiel | Rubrique du formulaire |
|---|---|
| §3 Finalités | 2. Finalités (RDV, dossier, télémédecine, télétransmission, comptabilité, études internes) |
| §4 Bases légales | 3. Base légale + justification + exception art. 9 |
| §5 Données | 4. Catégories a) à h), qualité des données |
| §6 Destinataires, sous-traitants | 5 et 6. Accès, secrétariat, HDS (L.1111-8 CSP), plateforme RDV, 9 clauses art. 28 |
| §7 Conservation | 7. 5 ans actif + 15 ans archive, FSE 3 mois, suppression/anonymisation |
| §8 Information | 8. Affichage, dépliant, courriel RDV, contenu des mentions |
| §9 Droits | 8. Accès, rectification, effacement, limitation, opposition (hors dossier médical) |
| §10 Sécurité | 9. ~40 mesures en 9 catégories + conformité ANS (L.1110-4-1 CSP) + justification des écarts |
| §11 AIPD / DPO | 10. SI partagé, seuil 10 000 patients, AIPD, DPO |

## Mise en place côté FEMAS HDF (dépôt modèle + Jotform)

1. **Dépôt GitHub** : `FEMASHDF/registre-rgpd` (déjà créé).
   Dans *Settings → General → Features*, vérifier que *Issues* est activé.
   Dans *Settings → Actions → General → Workflow permissions*, choisir *Read and write*.
2. **Labels** : `registre`, `a-valider`, `valide`, `archive`, `source:jotform`,
   `violation`, `urgent` (déjà créés).
3. **Créer le formulaire Jotform** (compte Jotform hébergé en **UE** recommandé) :
   ```bash
   pip install -r requirements.txt
   export JOTFORM_API_KEY=...            # Jotform > Paramètres > API > clé "Full Access"
   export JOTFORM_API_BASE=https://eu-api.jotform.com
   python scripts/jotform_create_form.py
   ```
   Notez l'ID et l'URL affichés. Personnalisez ensuite le thème (logo FEMAS HDF) dans l'éditeur Jotform.
4. **Relier Jotform à GitHub** – *Settings → Secrets and variables → Actions* :
   * Secret `JOTFORM_API_KEY` = la clé API (une clé *Read Access* suffit ici)
   * Variable `JOTFORM_FORM_ID` = l'ID du formulaire
   * (option) Variable `JOTFORM_API_BASE` si compte non UE : `https://api.jotform.com`
5. Formulaire Jotform créé : https://eu.jotform.com/262895989918386 (ID `262895989918386`), déjà relié dans `config.yml`.
6. Lancer manuellement les Actions *Import Jotform -> issues* puis *Compiler le registre RGPD*
   pour vérifier.

## Utilisation au quotidien

* **Remplir** : *Issues → New issue → Registre RGPD – fiche de traitement*, ou le lien Jotform.
* **Valider** : le référent RGPD relit la fiche, puis remplace le label `a-valider` par `valide`.
* **Mettre à jour** : modifier l'issue (le registre se recompile) ; mettre à jour la date de la fiche.
* **Retirer** un traitement qui n'existe plus : label `archive`.
* **Consulter / exporter** : `registre/registre.xlsx` (Excel mis en forme, présentable à la CNIL),
  `registre/REGISTRE.md`, `registre/registre.csv` et `registre/plan_actions.csv`.

## Modifier le questionnaire

Éditer **uniquement** `schema/registre.yml`, puis :
```bash
python scripts/generate_issue_form.py      # régénère le formulaire GitHub
python scripts/jotform_create_form.py      # crée une nouvelle version Jotform (mettre à jour JOTFORM_FORM_ID)
```
Une Action vérifie que le formulaire GitHub est bien à jour du schéma.

## Précautions RGPD sur l'outil lui-même

* **Aucune donnée de patient** ne doit être saisie (une attestation est demandée) :
  le registre décrit les traitements, pas leur contenu.
* Le **modèle** `FEMASHDF/registre-rgpd` est public mais ne doit contenir **aucune fiche** :
  chaque MSP remplit son registre dans **son dépôt privé**. Double authentification recommandée.
* Jotform : compte hébergé UE, accès restreint, suppression des soumissions après import si souhaité.
* Le registre contient des noms de professionnels (responsables, rédacteurs) : GitHub et
  Jotform sont alors sous-traitants de FEMAS HDF / des structures — à inscrire dans le registre.

## Arborescence

```
schema/registre.yml                       source unique des questions
scripts/generate_issue_form.py            schéma -> Issue Form GitHub
scripts/jotform_create_form.py            schéma -> formulaire Jotform (API)
scripts/jotform_sync.py                   réponses Jotform -> issues GitHub
scripts/build_registre.py                 issues -> registre (Excel, MD, CSV) + plan d'actions
.github/ISSUE_TEMPLATE/01-registre-traitement.yml   (généré)
.github/ISSUE_TEMPLATE/02-violation-donnees.yml
.github/ISSUE_TEMPLATE/config.yml
.github/workflows/jotform-sync.yml        import horaire
.github/workflows/build-registre.yml      compilation à chaque modification d'issue
.github/workflows/check-schema.yml        contrôle de cohérence
registre/                                 registre compilé
```
