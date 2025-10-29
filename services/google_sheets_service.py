import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

class GoogleSheetsService:
    def __init__(self, sheet_name):
        secrets = st.secrets["gcp_service_account"]
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(dict(secrets), scopes=scopes)
        self.gc = gspread.authorize(creds)
        self.sheet = self.gc.open(sheet_name).sheet1

    def carregar_tarefas(self):
        """Retorna todas as tarefas como DataFrame."""
        dados = self.sheet.get_all_records()
        return pd.DataFrame(dados)

    def salvar_tarefa(self, tarefa):
        """Adiciona nova tarefa."""
        self.sheet.append_row(tarefa.to_list())

    def atualizar_status(self, tarefa_id, novo_status):
        """Atualiza status e histórico de uma tarefa existente."""
        dados = self.sheet.get_all_records()
        for i, row in enumerate(dados, start=2):
            if row["id"] == tarefa_id:
                from datetime import datetime
                hist_antigo = row["historico"]
                novo_hist = f"{hist_antigo}\n{datetime.now().strftime('%d/%m/%Y %H:%M')} - Status alterado para {novo_status}"
                self.sheet.update(f"F{i}:H{i}", [
                    [novo_status, novo_hist, datetime.now().strftime("%d/%m/%Y %H:%M")]
                ])
                return True
        return False
