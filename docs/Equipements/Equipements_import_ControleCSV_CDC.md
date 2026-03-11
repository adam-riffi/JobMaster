# Cahier des Charges — Equipements / Import / ControleCSV

**Domaine** : Equipements
**Type de flux** : Import
**Plateforme cible** : TD
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Validation structurelle des fichiers equipements avant chargement en staging : colonnes, encodage et non-vide.

---

## Sources souhaitées

- Répertoire : `C:\data\equipements\work`
- Masque : `^equipements_\d{8}\.csv$`

---

## Cibles souhaitées

- Fichiers invalides déplacés vers `C:\data\equipements\erreur`

---

## Règles de gestion

- Vérifier la présence des colonnes : `id_equipement,id_client,type_equipement,marque,modele,imei`
- Séparateur attendu : `|`
- Encodage : UTF-8
- Fichier non vide obligatoire.

---

## Fréquence souhaitée

Quotidien — après déplacement en zone de travail.

---

## Contraintes techniques

- Le répertoire d'erreur `C:\data\equipements\erreur` doit exister.
- Le flux doit échouer si au moins un fichier est invalide.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
