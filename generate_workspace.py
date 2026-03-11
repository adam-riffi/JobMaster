#!/usr/bin/env python3
"""
generate_workspace.py
Génère un environnement de production fictif pour Aleister — domaine télécom.
Produit ~400 flux JobMaster (YAML + SQL) et ~400 CDCs (Markdown) dans docs/.

Usage : python generate_workspace.py
"""

import os
import shutil
from pathlib import Path

WORKSPACE_ROOT = Path("workspaces")
DOCS_ROOT      = Path("docs")

# ─────────────────────────────────────────────────────────────────────────────
# DÉPENDANCES CROSS-DOMAINE
# clé = domaine emprunteur, valeur = liste de (plateforme_source, table_socle, domaine_propriétaire)
# ─────────────────────────────────────────────────────────────────────────────
CROSS_REFS = {
    "Fraude":        [("TD", "cdr_voix",      "Consommations"),
                      ("BQ", "clients",        "Clients")],
    "Reseau":        [("TD", "incidents",      "Incidents"),
                      ("TD", "equipements",    "Equipements")],
    "Reporting":     [("BQ", "clients",        "Clients"),
                      ("BQ", "factures",       "Facturation"),
                      ("BQ", "contrats",       "Contrats"),
                      ("TD", "cdr_voix",       "Consommations")],
    "Finance":       [("BQ", "factures",       "Facturation"),
                      ("BQ", "paiements",      "Paiements"),
                      ("TD", "creances",       "Recouvrement")],
    "ServiceClient": [("BQ", "clients",        "Clients"),
                      ("BQ", "contrats",       "Contrats"),
                      ("TD", "incidents",      "Incidents")],
    "Marketing":     [("BQ", "clients",        "Clients"),
                      ("TD", "cdr_voix",       "Consommations"),
                      ("BQ", "commandes",      "Commandes")],
    "Ventes":        [("BQ", "clients",        "Clients"),
                      ("BQ", "produits",       "Produits")],
    "Equipements":   [("BQ", "clients",        "Clients")],
}

