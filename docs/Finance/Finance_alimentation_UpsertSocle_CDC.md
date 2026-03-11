# Cahier des Charges — Finance / Alimentation / UpsertSocle

**Domaine** : Finance
**Type de flux** : Alimentation
**Plateforme cible** : BQ
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Alimentation du SOCLE comptes_financiers depuis la staging par opération MERGE (UPSERT). Mise à jour des existants et insertion des nouveaux.

---

## Sources souhaitées

- Table staging : `£BQ_TMP.staging_finance`

---

## Cibles souhaitées

- Table SOCLE : `£BQ_SOCLE.comptes_financiers`
- Vue métier : `£BQ_VUES.comptes_financiers`

---

## Règles de gestion

- Clé de jointure : `id_ecriture`
- MERGE : UPDATE si existant, INSERT si nouveau.
- Mettre à jour `date_maj` à chaque modification.
- Créer/rafraîchir la vue métier après chaque run.

---

## Fréquence souhaitée

Quotidien — après chargement staging.

---

## Contraintes techniques

- La staging doit être peuplée (contrôle via FLAG avant merge).
- La vue ne doit jamais pointer sur une table vide.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
