# Cahier des Charges — Roaming / Import / ControleCSV

**Domaine** : Roaming
**Type de flux** : Import
**Plateforme cible** : TD
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Validation structurelle des fichiers roaming avant chargement en staging : colonnes, encodage et non-vide.

---

## Sources souhaitées

- Répertoire : `C:\data\roaming\work`
- Masque : `^roaming_\d{8}\.csv$`

---

## Cibles souhaitées

- Fichiers invalides déplacés vers `C:\data\roaming\erreur`

---

## Règles de gestion

- Vérifier la présence des colonnes : `id_roaming,id_client,date_debut,pays,operateur_partenaire,type_trafic`
- Séparateur attendu : `|`
- Encodage : UTF-8
- Fichier non vide obligatoire.

---

## Fréquence souhaitée

Quotidien — après déplacement en zone de travail.

---

## Contraintes techniques

- Le répertoire d'erreur `C:\data\roaming\erreur` doit exister.
- Le flux doit échouer si au moins un fichier est invalide.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