# ─────────────────────────────────────────────────────────────────────────────
# DÉFINITIONS DES DOMAINES (20)
# ─────────────────────────────────────────────────────────────────────────────
DOMAINS = [
    # ── BQ DOMAINS ────────────────────────────────────────────────────────────
    {
        "name": "Clients",
        "platform": "BQ",
        "desc": "Référentiel des abonnés et données personnelles client",
        "staging": "staging_clients",
        "socle": "clients",
        "histo": "clients_histo",
        "aggr": "clients_aggr_mensuel",
        "key_col": "id_client",
        "cols_bq": [("id_client","STRING NOT NULL"),("nom","STRING"),("prenom","STRING"),
                    ("email","STRING"),("telephone","STRING"),("date_naissance","DATE"),
                    ("segment","STRING"),("statut","STRING"),("date_maj","TIMESTAMP")],
        "file_mask": r"^clients_\d{8}\.csv$",
        "sep": ";", "encoding": "UTF-8",
        "sftp_in":  "sftp://crm-partner/clients/in",
        "sftp_out": "sftp://distribution/clients/out",
        "rep_in":   r"C:\data\clients\in",
        "rep_work": r"C:\data\clients\work",
        "rep_arch": r"C:\data\clients\archive",
        "rep_export":r"C:\data\clients\export",
        "rep_err":  r"C:\data\clients\erreur",
        "api_out":  "https://api.crm-partner.com/clients/push",
    },
    {
        "name": "Contrats",
        "platform": "BQ",
        "desc": "Contrats d'abonnement, offres souscrites et cycles de vie",
        "staging": "staging_contrats",
        "socle": "contrats",
        "histo": "contrats_histo",
        "aggr": "contrats_aggr_actifs_mensuel",
        "key_col": "id_contrat",
        "cols_bq": [("id_contrat","STRING NOT NULL"),("id_client","STRING"),
                    ("type_offre","STRING"),("technologie","STRING"),
                    ("date_debut","DATE"),("date_fin","DATE"),
                    ("statut","STRING"),("montant_mensuel","NUMERIC"),("date_maj","TIMESTAMP")],
        "file_mask": r"^contrats_\d{8}\.csv$",
        "sep": ";", "encoding": "UTF-8",
        "sftp_in":  "sftp://crm-partner/contrats/in",
        "sftp_out": "sftp://distribution/contrats/out",
        "rep_in":   r"C:\data\contrats\in",
        "rep_work": r"C:\data\contrats\work",
        "rep_arch": r"C:\data\contrats\archive",
        "rep_export":r"C:\data\contrats\export",
        "rep_err":  r"C:\data\contrats\erreur",
        "api_out":  None,
    },
    {
        "name": "Facturation",
        "platform": "BQ",
        "desc": "Factures émises, lignes de facturation et statuts de paiement",
        "staging": "staging_factures",
        "socle": "factures",
        "histo": "factures_histo",
        "aggr": "factures_aggr_mensuel_client",
        "key_col": "id_facture",
        "cols_bq": [("id_facture","STRING NOT NULL"),("id_client","STRING"),
                    ("id_contrat","STRING"),("periode","STRING"),
                    ("montant_ht","NUMERIC"),("montant_ttc","NUMERIC"),
                    ("tva","NUMERIC"),("statut_paiement","STRING"),("date_emission","DATE"),("date_maj","TIMESTAMP")],
        "file_mask": r"^factures_\d{8}\.csv$",
        "sep": ";", "encoding": "UTF-8",
        "sftp_in":  "sftp://billing-system/factures/in",
        "sftp_out": "sftp://distribution/factures/out",
        "rep_in":   r"C:\data\facturation\in",
        "rep_work": r"C:\data\facturation\work",
        "rep_arch": r"C:\data\facturation\archive",
        "rep_export":r"C:\data\facturation\export",
        "rep_err":  r"C:\data\facturation\erreur",
        "api_out":  None,
    },
    {
        "name": "Paiements",
        "platform": "BQ",
        "desc": "Règlements clients, modes de paiement et réconciliation bancaire",
        "staging": "staging_paiements",
        "socle": "paiements",
        "histo": "paiements_histo",
        "aggr": "paiements_aggr_mensuel",
        "key_col": "id_paiement",
        "cols_bq": [("id_paiement","STRING NOT NULL"),("id_facture","STRING"),
                    ("id_client","STRING"),("date_paiement","DATE"),
                    ("montant","NUMERIC"),("mode_paiement","STRING"),
                    ("statut","STRING"),("reference_bancaire","STRING"),("date_maj","TIMESTAMP")],
        "file_mask": r"^paiements_\d{8}\.csv$",
        "sep": ";", "encoding": "UTF-8",
        "sftp_in":  "sftp://banque-partner/paiements/in",
        "sftp_out": "sftp://distribution/paiements/out",
        "rep_in":   r"C:\data\paiements\in",
        "rep_work": r"C:\data\paiements\work",
        "rep_arch": r"C:\data\paiements\archive",
        "rep_export":r"C:\data\paiements\export",
        "rep_err":  r"C:\data\paiements\erreur",
        "api_out":  None,
    },
    {
        "name": "Produits",
        "platform": "BQ",
        "desc": "Catalogue des offres, options, équipements et tarifs",
        "staging": "staging_produits",
        "socle": "produits",
        "histo": "produits_histo",
        "aggr": "produits_aggr_ventes_mensuel",
        "key_col": "id_produit",
        "cols_bq": [("id_produit","STRING NOT NULL"),("libelle","STRING"),
                    ("type_produit","STRING"),("technologie","STRING"),
                    ("prix_ht","NUMERIC"),("prix_ttc","NUMERIC"),
                    ("actif","BOOL"),("date_lancement","DATE"),("date_maj","TIMESTAMP")],
        "file_mask": r"^produits_\d{8}\.csv$",
        "sep": ";", "encoding": "UTF-8",
        "sftp_in":  "sftp://catalogue-system/produits/in",
        "sftp_out": "sftp://distribution/produits/out",
        "rep_in":   r"C:\data\produits\in",
        "rep_work": r"C:\data\produits\work",
        "rep_arch": r"C:\data\produits\archive",
        "rep_export":r"C:\data\produits\export",
        "rep_err":  r"C:\data\produits\erreur",
        "api_out":  "https://api.catalogue.telecom/produits/sync",
    },
    {
        "name": "Commandes",
        "platform": "BQ",
        "desc": "Commandes client, cycle de vie et statuts de livraison",
        "staging": "staging_commandes",
        "socle": "commandes",
        "histo": "commandes_histo",
        "aggr": "commandes_aggr_journalier",
        "key_col": "id_commande",
        "cols_bq": [("id_commande","STRING NOT NULL"),("id_client","STRING"),
                    ("id_produit","STRING"),("date_commande","DATE"),
                    ("statut","STRING"),("canal_vente","STRING"),
                    ("montant_total","NUMERIC"),("date_livraison","DATE"),("date_maj","TIMESTAMP")],
        "file_mask": r"^commandes_\d{8}\.csv$",
        "sep": ";", "encoding": "UTF-8",
        "sftp_in":  "sftp://order-system/commandes/in",
        "sftp_out": "sftp://distribution/commandes/out",
        "rep_in":   r"C:\data\commandes\in",
        "rep_work": r"C:\data\commandes\work",
        "rep_arch": r"C:\data\commandes\archive",
        "rep_export":r"C:\data\commandes\export",
        "rep_err":  r"C:\data\commandes\erreur",
        "api_out":  None,
    },
    {
        "name": "Marketing",
        "platform": "BQ",
        "desc": "Campagnes marketing, segments clients et ciblage",
        "staging": "staging_campagnes",
        "socle": "campagnes",
        "histo": "campagnes_histo",
        "aggr": "campagnes_aggr_performance_mensuel",
        "key_col": "id_campagne",
        "cols_bq": [("id_campagne","STRING NOT NULL"),("code_segment","STRING"),
                    ("libelle","STRING"),("canal","STRING"),
                    ("date_debut","DATE"),("date_fin","DATE"),
                    ("budget","NUMERIC"),("nb_cibles","INT64"),("taux_conversion","FLOAT64"),("date_maj","TIMESTAMP")],
        "file_mask": r"^campagnes_\d{8}\.csv$",
        "sep": ";", "encoding": "UTF-8",
        "sftp_in":  "sftp://marketing-tool/campagnes/in",
        "sftp_out": "sftp://distribution/marketing/out",
        "rep_in":   r"C:\data\marketing\in",
        "rep_work": r"C:\data\marketing\work",
        "rep_arch": r"C:\data\marketing\archive",
        "rep_export":r"C:\data\marketing\export",
        "rep_err":  r"C:\data\marketing\erreur",
        "api_out":  "https://api.marketing-platform.com/push",
    },
    {
        "name": "Ventes",
        "platform": "BQ",
        "desc": "Actes de vente, commissionnement et performance commerciale",
        "staging": "staging_ventes",
        "socle": "ventes",
        "histo": "ventes_histo",
        "aggr": "ventes_aggr_mensuel_canal",
        "key_col": "id_vente",
        "cols_bq": [("id_vente","STRING NOT NULL"),("id_client","STRING"),
                    ("id_produit","STRING"),("id_commercial","STRING"),
                    ("date_vente","DATE"),("canal","STRING"),
                    ("montant","NUMERIC"),("commission","NUMERIC"),("statut","STRING"),("date_maj","TIMESTAMP")],
        "file_mask": r"^ventes_\d{8}\.csv$",
        "sep": ";", "encoding": "UTF-8",
        "sftp_in":  "sftp://crm-sales/ventes/in",
        "sftp_out": "sftp://distribution/ventes/out",
        "rep_in":   r"C:\data\ventes\in",
        "rep_work": r"C:\data\ventes\work",
        "rep_arch": r"C:\data\ventes\archive",
        "rep_export":r"C:\data\ventes\export",
        "rep_err":  r"C:\data\ventes\erreur",
        "api_out":  None,
    },
    {
        "name": "ServiceClient",
        "platform": "BQ",
        "desc": "Interactions client, réclamations, NPS et suivi satisfaction",
        "staging": "staging_interactions",
        "socle": "interactions",
        "histo": "interactions_histo",
        "aggr": "interactions_aggr_nps_mensuel",
        "key_col": "id_interaction",
        "cols_bq": [("id_interaction","STRING NOT NULL"),("id_client","STRING"),
                    ("date_interaction","DATE"),("canal_contact","STRING"),
                    ("motif","STRING"),("statut","STRING"),
                    ("duree_traitement","INT64"),("note_satisfaction","INT64"),("agent_id","STRING"),("date_maj","TIMESTAMP")],
        "file_mask": r"^interactions_\d{8}\.csv$",
        "sep": ";", "encoding": "UTF-8",
        "sftp_in":  "sftp://crm-support/interactions/in",
        "sftp_out": "sftp://distribution/service-client/out",
        "rep_in":   r"C:\data\service_client\in",
        "rep_work": r"C:\data\service_client\work",
        "rep_arch": r"C:\data\service_client\archive",
        "rep_export":r"C:\data\service_client\export",
        "rep_err":  r"C:\data\service_client\erreur",
        "api_out":  "https://api.crm.telecom/interactions/push",
    },
    {
        "name": "Reporting",
        "platform": "BQ",
        "desc": "Tableaux de bord transverses et KPIs consolidés multi-domaines",
        "staging": "staging_kpi_global",
        "socle": "kpi_global",
        "histo": "kpi_global_histo",
        "aggr": "reporting_aggr_mensuel_direction",
        "key_col": "id_kpi",
        "cols_bq": [("id_kpi","STRING NOT NULL"),("periode","STRING"),
                    ("domaine","STRING"),("indicateur","STRING"),
                    ("valeur","NUMERIC"),("unite","STRING"),
                    ("date_calcul","TIMESTAMP"),("date_maj","TIMESTAMP")],
        "file_mask": r"^kpi_\d{8}\.csv$",
        "sep": ";", "encoding": "UTF-8",
        "sftp_in":  "sftp://bi-platform/kpi/in",
        "sftp_out": "sftp://direction/reporting/out",
        "rep_in":   r"C:\data\reporting\in",
        "rep_work": r"C:\data\reporting\work",
        "rep_arch": r"C:\data\reporting\archive",
        "rep_export":r"C:\data\reporting\export",
        "rep_err":  r"C:\data\reporting\erreur",
        "api_out":  "https://api.bi.telecom/kpi/push",
    },
    # ── TD DOMAINS ────────────────────────────────────────────────────────────
    {
        "name": "Consommations",
        "platform": "TD",
        "desc": "Enregistrements CDR voix, data et SMS — volumétries de trafic",
        "staging": "staging_cdr_voix",
        "socle": "cdr_voix",
        "histo": "cdr_voix_histo",
        "aggr": "cdr_aggr_journalier_client",
        "key_col": "id_cdr",
        "cols_td": [("id_cdr","VARCHAR(36) NOT NULL"),("id_client","VARCHAR(20)"),
                    ("date_appel","DATE"),("heure_appel","TIME"),
                    ("duree_secondes","INTEGER"),("type_trafic","VARCHAR(10)"),
                    ("zone","VARCHAR(50)"),("montant","DECIMAL(10,4)"),
                    ("operateur_transit","VARCHAR(50)"),("date_maj","TIMESTAMP")],
        "file_mask": r"^cdr_voix_\d{8}\.csv\.gz$",
        "sep": "|", "encoding": "UTF-8",
        "sftp_in":  "sftp://mediation-platform/cdr/voix",
        "sftp_out": "sftp://distribution/conso/out",
        "rep_in":   r"C:\data\consommations\in",
        "rep_work": r"C:\data\consommations\work",
        "rep_arch": r"C:\data\consommations\archive",
        "rep_export":r"C:\data\consommations\export",
        "rep_err":  r"C:\data\consommations\erreur",
        "api_out":  None,
        "compressed": True,
    },
    {
        "name": "Roaming",
        "platform": "TD",
        "desc": "Consommations hors réseau national — accords inter-opérateurs",
        "staging": "staging_roaming",
        "socle": "roaming",
        "histo": "roaming_histo",
        "aggr": "roaming_aggr_mensuel_pays",
        "key_col": "id_roaming",
        "cols_td": [("id_roaming","VARCHAR(36) NOT NULL"),("id_client","VARCHAR(20)"),
                    ("date_debut","DATE"),("pays","VARCHAR(50)"),
                    ("operateur_partenaire","VARCHAR(100)"),("type_trafic","VARCHAR(10)"),
                    ("volume_mo","DECIMAL(12,3)"),("duree_secondes","INTEGER"),
                    ("cout_euros","DECIMAL(10,4)"),("date_maj","TIMESTAMP")],
        "file_mask": r"^roaming_\d{8}\.csv$",
        "sep": "|", "encoding": "UTF-8",
        "sftp_in":  "sftp://clearing-house/roaming/in",
        "sftp_out": "sftp://distribution/roaming/out",
        "rep_in":   r"C:\data\roaming\in",
        "rep_work": r"C:\data\roaming\work",
        "rep_arch": r"C:\data\roaming\archive",
        "rep_export":r"C:\data\roaming\export",
        "rep_err":  r"C:\data\roaming\erreur",
        "api_out":  None,
    },
    {
        "name": "Interconnexion",
        "platform": "TD",
        "desc": "Facturation inter-opérateurs — trafic entrant et sortant",
        "staging": "staging_interconnexion",
        "socle": "interconnexion",
        "histo": "interconnexion_histo",
        "aggr": "interconnexion_aggr_mensuel_operateur",
        "key_col": "id_interconnexion",
        "cols_td": [("id_interconnexion","VARCHAR(36) NOT NULL"),
                    ("operateur_source","VARCHAR(50)"),("operateur_cible","VARCHAR(50)"),
                    ("date_transit","DATE"),("type_trafic","VARCHAR(10)"),
                    ("volume_minutes","DECIMAL(12,2)"),("tarif_minute","DECIMAL(8,6)"),
                    ("montant_total","DECIMAL(12,2)"),("statut_facturation","VARCHAR(20)"),("date_maj","TIMESTAMP")],
        "file_mask": r"^interconnexion_\d{8}\.csv$",
        "sep": "|", "encoding": "UTF-8",
        "sftp_in":  "sftp://interconnexion-clearing/in",
        "sftp_out": "sftp://distribution/interconnexion/out",
        "rep_in":   r"C:\data\interconnexion\in",
        "rep_work": r"C:\data\interconnexion\work",
        "rep_arch": r"C:\data\interconnexion\archive",
        "rep_export":r"C:\data\interconnexion\export",
        "rep_err":  r"C:\data\interconnexion\erreur",
        "api_out":  None,
    },
    {
        "name": "Fraude",
        "platform": "TD",
        "desc": "Détection de fraude, alertes et blocages — scoring risque client",
        "staging": "staging_alertes_fraude",
        "socle": "alertes_fraude",
        "histo": "alertes_fraude_histo",
        "aggr": "fraude_aggr_mensuel_type",
        "key_col": "id_alerte",
        "cols_td": [("id_alerte","VARCHAR(36) NOT NULL"),("id_client","VARCHAR(20)"),
                    ("date_detection","DATE"),("type_fraude","VARCHAR(50)"),
                    ("score_risque","DECIMAL(5,2)"),("montant_suspect","DECIMAL(12,2)"),
                    ("statut","VARCHAR(20)"),("agent_investigation","VARCHAR(50)"),
                    ("date_cloture","DATE"),("date_maj","TIMESTAMP")],
        "file_mask": r"^fraude_alertes_\d{8}\.csv$",
        "sep": "|", "encoding": "UTF-8",
        "sftp_in":  "sftp://fraud-engine/alertes/in",
        "sftp_out": "sftp://distribution/fraude/out",
        "rep_in":   r"C:\data\fraude\in",
        "rep_work": r"C:\data\fraude\work",
        "rep_arch": r"C:\data\fraude\archive",
        "rep_export":r"C:\data\fraude\export",
        "rep_err":  r"C:\data\fraude\erreur",
        "api_out":  None,
    },
    {
        "name": "Recouvrement",
        "platform": "TD",
        "desc": "Gestion des créances, relances clients et contentieux",
        "staging": "staging_creances",
        "socle": "creances",
        "histo": "creances_histo",
        "aggr": "recouvrement_aggr_mensuel_statut",
        "key_col": "id_creance",
        "cols_td": [("id_creance","VARCHAR(36) NOT NULL"),("id_client","VARCHAR(20)"),
                    ("id_facture","VARCHAR(36)"),("date_echeance","DATE"),
                    ("montant_du","DECIMAL(12,2)"),("montant_recouvre","DECIMAL(12,2)"),
                    ("nb_relances","INTEGER"),("statut","VARCHAR(30)"),
                    ("date_contentieux","DATE"),("date_maj","TIMESTAMP")],
        "file_mask": r"^creances_\d{8}\.csv$",
        "sep": "|", "encoding": "UTF-8",
        "sftp_in":  "sftp://recouvrement-system/creances/in",
        "sftp_out": "sftp://distribution/recouvrement/out",
        "rep_in":   r"C:\data\recouvrement\in",
        "rep_work": r"C:\data\recouvrement\work",
        "rep_arch": r"C:\data\recouvrement\archive",
        "rep_export":r"C:\data\recouvrement\export",
        "rep_err":  r"C:\data\recouvrement\erreur",
        "api_out":  None,
    },
    {
        "name": "Portabilite",
        "platform": "TD",
        "desc": "Portabilité des numéros — flux entrants et sortants inter-opérateurs",
        "staging": "staging_portages",
        "socle": "portages",
        "histo": "portages_histo",
        "aggr": "portabilite_aggr_mensuel_operateur",
        "key_col": "id_portage",
        "cols_td": [("id_portage","VARCHAR(36) NOT NULL"),("msisdn","VARCHAR(15)"),
                    ("operateur_source","VARCHAR(50)"),("operateur_cible","VARCHAR(50)"),
                    ("date_demande","DATE"),("date_portage","DATE"),
                    ("statut","VARCHAR(20)"),("motif_rejet","VARCHAR(200)"),
                    ("type_portage","VARCHAR(20)"),("date_maj","TIMESTAMP")],
        "file_mask": r"^portages_\d{8}\.csv$",
        "sep": "|", "encoding": "UTF-8",
        "sftp_in":  "sftp://porting-clearinghouse/portages/in",
        "sftp_out": "sftp://distribution/portabilite/out",
        "rep_in":   r"C:\data\portabilite\in",
        "rep_work": r"C:\data\portabilite\work",
        "rep_arch": r"C:\data\portabilite\archive",
        "rep_export":r"C:\data\portabilite\export",
        "rep_err":  r"C:\data\portabilite\erreur",
        "api_out":  None,
    },
    {
        "name": "Reseau",
        "platform": "TD",
        "desc": "Infrastructure réseau — sites, antennes, capacités et trafic",
        "staging": "staging_sites_reseau",
        "socle": "sites_reseau",
        "histo": "sites_reseau_histo",
        "aggr": "reseau_aggr_kpi_journalier",
        "key_col": "id_site",
        "cols_td": [("id_site","VARCHAR(20) NOT NULL"),("code_site","VARCHAR(20)"),
                    ("technologie","VARCHAR(10)"),("region","VARCHAR(50)"),
                    ("latitude","DECIMAL(10,6)"),("longitude","DECIMAL(10,6)"),
                    ("capacite_max_mo","DECIMAL(12,2)"),("trafic_actuel_mo","DECIMAL(12,2)"),
                    ("statut","VARCHAR(20)"),("date_maj","TIMESTAMP")],
        "file_mask": r"^sites_reseau_\d{8}\.csv$",
        "sep": "|", "encoding": "UTF-8",
        "sftp_in":  "sftp://oss-network/sites/in",
        "sftp_out": "sftp://distribution/reseau/out",
        "rep_in":   r"C:\data\reseau\in",
        "rep_work": r"C:\data\reseau\work",
        "rep_arch": r"C:\data\reseau\archive",
        "rep_export":r"C:\data\reseau\export",
        "rep_err":  r"C:\data\reseau\erreur",
        "api_out":  None,
    },
    {
        "name": "Equipements",
        "platform": "TD",
        "desc": "Équipements clients — box, terminaux mobiles, modems et CPE",
        "staging": "staging_equipements",
        "socle": "equipements",
        "histo": "equipements_histo",
        "aggr": "equipements_aggr_parc_mensuel",
        "key_col": "id_equipement",
        "cols_td": [("id_equipement","VARCHAR(36) NOT NULL"),("id_client","VARCHAR(20)"),
                    ("type_equipement","VARCHAR(30)"),("marque","VARCHAR(50)"),
                    ("modele","VARCHAR(100)"),("imei","VARCHAR(20)"),
                    ("date_installation","DATE"),("statut","VARCHAR(20)"),
                    ("version_firmware","VARCHAR(50)"),("date_maj","TIMESTAMP")],
        "file_mask": r"^equipements_\d{8}\.csv$",
        "sep": "|", "encoding": "UTF-8",
        "sftp_in":  "sftp://device-management/equipements/in",
        "sftp_out": "sftp://distribution/equipements/out",
        "rep_in":   r"C:\data\equipements\in",
        "rep_work": r"C:\data\equipements\work",
        "rep_arch": r"C:\data\equipements\archive",
        "rep_export":r"C:\data\equipements\export",
        "rep_err":  r"C:\data\equipements\erreur",
        "api_out":  None,
    },
    {
        "name": "Paie",
        "platform": "TD",
        "desc": "Paie des employés, cotisations sociales et virements salaires",
        "staging": "staging_paie",
        "socle": "paie_employes",
        "histo": "paie_histo",
        "aggr": "paie_aggr_mensuel_direction",
        "key_col": "id_paie",
        "cols_td": [("id_paie","VARCHAR(36) NOT NULL"),("id_employe","VARCHAR(20)"),
                    ("periode","VARCHAR(7)"),("salaire_brut","DECIMAL(10,2)"),
                    ("cotisations_patronales","DECIMAL(10,2)"),("cotisations_salariales","DECIMAL(10,2)"),
                    ("salaire_net","DECIMAL(10,2)"),("mode_paiement","VARCHAR(20)"),
                    ("date_virement","DATE"),("date_maj","TIMESTAMP")],
        "file_mask": r"^paie_\d{6}\.csv$",
        "sep": ";", "encoding": "UTF-8",
        "sftp_in":  "sftp://sirh-system/paie/in",
        "sftp_out": "sftp://distribution/paie/out",
        "rep_in":   r"C:\data\paie\in",
        "rep_work": r"C:\data\paie\work",
        "rep_arch": r"C:\data\paie\archive",
        "rep_export":r"C:\data\paie\export",
        "rep_err":  r"C:\data\paie\erreur",
        "api_out":  None,
    },
    {
        "name": "Incidents",
        "platform": "TD",
        "desc": "Incidents réseau, pannes, maintenances et tickets de résolution",
        "staging": "staging_incidents",
        "socle": "incidents",
        "histo": "incidents_histo",
        "aggr": "incidents_aggr_journalier_severite",
        "key_col": "id_incident",
        "cols_td": [("id_incident","VARCHAR(36) NOT NULL"),("id_site","VARCHAR(20)"),
                    ("date_debut","DATE"),("heure_debut","TIME"),
                    ("date_fin","DATE"),("severite","VARCHAR(10)"),
                    ("type_incident","VARCHAR(50)"),("zones_impactees","VARCHAR(500)"),
                    ("nb_clients_touches","INTEGER"),("statut","VARCHAR(20)"),("date_maj","TIMESTAMP")],
        "file_mask": r"^incidents_\d{8}\.csv$",
        "sep": "|", "encoding": "UTF-8",
        "sftp_in":  "sftp://noc-platform/incidents/in",
        "sftp_out": "sftp://distribution/incidents/out",
        "rep_in":   r"C:\data\incidents\in",
        "rep_work": r"C:\data\incidents\work",
        "rep_arch": r"C:\data\incidents\archive",
        "rep_export":r"C:\data\incidents\export",
        "rep_err":  r"C:\data\incidents\erreur",
        "api_out":  None,
    },
    {
        "name": "Finance",
        "platform": "BQ",
        "desc": "Consolidation financière transverse — P&L, trésorerie et reporting IFRS",
        "staging": "staging_finance",
        "socle": "comptes_financiers",
        "histo": "comptes_financiers_histo",
        "aggr": "finance_aggr_mensuel_rubrique",
        "key_col": "id_ecriture",
        "cols_bq": [("id_ecriture","STRING NOT NULL"),("periode","STRING"),
                    ("rubrique","STRING"),("sous_rubrique","STRING"),
                    ("montant_debit","NUMERIC"),("montant_credit","NUMERIC"),
                    ("solde","NUMERIC"),("devise","STRING"),("date_comptable","DATE"),("date_maj","TIMESTAMP")],
        "file_mask": r"^ecritures_\d{8}\.csv$",
        "sep": ";", "encoding": "UTF-8",
        "sftp_in":  "sftp://erp-finance/ecritures/in",
        "sftp_out": "sftp://distribution/finance/out",
        "rep_in":   r"C:\data\finance\in",
        "rep_work": r"C:\data\finance\work",
        "rep_arch": r"C:\data\finance\archive",
        "rep_export":r"C:\data\finance\export",
        "rep_err":  r"C:\data\finance\erreur",
        "api_out":  None,
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# UTILITAIRES
# ─────────────────────────────────────────────────────────────────────────────

def w(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def pf(d): return d["platform"]
def ext(d): return "gql" if pf(d) == "BQ" else "dql"
def pfx(d): return "£BQ" if pf(d) == "BQ" else "£TD"
def dn(d): return d["name"]
def staging(d): return d["staging"]
def socle(d): return d["socle"]
def histo(d): return d["histo"]
def aggr_t(d): return d["aggr"]
def key(d): return d["key_col"]
def col_names(d):
    if pf(d) == "BQ":
        return [c[0] for c in d.get("cols_bq", [])]
    else:
        return [c[0] for c in d.get("cols_td", [])]

def col_defs_sql(d):
    if pf(d) == "BQ":
        return "\n".join(f"  {c[0]:<35} {c[1]}" for c in d.get("cols_bq", []))
    else:
        return "\n".join(f"  {c[0]:<35} {c[1]}," for c in d.get("cols_td", []))[:-1]

def cross_sql_snippet(d):
    name = dn(d)
    if name not in CROSS_REFS:
        return ""
    lines = []
    for (plat, tbl, owner) in CROSS_REFS[name]:
        prefix = "£BQ" if plat == "BQ" else "£TD"
        lines.append(f"-- Référence cross-domaine : {prefix}_SOCLE.{tbl} (domaine {owner})")
        lines.append(f"LEFT JOIN {prefix}_SOCLE.{tbl} ext_{tbl} ON t.{key(d)} = ext_{tbl}.{key(d)}")
    return "\n".join(lines)

# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATES YAML
# ─────────────────────────────────────────────────────────────────────────────

def yaml_import_rapatriement(d):
    n = dn(d)
    return f"""script:
  id_script: {n}_Import_RapatriementSFTP
  description: Rapatriement des fichiers {n.lower()} depuis le SFTP source vers la zone d'entrée

  parametres_env:
    SFTP_SOURCE: {d["sftp_in"]}
    REP_IN: {d["rep_in"]}

  jobs:
    - job_id: job.externe.import
      description: Récupère les fichiers {n.lower()} depuis le SFTP
      parametres:
        Source: £SFTP_SOURCE
        Cible: £REP_IN
        Type: sftp
"""

def yaml_import_deplacement(d):
    n = dn(d)
    return f"""script:
  id_script: {n}_Import_DeplacementTravail
  description: Déplacement des fichiers {n.lower()} de la zone d'entrée vers la zone de travail

  parametres_env:
    REP_IN: {d["rep_in"]}
    REP_WORK: {d["rep_work"]}
    MASQUE_{n.upper()}: "{d["file_mask"]}"

  jobs:
    - job_id: job.fichier.manipulation
      description: Déplace les fichiers vers la zone de travail
      parametres:
        Source: £REP_IN
        Cible: £REP_WORK
        Masque: £MASQUE_{n.upper()}
        Mode: deplacement
"""

def yaml_import_decompression(d):
    n = dn(d)
    mask_gz = d["file_mask"]
    mask_csv = mask_gz.replace(r"\.gz", "")
    return f"""script:
  id_script: {n}_Import_Decompression
  description: Décompression des fichiers {n.lower()} compressés avant traitement

  parametres_env:
    REP_IN: {d["rep_in"]}
    REP_WORK: {d["rep_work"]}
    MASQUE_GZ: "{mask_gz}"
    MASQUE_CSV: "{mask_csv}"

  jobs:
    - job_id: job.fichier.decompression
      description: Décompresse les archives {n.lower()}
      parametres:
        Source: £REP_IN
        Cible: £REP_WORK
        Masque: £MASQUE_GZ
        Format: gzip

    - job_id: job.fichier.manipulation
      description: Déplace les CSV décompressés vers la zone de travail
      parametres:
        Source: £REP_IN
        Cible: £REP_WORK
        Masque: £MASQUE_CSV
        Mode: deplacement
"""

def yaml_import_controle(d):
    n = dn(d)
    cols = ",".join(col_names(d)[:6])
    return f"""script:
  id_script: {n}_Import_ControleCSV
  description: Validation structurelle des fichiers {n.lower()} avant chargement en staging

  parametres_env:
    REP_WORK: {d["rep_work"]}
    REP_ERR: {d["rep_err"]}
    MASQUE_{n.upper()}: "{d["file_mask"].replace(r'\.gz', '')}"

  jobs:
    - job_id: job.fichier.controle
      description: Valide le format et les colonnes des fichiers {n.lower()}
      parametres:
        Source: £REP_WORK
        Masque: £MASQUE_{n.upper()}
        Colonnes: "{cols}"
        Separateur: "{d["sep"]}"
        Encodage: {d["encoding"]}
        NonVide: true
        RepertoireErreur: £REP_ERR
"""

def yaml_import_batch(d):
    n = dn(d)
    p = pf(d)
    e = ext(d)
    return f"""script:
  id_script: {n}_Import_TraitementBatch
  description: Chargement en masse des fichiers {n.lower()} en staging puis archivage

  parametres_env:
    REP_WORK: {d["rep_work"]}
    REP_ARCH: {d["rep_arch"]}
    MASQUE_{n.upper()}: "{d["file_mask"].replace(r'\.gz', '')}"
    TBL_STAGING: {pfx(d)}_TMP.{staging(d)}

  jobs:
    - job_id: job.fichier.comptage
      description: Compte les fichiers à traiter
      parametres:
        Source: £REP_WORK
        Masque: £MASQUE_{n.upper()}
        Variable: NB_FICHIERS_{n.upper()}

    - job_id: job.conditionnelle.si
      description: Lance le batch uniquement si des fichiers sont présents
      parametres:
        Variable: NB_FICHIERS_{n.upper()}
        Valeur: "0"

    - job_id: job.process.batch
      description: Charge la staging depuis tous les fichiers puis archive
      parametres:
        Source: £REP_WORK
        SAS: £REP_WORK
        Archive: £REP_ARCH
      jobs:
        - job_id: job.run.sql
          description: Charge les fichiers dans la table staging {p}
          parametres:
            Plateforme: {p}
            Requete: {n}_import_chargement_staging.{e}

        - job_id: job.fichier.manipulation
          description: Archive les fichiers traités
          parametres:
            Source: £REP_WORK
            Cible: £REP_ARCH
            Masque: £MASQUE_{n.upper()}
            Mode: deplacement

    - job_id: job.fichier.effacement
      description: Purge les archives de plus de 3 mois
      parametres:
        Source: £REP_ARCH
        Duree: 3
"""

def yaml_install_staging(d):
    n = dn(d)
    p = pf(d)
    e = ext(d)
    return f"""script:
  id_script: {n}_Installation_CreationTableStaging
  description: Création initiale de la table staging {staging(d)} ({p})

  parametres_env:
    TBL_STAGING: {pfx(d)}_TMP.{staging(d)}

  jobs:
    - job_id: job.run.sql
      description: Crée la table staging {staging(d)} sur {p}
      parametres:
        Plateforme: {p}
        Requete: {n}_installation_creation_table_staging.{e}
"""

def yaml_alim_upsert(d):
    n = dn(d)
    p = pf(d)
    e = ext(d)
    return f"""script:
  id_script: {n}_Alimentation_UpsertSocle
  description: Alimentation du SOCLE {socle(d)} depuis la staging par MERGE/UPSERT

  parametres_env:
    TBL_STAGING: {pfx(d)}_TMP.{staging(d)}
    TBL_SOCLE: {pfx(d)}_SOCLE.{socle(d)}

  jobs:
    - job_id: job.run.sql
      description: Vérifie que la staging contient des données
      parametres:
        Plateforme: {p}
        Requete: {n}_alimentation_check_staging.{e}
        Variable: FLAG_STAGING_{n.upper()}

    - job_id: job.conditionnelle.si
      description: Upsert uniquement si la staging est peuplée
      parametres:
        Variable: FLAG_STAGING_{n.upper()}
        Valeur: "OUI"
      jobs:
        - job_id: job.run.sql
          description: MERGE staging → SOCLE {socle(d)}
          parametres:
            Plateforme: {p}
            Requete: {n}_alimentation_upsert_socle.{e}

        - job_id: job.run.create_view
          description: Rafraîchit la vue métier {socle(d)}
          parametres:
            Plateforme: {p}
            Table: £TBL_SOCLE
"""

def yaml_alim_transfert(d):
    """Flux avec job.run.transfert pour les domaines ayant des cross-refs cross-plateforme."""
    n = dn(d)
    p = pf(d)
    e = ext(d)
    other_pf = "BQ" if p == "TD" else "TD"
    other_pfx = "£BQ" if p == "TD" else "£TD"
    return f"""script:
  id_script: {n}_Alimentation_EnrichissementTransverse
  description: Enrichissement du SOCLE {socle(d)} avec données cross-domaine via transfert

  parametres_env:
    TBL_SOCLE: {pfx(d)}_SOCLE.{socle(d)}
    TBL_TMP_ENRICHI: {pfx(d)}_TMP.{socle(d)}_enrichi

  jobs:
    - job_id: job.run.sql
      description: Prépare la table enrichie en croisant avec données transverses
      parametres:
        Plateforme: {p}
        Requete: {n}_alimentation_enrichissement_transverse.{e}

    - job_id: job.run.transfert
      description: Transfère les données enrichies vers la plateforme cible
      parametres:
        PlateformeSource: {p}
        TableSource: £TBL_TMP_ENRICHI
        PlateformeCible: {other_pf}
        TableCible: {other_pfx}_TMP.{socle(d)}_enrichi_sync
        Mode: FULL
"""

def yaml_alim_parallele(d):
    n = dn(d)
    p = pf(d)
    e = ext(d)
    return f"""script:
  id_script: {n}_Alimentation_ChargementsParalleles
  description: Chargement parallèle du SOCLE et de la table historique {n.lower()}

  parametres_env:
    TBL_SOCLE: {pfx(d)}_SOCLE.{socle(d)}
    TBL_HISTO: {pfx(d)}_HISTO.{histo(d)}

  jobs:
    - job_id: job.process.parallele
      description: Alimente SOCLE et HISTO simultanément
      jobs:
        - job_id: job.run.sql
          description: Upsert SOCLE {socle(d)}
          parametres:
            Plateforme: {p}
            Requete: {n}_alimentation_upsert_socle.{e}

        - job_id: job.run.sql
          description: Insert historique {histo(d)}
          parametres:
            Plateforme: {p}
            Requete: {n}_alimentation_insert_histo.{e}
"""

def yaml_install_socle(d):
    n = dn(d)
    p = pf(d)
    e = ext(d)
    return f"""script:
  id_script: {n}_Installation_CreationTableSocle
  description: Création initiale de la table SOCLE {socle(d)} ({p})

  parametres_env:
    TBL_SOCLE: {pfx(d)}_SOCLE.{socle(d)}

  jobs:
    - job_id: job.run.sql
      description: Crée la table SOCLE {socle(d)} sur {p}
      parametres:
        Plateforme: {p}
        Requete: {n}_installation_creation_table_socle.{e}
"""

def yaml_export_extraction(d):
    n = dn(d)
    p = pf(d)
    e = ext(d)
    return f"""script:
  id_script: {n}_Export_ExtractionCSV
  description: Extraction du SOCLE {socle(d)} vers fichiers CSV datés

  parametres_env:
    TBL_SOCLE: {pfx(d)}_SOCLE.{socle(d)}
    REP_EXPORT: {d["rep_export"]}
    NOM_FICHIER: {n.lower()}_£DATE.csv

  jobs:
    - job_id: job.table.extraction
      description: Extrait la table {socle(d)} en CSV
      parametres:
        Plateforme: {p}
        TableSource: £TBL_SOCLE
        Destination: £REP_EXPORT
        NomFichier: £NOM_FICHIER
        Format: csv
"""

def yaml_export_sftp(d):
    n = dn(d)
    return f"""script:
  id_script: {n}_Export_EnvoiSFTP
  description: Envoi des fichiers CSV {n.lower()} vers le SFTP de distribution

  parametres_env:
    REP_EXPORT: {d["rep_export"]}
    SFTP_DEST: {d["sftp_out"]}
    MASQUE_EXPORT: "^{n.lower()}_\\\\d{{8}}\\\\.csv$"

  jobs:
    - job_id: job.fichier.comptage
      description: Vérifie qu'il y a des fichiers à envoyer
      parametres:
        Source: £REP_EXPORT
        Masque: £MASQUE_EXPORT
        Variable: NB_EXPORT_{n.upper()}

    - job_id: job.conditionnelle.si
      description: Envoie uniquement si des fichiers sont disponibles
      parametres:
        Variable: NB_EXPORT_{n.upper()}
        Valeur: "0"

    - job_id: job.externe.export
      description: Envoie les CSV vers le SFTP de distribution
      parametres:
        Source: £REP_EXPORT
        Cible: £SFTP_DEST
        Type: sftp

    - job_id: job.fichier.effacement
      description: Purge les exports de plus de 1 mois
      parametres:
        Source: £REP_EXPORT
        Duree: 1
"""

def yaml_export_api(d):
    n = dn(d)
    p = pf(d)
    e = ext(d)
    return f"""script:
  id_script: {n}_Export_ExportAPI
  description: Export du SOCLE {socle(d)} vers l'API partenaire via extraction JSON

  parametres_env:
    TBL_SOCLE: {pfx(d)}_SOCLE.{socle(d)}
    REP_EXPORT: {d["rep_export"]}
    API_DEST: {d["api_out"]}
    NOM_FICHIER: {n.lower()}_api_£DATETIME.json

  jobs:
    - job_id: job.table.extraction
      description: Extrait le SOCLE {socle(d)} en JSON
      parametres:
        Plateforme: {p}
        TableSource: £TBL_SOCLE
        Destination: £REP_EXPORT
        NomFichier: £NOM_FICHIER
        Format: json

    - job_id: job.externe.export
      description: Pousse le JSON vers l'API partenaire
      parametres:
        Source: £REP_EXPORT
        Cible: £API_DEST
        Type: api
"""

def yaml_aggr_journalier(d):
    n = dn(d)
    p = pf(d)
    e = ext(d)
    return f"""script:
  id_script: {n}_Aggregat_JournalierSocle
  description: Agrégation journalière du SOCLE {socle(d)} vers l'historique

  parametres_env:
    TBL_SOCLE: {pfx(d)}_SOCLE.{socle(d)}
    TBL_HISTO: {pfx(d)}_HISTO.{histo(d)}
    PERIODE: £DATE

  jobs:
    - job_id: job.run.sql
      description: Vérifie que le SOCLE a été alimenté aujourd'hui
      parametres:
        Plateforme: {p}
        Requete: {n}_aggregat_check_socle_jour.{e}
        Variable: FLAG_SOCLE_{n.upper()}

    - job_id: job.conditionnelle.si
      description: Agrège uniquement si le SOCLE est à jour
      parametres:
        Variable: FLAG_SOCLE_{n.upper()}
        Valeur: "OUI"
      jobs:
        - job_id: job.run.sql
          description: Insère les données du jour dans l'historique
          parametres:
            Plateforme: {p}
            Requete: {n}_aggregat_insert_journalier.{e}
"""

def yaml_aggr_mensuel(d):
    n = dn(d)
    p = pf(d)
    e = ext(d)
    return f"""script:
  id_script: {n}_Aggregat_MensuelParSegment
  description: Agrégation mensuelle du SOCLE {socle(d)} par segment métier

  parametres_env:
    TBL_SOCLE: {pfx(d)}_SOCLE.{socle(d)}
    TBL_AGGR: {pfx(d)}_HISTO.{aggr_t(d)}
    PERIODE: £YEAR£MONTH

  jobs:
    - job_id: job.run.sql
      description: Supprime les agrégats du mois courant avant recalcul
      parametres:
        Plateforme: {p}
        Requete: {n}_aggregat_delete_mensuel.{e}

    - job_id: job.run.sql
      description: Calcule et insère les agrégats mensuels par segment
      parametres:
        Plateforme: {p}
        Requete: {n}_aggregat_insert_mensuel_segment.{e}
"""

def yaml_aggr_cumul(d):
    n = dn(d)
    p = pf(d)
    e = ext(d)
    return f"""script:
  id_script: {n}_Aggregat_CumulGlissant
  description: Calcul des cumuls glissants sur 12 mois pour le domaine {n.lower()}

  parametres_env:
    TBL_HISTO: {pfx(d)}_HISTO.{histo(d)}
    TBL_AGGR: {pfx(d)}_HISTO.{aggr_t(d)}

  jobs:
    - job_id: job.run.sql
      description: Recalcule le cumul glissant 12 mois
      parametres:
        Plateforme: {p}
        Requete: {n}_aggregat_cumul_glissant_12m.{e}
"""

def yaml_install_aggr(d):
    n = dn(d)
    p = pf(d)
    e = ext(d)
    return f"""script:
  id_script: {n}_Installation_CreationTableAggregat
  description: Création initiale de la table agrégat {aggr_t(d)} ({p})

  parametres_env:
    TBL_AGGR: {pfx(d)}_HISTO.{aggr_t(d)}

  jobs:
    - job_id: job.run.sql
      description: Crée la table agrégat {aggr_t(d)} sur {p}
      parametres:
        Plateforme: {p}
        Requete: {n}_installation_creation_table_aggregat.{e}
"""


# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATES SQL
# ─────────────────────────────────────────────────────────────────────────────

def sql_load_staging(d):
    n = dn(d)
    p = pf(d)
    if p == "BQ":
        return f"""-- Chargement des fichiers {n.lower()} dans la table staging BigQuery
LOAD DATA OVERWRITE £BQ_TMP.{staging(d)}
FROM FILES (
  format = 'CSV',
  uris = ['gs://telecom-landing/{n.lower()}/*.csv'],
  skip_leading_rows = 1,
  field_delimiter = '{d["sep"]}'
);
"""
    else:
        cols = ",\n  ".join(col_names(d))
        return f"""-- Chargement des fichiers {n.lower()} dans la table staging Teradata
INSERT INTO £TD_TMP.{staging(d)} (
  {cols}
)
SELECT
  {cols}
FROM £TD_TMP.ext_{staging(d)};
"""

def sql_check_staging(d):
    n = dn(d)
    p = pf(d)
    if p == "BQ":
        return f"""-- Vérifie si la staging {staging(d)} contient des lignes aujourd'hui
SELECT IF(COUNT(*) > 0, 'OUI', 'NON')
FROM £BQ_TMP.{staging(d)}
WHERE DATE(date_maj) = CURRENT_DATE();
"""
    else:
        return f"""-- Vérifie si la staging {staging(d)} contient des lignes aujourd'hui
SELECT CASE WHEN COUNT(*) > 0 THEN 'OUI' ELSE 'NON' END
FROM £TD_TMP.{staging(d)}
WHERE CAST(date_maj AS DATE) = CURRENT_DATE;
"""

def sql_upsert_socle(d):
    n = dn(d)
    p = pf(d)
    k = key(d)
    cols = col_names(d)
    update_cols = [c for c in cols if c != k and c != "date_maj"]

    if p == "BQ":
        set_clause = "\n    ".join(f"cible.{c} = staging.{c}," for c in update_cols)
        set_clause = set_clause.rstrip(",")
        ins_cols = ", ".join(cols)
        ins_vals = ", ".join(f"staging.{c}" for c in cols[:-1]) + ", CURRENT_TIMESTAMP()"
        return f"""-- MERGE staging → SOCLE {socle(d)} (BigQuery)
MERGE £BQ_SOCLE.{socle(d)} AS cible
USING £BQ_TMP.{staging(d)} AS staging
ON cible.{k} = staging.{k}
WHEN MATCHED THEN
  UPDATE SET
    {set_clause},
    cible.date_maj = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
  INSERT ({ins_cols})
  VALUES ({ins_vals});
"""
    else:
        set_clause = "\n    ".join(f"cible.{c} = staging.{c}," for c in update_cols)
        set_clause = set_clause.rstrip(",")
        ins_cols = ", ".join(cols)
        ins_vals = ", ".join(f"staging.{c}" for c in cols[:-1]) + ", CURRENT_TIMESTAMP"
        return f"""-- MERGE staging → SOCLE {socle(d)} (Teradata)
MERGE £TD_SOCLE.{socle(d)} AS cible
USING £TD_TMP.{staging(d)} AS staging
ON cible.{k} = staging.{k}
WHEN MATCHED THEN UPDATE SET
    {set_clause},
    cible.date_maj = CURRENT_TIMESTAMP
WHEN NOT MATCHED THEN INSERT ({ins_cols})
  VALUES ({ins_vals});
"""

def sql_insert_histo(d):
    n = dn(d)
    p = pf(d)
    cols = col_names(d)
    sel_cols = ", ".join(f"s.{c}" for c in cols[:-1])
    if p == "BQ":
        return f"""-- Insert historique journalier {histo(d)} (BigQuery)
INSERT INTO £BQ_HISTO.{histo(d)}
SELECT
  {sel_cols},
  CURRENT_TIMESTAMP() AS date_maj
FROM £BQ_SOCLE.{socle(d)} s
WHERE DATE(s.date_maj) = CURRENT_DATE();
"""
    else:
        return f"""-- Insert historique journalier {histo(d)} (Teradata)
INSERT INTO £TD_HISTO.{histo(d)}
SELECT
  {sel_cols},
  CURRENT_TIMESTAMP AS date_maj
FROM £TD_SOCLE.{socle(d)} s
WHERE CAST(s.date_maj AS DATE) = CURRENT_DATE;
"""

def sql_aggr_journalier(d):
    n = dn(d)
    p = pf(d)
    k = key(d)
    if p == "BQ":
        return f"""-- Vérification que le SOCLE {socle(d)} a été mis à jour aujourd'hui
SELECT IF(COUNT(*) > 0, 'OUI', 'NON')
FROM £BQ_SOCLE.{socle(d)}
WHERE DATE(date_maj) = CURRENT_DATE();
"""
    else:
        return f"""-- Vérification que le SOCLE {socle(d)} a été mis à jour aujourd'hui
SELECT CASE WHEN COUNT(*) > 0 THEN 'OUI' ELSE 'NON' END
FROM £TD_SOCLE.{socle(d)}
WHERE CAST(date_maj AS DATE) = CURRENT_DATE;
"""

def sql_aggr_insert_journalier(d):
    n = dn(d)
    p = pf(d)
    k = key(d)
    if p == "BQ":
        return f"""-- Insertion agrégat journalier dans {histo(d)} (BigQuery)
INSERT INTO £BQ_HISTO.{histo(d)} (
  {k},
  date_agregat,
  nb_enregistrements,
  date_maj
)
SELECT
  '{n.lower()}' AS {k},
  CURRENT_DATE() AS date_agregat,
  COUNT(*) AS nb_enregistrements,
  CURRENT_TIMESTAMP() AS date_maj
FROM £BQ_SOCLE.{socle(d)}
WHERE DATE(date_maj) = CURRENT_DATE();
"""
    else:
        return f"""-- Insertion agrégat journalier dans {histo(d)} (Teradata)
INSERT INTO £TD_HISTO.{histo(d)} (
  {k},
  date_agregat,
  nb_enregistrements,
  date_maj
)
SELECT
  '{n.lower()}',
  CURRENT_DATE,
  COUNT(*),
  CURRENT_TIMESTAMP
FROM £TD_SOCLE.{socle(d)}
WHERE CAST(date_maj AS DATE) = CURRENT_DATE;
"""

def sql_aggr_delete_mensuel(d):
    n = dn(d)
    p = pf(d)
    if p == "BQ":
        return f"""-- Suppression des agrégats du mois courant avant recalcul (BigQuery)
DELETE FROM £BQ_HISTO.{aggr_t(d)}
WHERE FORMAT_DATE('%Y%m', date_agregat) = FORMAT_DATE('%Y%m', CURRENT_DATE());
"""
    else:
        return f"""-- Suppression des agrégats du mois courant avant recalcul (Teradata)
DELETE FROM £TD_HISTO.{aggr_t(d)}
WHERE TO_CHAR(date_agregat, 'YYYYMM') = TO_CHAR(CURRENT_DATE, 'YYYYMM');
"""

def sql_aggr_insert_mensuel(d):
    n = dn(d)
    p = pf(d)
    cross = cross_sql_snippet(d)
    cross_comment = f"\n-- Flux transverse : jointures avec tables d'autres domaines\n{cross}\n" if cross else ""
    if p == "BQ":
        return f"""-- Agrégation mensuelle {aggr_t(d)} par segment (BigQuery)
{cross_comment}
INSERT INTO £BQ_HISTO.{aggr_t(d)} (
  periode,
  nb_enregistrements,
  date_calcul
)
SELECT
  FORMAT_DATE('%Y%m', CURRENT_DATE()) AS periode,
  COUNT(*) AS nb_enregistrements,
  CURRENT_TIMESTAMP() AS date_calcul
FROM £BQ_SOCLE.{socle(d)} t
WHERE DATE(t.date_maj) >= DATE_TRUNC(CURRENT_DATE(), MONTH);
"""
    else:
        return f"""-- Agrégation mensuelle {aggr_t(d)} par segment (Teradata)
{cross_comment}
INSERT INTO £TD_HISTO.{aggr_t(d)} (
  periode,
  nb_enregistrements,
  date_calcul
)
SELECT
  TO_CHAR(CURRENT_DATE, 'YYYYMM') AS periode,
  COUNT(*) AS nb_enregistrements,
  CURRENT_TIMESTAMP AS date_calcul
FROM £TD_SOCLE.{socle(d)} t
WHERE CAST(t.date_maj AS DATE) >= (CURRENT_DATE - EXTRACT(DAY FROM CURRENT_DATE) + 1);
"""

def sql_aggr_cumul(d):
    n = dn(d)
    p = pf(d)
    if p == "BQ":
        return f"""-- Calcul cumul glissant 12 mois pour {aggr_t(d)} (BigQuery)
DELETE FROM £BQ_HISTO.{aggr_t(d)}
WHERE date_calcul >= TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), MONTH);

INSERT INTO £BQ_HISTO.{aggr_t(d)}
SELECT
  FORMAT_DATE('%Y%m', h.periode_date) AS periode,
  SUM(h.nb_enregistrements) OVER (
    ORDER BY h.periode_date
    ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
  ) AS cumul_12m,
  CURRENT_TIMESTAMP() AS date_calcul
FROM (
  SELECT PARSE_DATE('%Y%m', periode) AS periode_date, nb_enregistrements
  FROM £BQ_HISTO.{histo(d)}
) h
ORDER BY h.periode_date;
"""
    else:
        return f"""-- Calcul cumul glissant 12 mois pour {aggr_t(d)} (Teradata)
DELETE FROM £TD_HISTO.{aggr_t(d)}
WHERE date_calcul >= (CURRENT_DATE - EXTRACT(DAY FROM CURRENT_DATE) + 1);

INSERT INTO £TD_HISTO.{aggr_t(d)}
SELECT
  TO_CHAR(h.periode_date, 'YYYYMM') AS periode,
  SUM(h.nb_enregistrements) OVER (
    ORDER BY h.periode_date ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
  ) AS cumul_12m,
  CURRENT_TIMESTAMP AS date_calcul
FROM (
  SELECT CAST(periode AS DATE FORMAT 'YYYYMM') AS periode_date, nb_enregistrements
  FROM £TD_HISTO.{histo(d)}
) h
ORDER BY h.periode_date;
"""

def sql_create_table_staging(d):
    n = dn(d)
    p = pf(d)
    defs = col_defs_sql(d)
    if p == "BQ":
        return f"""-- Création de la table staging {staging(d)} (BigQuery)
CREATE TABLE IF NOT EXISTS £BQ_TMP.{staging(d)} (
{defs}
)
OPTIONS (expiration_timestamp = NULL);
"""
    else:
        return f"""-- Création de la table staging {staging(d)} (Teradata)
CREATE TABLE IF NOT EXISTS £TD_TMP.{staging(d)} (
{defs}
)
PRIMARY INDEX ({key(d)});
"""

def sql_create_table_socle(d):
    n = dn(d)
    p = pf(d)
    defs = col_defs_sql(d)
    if p == "BQ":
        return f"""-- Création de la table SOCLE {socle(d)} (BigQuery)
CREATE TABLE IF NOT EXISTS £BQ_SOCLE.{socle(d)} (
{defs}
);
"""
    else:
        return f"""-- Création de la table SOCLE {socle(d)} (Teradata)
CREATE TABLE IF NOT EXISTS £TD_SOCLE.{socle(d)} (
{defs}
)
PRIMARY INDEX ({key(d)});
"""

def sql_create_table_aggr(d):
    n = dn(d)
    p = pf(d)
    if p == "BQ":
        return f"""-- Création de la table agrégat {aggr_t(d)} (BigQuery)
CREATE TABLE IF NOT EXISTS £BQ_HISTO.{aggr_t(d)} (
  periode                  STRING         NOT NULL,
  nb_enregistrements       INT64,
  cumul_12m                INT64,
  date_calcul              TIMESTAMP
);
"""
    else:
        return f"""-- Création de la table agrégat {aggr_t(d)} (Teradata)
CREATE TABLE IF NOT EXISTS £TD_HISTO.{aggr_t(d)} (
  periode                  VARCHAR(7)     NOT NULL,
  nb_enregistrements       INTEGER,
  cumul_12m                INTEGER,
  date_calcul              TIMESTAMP
)
PRIMARY INDEX (periode);
"""

def sql_enrichissement_transverse(d):
    n = dn(d)
    p = pf(d)
    cross = cross_sql_snippet(d)
    if p == "BQ":
        return f"""-- Enrichissement transverse {socle(d)} (BigQuery)
-- Ce flux est TRANSVERSE : il emprunte des tables d'autres domaines.
{cross}
INSERT INTO £BQ_TMP.{socle(d)}_enrichi
SELECT
  t.*
FROM £BQ_SOCLE.{socle(d)} t;
"""
    else:
        return f"""-- Enrichissement transverse {socle(d)} (Teradata)
-- Ce flux est TRANSVERSE : il emprunte des tables d'autres domaines.
{cross}
INSERT INTO £TD_TMP.{socle(d)}_enrichi
SELECT
  t.*
FROM £TD_SOCLE.{socle(d)} t;
"""


# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATES CDC (pré-implémentation)
# ─────────────────────────────────────────────────────────────────────────────

def cdc(d, flow_type, flow_name, description, sources, cibles, regles, frequence, contraintes, is_transverse=False):
    n = dn(d)
    p = pf(d)
    transverse_note = ""
    if is_transverse:
        refs = CROSS_REFS.get(n, [])
        ref_list = "\n".join(f"- `{r[0]}_SOCLE.{r[1]}` (domaine **{r[2]}**)" for r in refs)
        transverse_note = f"""
## Dépendances transverses

Ce flux est **transverse** : il emprunte des tables appartenant à d'autres domaines.
Toute évolution de ces tables peut impacter ce flux.

{ref_list}

"""
    return f"""# Cahier des Charges — {n} / {flow_type} / {flow_name}

**Domaine** : {n}
**Type de flux** : {flow_type}
**Plateforme cible** : {p}
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

{description}

---

## Sources souhaitées

{sources}

---

## Cibles souhaitées

{cibles}

---

## Règles de gestion

{regles}

---
{transverse_note}
## Fréquence souhaitée

{frequence}

---

## Contraintes techniques

{contraintes}

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
"""

# ─────────────────────────────────────────────────────────────────────────────
# GÉNÉRATION PAR DOMAINE
# ─────────────────────────────────────────────────────────────────────────────

def generate_domain(d):
    n  = dn(d)
    p  = pf(d)
    e  = ext(d)
    wp = WORKSPACE_ROOT / n
    dp = DOCS_ROOT / n
    is_compressed = d.get("compressed", False)
    has_api = d.get("api_out") is not None
    has_cross = n in CROSS_REFS

    print(f"  [{p}] {n}")

    # ── IMPORT ────────────────────────────────────────────────────────────────
    w(wp / "Import/config" / f"{n}_import_RapatriementSFTP.yml",
      yaml_import_rapatriement(d))
    w(dp / f"{n}_import_RapatriementSFTP_CDC.md",
      cdc(d, "Import", "RapatriementSFTP",
          f"Rapatriement quotidien des fichiers {n.lower()} depuis le serveur SFTP du partenaire vers la zone d'entrée locale.",
          f"- SFTP source : `{d['sftp_in']}`\n- Format : CSV (séparateur `{d['sep']}`, encodage {d['encoding']})\n- Masque fichier : `{d['file_mask']}`",
          f"- Répertoire local : `{d['rep_in']}`",
          "- Récupérer tous les fichiers correspondant au masque.\n- Ne pas supprimer les fichiers sur le SFTP source.\n- En cas d'échec de connexion, le flux doit échouer et alerter.",
          "Quotidien — déclenchement à 06h00.",
          f"- Connexion SFTP sécurisée (clé SSH).\n- Timeout de connexion : 30 secondes.\n- Le répertoire `{d['rep_in']}` doit exister avant exécution."))

    w(wp / "Import/config" / f"{n}_import_DeplacementTravail.yml",
      yaml_import_deplacement(d))
    w(dp / f"{n}_import_DeplacementTravail_CDC.md",
      cdc(d, "Import", "DeplacementTravail",
          f"Déplacement des fichiers {n.lower()} validés de la zone d'entrée vers la zone de travail pour traitement.",
          f"- Répertoire source : `{d['rep_in']}`\n- Masque : `{d['file_mask']}`",
          f"- Répertoire cible : `{d['rep_work']}`",
          "- Déplacer uniquement les fichiers correspondant au masque.\n- Ne laisser aucun fichier en zone d'entrée après déplacement.",
          "Quotidien — après le rapatriement SFTP.",
          f"- Répertoire `{d['rep_work']}` doit exister.\n- Aucun fichier en doublon accepté en zone de travail."))

    if is_compressed:
        w(wp / "Import/config" / f"{n}_import_Decompression.yml",
          yaml_import_decompression(d))
        w(dp / f"{n}_import_Decompression_CDC.md",
          cdc(d, "Import", "Decompression",
              f"Décompression des archives {n.lower()} (.gz) reçues depuis la plateforme de médiation avant validation.",
              f"- Répertoire source : `{d['rep_in']}`\n- Format : gzip (.csv.gz)",
              f"- Répertoire cible : `{d['rep_work']}` (fichiers .csv décompressés)",
              "- Décompresser chaque fichier .gz individuellement.\n- Conserver le fichier source jusqu'à validation.",
              "Quotidien — immédiatement après rapatriement.",
              "- Format gzip uniquement. Les autres formats doivent être rejetés."))

    w(wp / "Import/config" / f"{n}_import_ControleCSV.yml",
      yaml_import_controle(d))
    w(dp / f"{n}_import_ControleCSV_CDC.md",
      cdc(d, "Import", "ControleCSV",
          f"Validation structurelle des fichiers {n.lower()} avant chargement en staging : colonnes, encodage et non-vide.",
          f"- Répertoire : `{d['rep_work']}`\n- Masque : `{d['file_mask']}`",
          f"- Fichiers invalides déplacés vers `{d['rep_err']}`",
          f"- Vérifier la présence des colonnes : `{','.join(col_names(d)[:6])}`\n- Séparateur attendu : `{d['sep']}`\n- Encodage : {d['encoding']}\n- Fichier non vide obligatoire.",
          "Quotidien — après déplacement en zone de travail.",
          f"- Le répertoire d'erreur `{d['rep_err']}` doit exister.\n- Le flux doit échouer si au moins un fichier est invalide."))

    w(wp / "Import/config" / f"{n}_import_TraitementBatch.yml",
      yaml_import_batch(d))
    w(wp / "Import/sql" / f"{n}_import_chargement_staging.{e}",
      sql_load_staging(d))
    w(dp / f"{n}_import_TraitementBatch_CDC.md",
      cdc(d, "Import", "TraitementBatch",
          f"Chargement en masse de tous les fichiers {n.lower()} validés dans la table staging puis archivage.",
          f"- Zone de travail : `{d['rep_work']}`\n- Table staging : `{pfx(d)}_TMP.{staging(d)}`",
          f"- Table staging chargée : `{pfx(d)}_TMP.{staging(d)}`\n- Fichiers archivés dans `{d['rep_arch']}`",
          "- Charger tous les fichiers en une seule passe (batch).\n- Archiver les fichiers traités.\n- Purger les archives de plus de 3 mois.",
          "Quotidien — après contrôle CSV.",
          "- La table staging doit exister (voir installation).\n- En cas d'échec partiel, toute la passe doit être rejouée."))

    # Import installation
    w(wp / "Import/installation/config" / f"{n}_installation_CreationTableStaging.yml",
      yaml_install_staging(d))
    w(wp / "Import/installation/sql" / f"{n}_installation_creation_table_staging.{e}",
      sql_create_table_staging(d))

    # ── ALIMENTATION ──────────────────────────────────────────────────────────
    w(wp / "Alimentation/config" / f"{n}_alimentation_UpsertSocle.yml",
      yaml_alim_upsert(d))
    w(wp / "Alimentation/sql" / f"{n}_alimentation_check_staging.{e}",
      sql_check_staging(d))
    w(wp / "Alimentation/sql" / f"{n}_alimentation_upsert_socle.{e}",
      sql_upsert_socle(d))
    w(wp / "Alimentation/sql" / f"{n}_alimentation_insert_histo.{e}",
      sql_insert_histo(d))
    w(dp / f"{n}_alimentation_UpsertSocle_CDC.md",
      cdc(d, "Alimentation", "UpsertSocle",
          f"Alimentation du SOCLE {socle(d)} depuis la staging par opération MERGE (UPSERT). Mise à jour des existants et insertion des nouveaux.",
          f"- Table staging : `{pfx(d)}_TMP.{staging(d)}`",
          f"- Table SOCLE : `{pfx(d)}_SOCLE.{socle(d)}`\n- Vue métier : `{pfx(d)}_VUES.{socle(d)}`",
          f"- Clé de jointure : `{key(d)}`\n- MERGE : UPDATE si existant, INSERT si nouveau.\n- Mettre à jour `date_maj` à chaque modification.\n- Créer/rafraîchir la vue métier après chaque run.",
          "Quotidien — après chargement staging.",
          "- La staging doit être peuplée (contrôle via FLAG avant merge).\n- La vue ne doit jamais pointer sur une table vide."))

    w(wp / "Alimentation/config" / f"{n}_alimentation_ChargementsParalleles.yml",
      yaml_alim_parallele(d))
    w(dp / f"{n}_alimentation_ChargementsParalleles_CDC.md",
      cdc(d, "Alimentation", "ChargementsParalleles",
          f"Chargement simultané du SOCLE et de la table historique {n.lower()} pour optimiser les temps de traitement.",
          f"- Table staging : `{pfx(d)}_TMP.{staging(d)}`",
          f"- SOCLE : `{pfx(d)}_SOCLE.{socle(d)}`\n- Historique : `{pfx(d)}_HISTO.{histo(d)}`",
          "- Exécuter le MERGE SOCLE et l'INSERT HISTO en parallèle.\n- Les deux opérations sont indépendantes.\n- Le flux global échoue si l'une des deux échoue.",
          "Quotidien — en remplacement du chargement séquentiel sur les volumes importants.",
          "- Aucune dépendance entre SOCLE et HISTO pour ce flux.\n- Rollback manuel si l'une des deux opérations échoue à mi-course."))

    if has_cross:
        w(wp / "Alimentation/config" / f"{n}_alimentation_EnrichissementTransverse.yml",
          yaml_alim_transfert(d))
        w(wp / "Alimentation/sql" / f"{n}_alimentation_enrichissement_transverse.{e}",
          sql_enrichissement_transverse(d))
        w(dp / f"{n}_alimentation_EnrichissementTransverse_CDC.md",
          cdc(d, "Alimentation", "EnrichissementTransverse",
              f"Enrichissement du SOCLE {socle(d)} avec des données provenant d'autres domaines via jointures SQL transverses.",
              f"- Table SOCLE locale : `{pfx(d)}_SOCLE.{socle(d)}`\n"
              + "\n".join(f"- Table transverse : `{'£BQ' if r[0]=='BQ' else '£TD'}_SOCLE.{r[1]}` (domaine {r[2]})" for r in CROSS_REFS[n]),
              f"- Table enrichie : `{pfx(d)}_TMP.{socle(d)}_enrichi`",
              "- Joindre les tables des domaines référencés.\n- Ne pas modifier les données SOCLE originales.\n- Stocker le résultat en table temporaire pour les agrégats.",
              "Hebdomadaire — chaque dimanche.",
              "- Les tables des domaines partenaires doivent être à jour.\n- Flux TRANSVERSE : toute évolution des tables empruntées impacte ce flux.",
              is_transverse=True))

    # Alimentation installation
    w(wp / "Alimentation/installation/config" / f"{n}_installation_CreationTableSocle.yml",
      yaml_install_socle(d))
    w(wp / "Alimentation/installation/sql" / f"{n}_installation_creation_table_socle.{e}",
      sql_create_table_socle(d))

    # ── EXPORT ────────────────────────────────────────────────────────────────
    w(wp / "Export/config" / f"{n}_export_ExtractionCSV.yml",
      yaml_export_extraction(d))
    w(dp / f"{n}_export_ExtractionCSV_CDC.md",
      cdc(d, "Export", "ExtractionCSV",
          f"Extraction quotidienne du SOCLE {socle(d)} vers un fichier CSV daté pour distribution aux partenaires.",
          f"- Table SOCLE : `{pfx(d)}_SOCLE.{socle(d)}`",
          f"- Fichier CSV : `{d['rep_export']}/{n.lower()}_AAAAMMJJ.csv`",
          "- Extraire toutes les lignes actives du SOCLE.\n- Nommer le fichier avec la date du jour (format AAAAMMJJ).\n- Format CSV avec en-têtes.",
          "Quotidien — après alimentation SOCLE.",
          f"- Le répertoire `{d['rep_export']}` doit exister.\n- Purge des exports de plus de 1 mois."))

    w(wp / "Export/config" / f"{n}_export_EnvoiSFTP.yml",
      yaml_export_sftp(d))
    w(dp / f"{n}_export_EnvoiSFTP_CDC.md",
      cdc(d, "Export", "EnvoiSFTP",
          f"Envoi des fichiers CSV {n.lower()} extraits vers le SFTP de distribution partenaire.",
          f"- Répertoire source : `{d['rep_export']}`",
          f"- SFTP destination : `{d['sftp_out']}`",
          "- Envoyer uniquement les fichiers du jour.\n- Vérifier la présence de fichiers avant envoi.\n- Purger les exports locaux après envoi réussi.",
          "Quotidien — après extraction CSV.",
          "- Connexion SFTP sécurisée requise.\n- En cas d'échec d'envoi, conserver le fichier local."))

    if has_api:
        w(wp / "Export/config" / f"{n}_export_ExportAPI.yml",
          yaml_export_api(d))
        w(dp / f"{n}_export_ExportAPI_CDC.md",
          cdc(d, "Export", "ExportAPI",
              f"Export du SOCLE {socle(d)} vers l'API partenaire en format JSON pour synchronisation temps réel.",
              f"- Table SOCLE : `{pfx(d)}_SOCLE.{socle(d)}`",
              f"- API destination : `{d['api_out']}`\n- Format : JSON",
              "- Extraire le SOCLE complet en JSON.\n- Authentification Bearer Token sur l'API.\n- Retry automatique en cas d'erreur HTTP 5xx.",
              "Quotidien — après extraction CSV.",
              "- Token API valide requis (configuré en variable d'environnement).\n- Timeout API : 60 secondes par appel."))

    # ── AGGREGAT ──────────────────────────────────────────────────────────────
    w(wp / "Aggregat/config" / f"{n}_aggregat_JournalierSocle.yml",
      yaml_aggr_journalier(d))
    w(wp / "Aggregat/sql" / f"{n}_aggregat_check_socle_jour.{e}",
      sql_aggr_journalier(d))
    w(wp / "Aggregat/sql" / f"{n}_aggregat_insert_journalier.{e}",
      sql_aggr_insert_journalier(d))
    w(dp / f"{n}_aggregat_JournalierSocle_CDC.md",
      cdc(d, "Aggregat", "JournalierSocle",
          f"Historisation quotidienne des comptages du SOCLE {socle(d)} pour suivi de volumétrie.",
          f"- Table SOCLE : `{pfx(d)}_SOCLE.{socle(d)}`",
          f"- Table historique : `{pfx(d)}_HISTO.{histo(d)}`",
          "- Insérer une ligne par jour avec le count du SOCLE.\n- Ne pas écraser les jours précédents.\n- Contrôler que le SOCLE a été mis à jour avant d'agréger.",
          "Quotidien — après alimentation SOCLE.",
          "- La table historique doit exister (voir installation).\n- Un seul enregistrement par jour autorisé."))

    w(wp / "Aggregat/config" / f"{n}_aggregat_MensuelParSegment.yml",
      yaml_aggr_mensuel(d))
    w(wp / "Aggregat/sql" / f"{n}_aggregat_delete_mensuel.{e}",
      sql_aggr_delete_mensuel(d))
    w(wp / "Aggregat/sql" / f"{n}_aggregat_insert_mensuel_segment.{e}",
      sql_aggr_insert_mensuel(d))
    w(dp / f"{n}_aggregat_MensuelParSegment_CDC.md",
      cdc(d, "Aggregat", "MensuelParSegment",
          f"Calcul des agrégats mensuels du SOCLE {socle(d)} par dimension métier pour le reporting mensuel.",
          f"- Table SOCLE : `{pfx(d)}_SOCLE.{socle(d)}`",
          f"- Table agrégat mensuelle : `{pfx(d)}_HISTO.{aggr_t(d)}`",
          "- Supprimer les agrégats du mois courant avant recalcul (idempotent).\n- Agréger sur la période AAAAMM en cours.\n- Granularité : par segment ou dimension principale.",
          "Mensuel — 1er jour du mois suivant.",
          "- Flux idempotent : peut être rejoué sans doublon.\n- Le mois en cours ne doit jamais être partiel dans la table agrégat.",
          is_transverse=has_cross))

    w(wp / "Aggregat/config" / f"{n}_aggregat_CumulGlissant.yml",
      yaml_aggr_cumul(d))
    w(wp / "Aggregat/sql" / f"{n}_aggregat_cumul_glissant_12m.{e}",
      sql_aggr_cumul(d))
    w(dp / f"{n}_aggregat_CumulGlissant_CDC.md",
      cdc(d, "Aggregat", "CumulGlissant",
          f"Calcul du cumul glissant sur 12 mois pour les indicateurs {n.lower()} — utilisé pour les analyses de tendance.",
          f"- Table historique : `{pfx(d)}_HISTO.{histo(d)}`",
          f"- Table agrégat glissante : `{pfx(d)}_HISTO.{aggr_t(d)}`",
          "- Calculer le cumul sur une fenêtre glissante de 12 mois.\n- Recalcul complet du mois en cours à chaque run.\n- Résultat trié chronologiquement.",
          "Mensuel — après calcul des agrégats mensuels.",
          "- Au moins 12 mois d'historique requis pour un résultat complet.\n- Les mois manquants dans l'historique produisent un cumul partiel."))

    # Aggregat installation
    w(wp / "Aggregat/installation/config" / f"{n}_installation_CreationTableAggregat.yml",
      yaml_install_aggr(d))
    w(wp / "Aggregat/installation/sql" / f"{n}_installation_creation_table_aggregat.{e}",
      sql_create_table_aggr(d))

# ─────────────────────────────────────────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("Nettoyage des répertoires existants...")
    if WORKSPACE_ROOT.exists():
        shutil.rmtree(WORKSPACE_ROOT)
    if DOCS_ROOT.exists():
        shutil.rmtree(DOCS_ROOT)

    print(f"Génération de {len(DOMAINS)} domaines télécom...\n")
    total_yaml = 0
    total_sql  = 0
    total_docs = 0

    for d in DOMAINS:
        generate_domain(d)

    # Comptage
    for f in WORKSPACE_ROOT.rglob("*.yml"):
        total_yaml += 1
    for f in WORKSPACE_ROOT.rglob("*.gql"):
        total_sql += 1
    for f in WORKSPACE_ROOT.rglob("*.dql"):
        total_sql += 1
    for f in DOCS_ROOT.rglob("*.md"):
        total_docs += 1

    print(f"\nGeneration terminee.")
    print(f"  YAML   : {total_yaml}")
    print(f"  SQL    : {total_sql}")
    print(f"  CDCs   : {total_docs}")
    print(f"  TOTAL  : {total_yaml + total_sql + total_docs} fichiers")
    print(f"\n  Workspace : {WORKSPACE_ROOT.resolve()}")
    print(f"  Docs      : {DOCS_ROOT.resolve()}")

if __name__ == "__main__":
    main()
