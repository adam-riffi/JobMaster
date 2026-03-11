# Cahier des Charges — Consommations / Aggregat / CumulGlissant

**Domaine** : Consommations
**Type de flux** : Aggregat
**Plateforme cible** : TD
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Calcul du cumul glissant sur 12 mois pour les indicateurs consommations — utilisé pour les analyses de tendance.

---

## Sources souhaitées

- Table historique : `£TD_HISTO.cdr_voix_histo`

---

## Cibles souhaitées

- Table agrégat glissante : `£TD_HISTO.cdr_aggr_journalier_client`

---

## Règles de gestion

- Calculer le cumul sur une fenêtre glissante de 12 mois.
- Recalcul complet du mois en cours à chaque run.
- Résultat trié chronologiquement.

---

## Fréquence souhaitée

Mensuel — après calcul des agrégats mensuels.

---

## Contraintes techniques

- Au moins 12 mois d'historique requis pour un résultat complet.
- Les mois manquants dans l'historique produisent un cumul partiel.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
