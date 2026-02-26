# ⚙️ JobMaster — Générateur de workflows par IA

Application Streamlit qui génère automatiquement des workflows YAML + SQL conformes à la documentation JobMaster, via l'API Groq (LLM).

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red)
![License](https://img.shields.io/badge/License-MIT-green)

## 🎯 Fonctionnalités

- **Wizard guidé** en 5 étapes : paramètres → structure données → détails techniques → questions IA → génération
- **Éditeur de colonnes** interactif avec typage BQ (BigQuery) ou TD (Teradata)
- **Mode Full IA** 🎲 : l'IA invente un cas d'usage complet pour la démo (domaine, colonnes, types, etc.)
- **Questions de clarification** : l'IA analyse le contexte et pose des questions avant de générer
- **Vue arborescente** des fichiers générés (Import/config, Alimentation/sql, etc.)
- **Export ZIP** de l'ensemble des fichiers générés
- Respect strict de la documentation officielle JobMaster v1.2

## 📁 Structure du projet

```
JobMaster/
├── app.py              # Point d'entrée Streamlit (orchestrateur wizard)
├── config.py           # Configuration centrale (types, plateformes, modèles)
├── prompts.py          # Prompts système et utilisateur pour Groq
├── generator.py        # Appels API Groq, parsing réponse, ZIP
├── ui_composants.py    # Composants UI Streamlit (5 étapes du wizard)
├── doc.txt             # Documentation officielle JobMaster v1.2
├── requirements.txt    # Dépendances Python
├── .env.example        # Template pour la clé API
├── .gitignore
└── README.md
```

## 🚀 Installation

### Prérequis

- Python 3.10+
- Un compte [Groq](https://console.groq.com/) (gratuit) pour obtenir une clé API

### Étapes

```bash
# Cloner le dépôt
git clone https://github.com/adam-riffi/JobMaster.git
cd JobMaster

# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer la clé API
cp .env.example .env
# Éditez .env et ajoutez votre clé Groq
```

### Lancement

```bash
streamlit run app.py
```

L'application s'ouvre sur [http://localhost:8501](http://localhost:8501).

## 🔑 Configuration API

Récupérez votre clé API gratuite sur [console.groq.com/keys](https://console.groq.com/keys), puis :

- **Option 1** : Créez un fichier `.env` à la racine :
  ```
  GROQ_API_KEY=gsk_votre_cle_ici
  ```
- **Option 2** : Saisissez la clé directement dans la sidebar de l'application.

## 📖 Documentation JobMaster

Le fichier `doc.txt` contient la documentation officielle v1.2 utilisée par l'IA pour générer des workflows conformes. Elle couvre :

- Architecture des répertoires (Import/Alimentation/Export)
- Format YAML et variables (préfixe `£`)
- Catalogue de 10 job_id
- Tables externes et chargement (BigQuery + Teradata)
- Conventions de nommage
- Bonnes pratiques

## 🤖 Modèles supportés

| Modèle | Description |
|--------|-------------|
| `llama-3.3-70b-versatile` | Meilleure qualité (par défaut) |
| `llama-3.1-8b-instant` | Rapide, bon pour les tests |
| `gemma2-9b-it` | Alternative Google |
| `mixtral-8x7b-32768` | Long contexte |

## 📝 Licence

MIT
