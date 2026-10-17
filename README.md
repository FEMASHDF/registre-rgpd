# FEMAS HDF – Registre RGPD en ligne

Outil permettant à chaque structure (MSP, cabinet de groupe, professionnel libéral) de
constituer son **registre des activités de traitement (art. 30 RGPD)**, d'après la fiche CNIL
[RGPD et professionnels de santé libéraux](https://www.cnil.fr/fr/rgpd-et-professionnels-de-sante-liberaux-ce-que-vous-devez-savoir)
et le [référentiel « cabinets médicaux et paramédicaux »](https://www.cnil.fr/sites/default/files/atoms/files/referentiel_-_cabinet.pdf).

## 👉 Utiliser l'outil

**https://femashdf.github.io/registre-rgpd/**

1. Renseignez votre structure.
2. Ajoutez une fiche par activité de traitement (modèles proposés : dossier patient, RDV,
   télétransmission, comptabilité, télémédecine, coordination, personnel…).
3. Cliquez sur **Télécharger le registre Excel** : *Synthèse*, *Registre*, *Plan d'actions*.
4. Pour mettre à jour plus tard : **Importer mon registre Excel**, modifiez, re-téléchargez.

## Confidentialité

* Les réponses **ne quittent pas le navigateur** : aucune donnée n'est envoyée à GitHub ni
  à FEMAS HDF ; le fichier Excel est généré localement.
* Au téléchargement, seuls le **nom** et le **type de structure** sont transmis à un
  formulaire Jotform de FEMAS HDF (hébergé UE) pour suivre l'utilisation de l'outil.
* Un brouillon est conservé dans le navigateur (stockage local) ; le bouton
  *Effacer les données de ce navigateur* le supprime (à utiliser sur un poste partagé).
* Aucune donnée de patient ne doit être saisie.

## Contenu du questionnaire (référentiel CNIL)

| § référentiel | Rubrique |
|---|---|
| §3 Finalités | Finalités (RDV, dossier, télémédecine, télétransmission, comptabilité, études internes) |
| §4 Bases légales | Base légale + justification + exception art. 9 |
| §5 Données | Catégories a) à h), qualité des données |
| §6 Destinataires, sous-traitants | Accès, secrétariat, HDS (L.1111-8 CSP), plateforme RDV, 9 clauses art. 28 |
| §7 Conservation | 5 ans actif + 15 ans archive, FSE 3 mois, suppression/anonymisation |
| §8–9 Information, droits | Affichage, dépliant, courriel RDV ; accès, rectification, effacement, limitation, opposition |
| §10 Sécurité | ~40 mesures en 9 catégories + conformité ANS (L.1110-4-1 CSP) |
| §11 AIPD / DPO | SI partagé, seuil 10 000 patients/an, AIPD, DPO |

Toute case de sécurité ou d'obligation non cochée devient une **action** du plan
(priorité haute : HDS, authentification, habilitations, art. 28, sauvegardes, AIPD/DPO).

## Maintenance (FEMAS HDF)

Les questions sont définies dans `schema/registre.yml`. Après modification :
```bash
pip install -r requirements.txt
python scripts/generate_page.py      # régénère docs/index.html
```
Publication : GitHub Pages, branche `main`, dossier `/docs`.
Suivi d'utilisation : formulaire Jotform « FEMAS HDF – Suivi d'utilisation du registre RGPD »
(ID 262895568192373).
