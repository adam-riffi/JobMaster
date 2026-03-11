"""Aleister — Configuration centrale."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT_DIR       = Path(__file__).parent.parent
WORKSPACE_ROOT = Path(os.getenv("WORKSPACE_ROOT", str(ROOT_DIR / "workspaces")))
DOCS_ROOT      = Path(os.getenv("DOCS_ROOT",      str(ROOT_DIR / "docs")))
DOC_PATH       = ROOT_DIR / "jobmaster" / "doc.txt"

# ── LLM ───────────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

MODELES_GROQ = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
    "mixtral-8x7b-32768",
]
DEFAULT_MODEL = MODELES_GROQ[0]

# ── JobMaster grammar ──────────────────────────────────────────────────────────
FLOW_TYPES  = ["Import", "Alimentation", "Export", "Aggregat"]
PLATFORMS   = ["BQ", "TD"]
LOAD_MODES  = ["FULL", "INSERT", "UPDATE", "UPSERT"]
