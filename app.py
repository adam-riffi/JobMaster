"""
JobMaster — Générateur de workflows YAML par IA
Application Streamlit + API Groq (wizard multi-étapes)
"""

import streamlit as st
from dotenv import load_dotenv

from ui_composants import (
    afficher_etape_1,
    afficher_etape_2,
    afficher_etape_3,
    afficher_etape_4,
    afficher_etape_5,
    afficher_recap,
    afficher_sidebar,
    init_session,
)

load_dotenv()


def main():
    st.set_page_config(
        page_title="JobMaster — Générateur de workflows",
        page_icon="⚙️",
        layout="wide",
    )

    st.title("⚙️ JobMaster — Générateur de workflows par IA")
    st.caption("Wizard guidé : définissez vos paramètres, l'IA pose ses questions, puis génère le workflow complet.")

    # Initialisation
    init_session()

    # Sidebar (config + progression)
    api_key, modele = afficher_sidebar()
    afficher_recap()

    # Routeur d'étapes
    etape = st.session_state["etape"]

    if etape == 1:
        afficher_etape_1(api_key, modele)
    elif etape == 2:
        afficher_etape_2()
    elif etape == 3:
        afficher_etape_3()
    elif etape == 4:
        afficher_etape_4(api_key, modele)
    elif etape == 5:
        afficher_etape_5(api_key, modele)


if __name__ == "__main__":
    main()
