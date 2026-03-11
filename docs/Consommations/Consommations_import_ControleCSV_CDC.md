# Cahier des Charges — Consommations / Import / ControleCSV

**Domaine** : Consommations
**Type de flux** : Import
**Plateforme cible** : TD
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Validation structurelle des fichiers consommations avant chargement en staging : colonnes, encodage et non-vide.

---

## Sources souhaitées

- Répertoire : `C:\data\consommations\work`
- Masque : `^cdr_voix_\d{8}\.csv\.gz$`

---

## Cibles souhaitées

- Fichiers invalides déplacés vers `C:\data\consommations\erreur`

---

## Règles de gestion

- Vérifier la présence des colonnes : `id_cdr,id_client,date_appel,heure_appel,duree_secondes,type_trafic`
- Séparateur attendu : `|`
- Encodage : UTF-8
- Fichier non vide obligatoire.

---

## Fréquence souhaitée

Quotidien — après déplacement en zone de travail.

---

## Contraintes techniques

- Le répertoire d'erreur `C:\data\consommations\erreur` doit exister.
- Le flux doit échouer si au moins un fichier est invalide.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
