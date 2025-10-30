import streamlit as st
import gspread
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials

class GoogleSheetsService:
    def __init__(self, sheet_name: str):
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scopes
        )
        client = gspread.authorize(credentials)
        self.sheet = client.open_by_key(sheet_name).sheet1  # aba principal

    def carregar_tarefas(self) -> pd.DataFrame:
        try:
            data = self.sheet.get_all_records()
            df = pd.DataFrame(data)
        except Exception as e:
            print(f"Erro ao carregar planilha: {e}")
            return pd.DataFrame()

        df.columns = [c.strip().lower() for c in df.columns]
        required = ["id","data_criacao","titulo","categoria","prazo","status","historico","ultima_atualizacao","autor"]
        for c in required:
            if c not in df.columns:
                df[c] = ""
        df = df.dropna(how="all")
        return df

    def registrar_log(self, usuario: str, id_tarefa: str, campo: str, valor_antigo: str, valor_novo: str):
        """Adiciona linha em 'Logs' (cria se não existir)."""
        try:
            log_sheet = self.sheet.spreadsheet.worksheet("Logs")
        except Exception:
            log_sheet = self.sheet.spreadsheet.add_worksheet(title="Logs", rows="100", cols="10")
            log_sheet.append_row(["data_hora", "usuario", "id_tarefa", "campo", "valor_antigo", "valor_novo"])

        log_entry = [
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            usuario,
            id_tarefa,
            campo,
            valor_antigo or "",
            valor_novo or ""
        ]
        log_sheet.append_row(log_entry)
