import streamlit as st
import pandas as pd
import bcrypt
from datetime import datetime

from models.tarefa import Tarefa
from models.dashboard import Dashboard
from models.interface_ui import InterfaceUI
from services.google_sheets_service import GoogleSheetsService

# ============================================================
# ⚙️ CONFIGURAÇÕES INICIAIS
# ============================================================
st.set_page_config(page_title="Controle de Tarefas", page_icon="✅", layout="wide")

# ============================================================
# 🔐 AUTENTICAÇÃO MANUAL
# ============================================================
creds = st.secrets["credentials"]["usernames"]
cookie = st.secrets["cookie"]

if "user" not in st.session_state:
    st.session_state["user"] =
