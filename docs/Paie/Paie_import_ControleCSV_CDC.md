# Cahier des Charges — Paie / Import / ControleCSV

**Domaine** : Paie
**Type de flux** : Import
**Plateforme cible** : TD
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Validation structurelle des fichiers paie avant chargement en staging : colonnes, encodage et non-vide.

---

## Sources souhaitées

- Répertoire : `C:\data\paie\work`
- Masque : `^paie_\d{6}\.csv$`

---

## Cibles souhaitées

- Fichiers invalides déplacés vers `C:\data\paie\erreur`

---

## Règles de gestion

- Vérifier la présence des colonnes : `id_paie,id_employe,periode,salaire_brut,cotisations_patronales,cotisations_salariales`
- Séparateur attendu : `;`
- Encodage : UTF-8
- Fichier non vide obligatoire.

---

## Fréquence souhaitée

Quotidien — après déplacement en zone de travail.

---

## Contraintes techniques

- Le répertoire d'erreur `C:\data\paie\erreur` doit exister.
- Le flux doit échouer si au moins un fichier est invalide.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
