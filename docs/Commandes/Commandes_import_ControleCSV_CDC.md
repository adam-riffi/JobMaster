# Cahier des Charges — Commandes / Import / ControleCSV

**Domaine** : Commandes
**Type de flux** : Import
**Plateforme cible** : BQ
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Validation structurelle des fichiers commandes avant chargement en staging : colonnes, encodage et non-vide.

---

## Sources souhaitées

- Répertoire : `C:\data\commandes\work`
- Masque : `^commandes_\d{8}\.csv$`

---

## Cibles souhaitées

- Fichiers invalides déplacés vers `C:\data\commandes\erreur`

---

## Règles de gestion

- Vérifier la présence des colonnes : `id_commande,id_client,id_produit,date_commande,statut,canal_vente`
- Séparateur attendu : `;`
- Encodage : UTF-8
- Fichier non vide obligatoire.

---

## Fréquence souhaitée

Quotidien — après déplacement en zone de travail.

---

## Contraintes techniques

- Le répertoire d'erreur `C:\data\commandes\erreur` doit exister.
- Le flux doit échouer si au moins un fichier est invalide.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
