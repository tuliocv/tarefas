# services/google_sheets_service.py
import streamlit as st
import gspread
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials

class GoogleSheetsService:
    def __init__(self, sheet_name: str):
        """Inicializa o serviço de conexão com Google Sheets"""
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scopes
        )
        client = gspread.authorize(credentials)
        self.sheet = client.open_by_key(sheet_name).sheet1  # aba principal (Sheet1)

    def carregar_tarefas(self) -> pd.DataFrame:
        """Lê registros da planilha"""
        try:
            data = self.sheet.get_all_records()
            df = pd.DataFrame(data)
        except Exception as e:
            print(f"Erro ao carregar planilha: {e}")
            return pd.DataFrame()

        # Garante colunas esperadas (em minúsculo, caso venham maiúsculas)
        df.columns = [c.strip().lower() for c in df.columns]
        required_cols = [
            "id", "data_criacao", "titulo", "categoria", "prazo",
            "status", "historico", "ultima_atualizacao", "autor"
        ]
        for col in required_cols:
            if col not in df.columns:
                df[col] = ""
        df = df.dropna(how="all")
        return df

    # ==============================================
    # 🔍 Função de registro automático de logs
    # ==============================================
    def registrar_log(self, usuario: str, id_tarefa: str, campo: str, valor_antigo: str, valor_novo: str):
        """Adiciona uma linha de log na aba 'Logs'"""
        try:
            log_sheet = self.sheet.spreadsheet.worksheet("Logs")
        except Exception:
            # cria a aba e cabeçalho, se não existir
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
