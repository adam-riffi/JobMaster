# Cahier des Charges — Produits / Export / ExportAPI

**Domaine** : Produits
**Type de flux** : Export
**Plateforme cible** : BQ
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Export du SOCLE produits vers l'API partenaire en format JSON pour synchronisation temps réel.

---

## Sources souhaitées

- Table SOCLE : `£BQ_SOCLE.produits`

---

## Cibles souhaitées

- API destination : `https://api.catalogue.telecom/produits/sync`
- Format : JSON

---

## Règles de gestion

- Extraire le SOCLE complet en JSON.
- Authentification Bearer Token sur l'API.
- Retry automatique en cas d'erreur HTTP 5xx.

---

## Fréquence souhaitée

Quotidien — après extraction CSV.

---

## Contraintes techniques

- Token API valide requis (configuré en variable d'environnement).
- Timeout API : 60 secondes par appel.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
