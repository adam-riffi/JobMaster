# Cahier des Charges — Incidents / Import / ControleCSV

**Domaine** : Incidents
**Type de flux** : Import
**Plateforme cible** : TD
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Validation structurelle des fichiers incidents avant chargement en staging : colonnes, encodage et non-vide.

---

## Sources souhaitées

- Répertoire : `C:\data\incidents\work`
- Masque : `^incidents_\d{8}\.csv$`

---

## Cibles souhaitées

- Fichiers invalides déplacés vers `C:\data\incidents\erreur`

---

## Règles de gestion

- Vérifier la présence des colonnes : `id_incident,id_site,date_debut,heure_debut,date_fin,severite`
- Séparateur attendu : `|`
- Encodage : UTF-8
- Fichier non vide obligatoire.

---

## Fréquence souhaitée

Quotidien — après déplacement en zone de travail.

---

## Contraintes techniques

- Le répertoire d'erreur `C:\data\incidents\erreur` doit exister.
- Le flux doit échouer si au moins un fichier est invalide.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
