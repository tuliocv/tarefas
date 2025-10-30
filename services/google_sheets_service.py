# services/google_sheets_service.py
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

class GoogleSheetsService:
    def __init__(self, sheet_name: str):
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scopes
        )
        client = gspread.authorize(credentials)
        self.sheet = client.open_by_key(sheet_name).sheet1

    def carregar_tarefas(self) -> pd.DataFrame:
        """Carrega as tarefas do Google Sheets e garante cabeçalhos válidos"""
        try:
            data = self.sheet.get_all_records()
            df = pd.DataFrame(data)

            # Garante que todas as colunas necessárias existam
            required_cols = ["id", "titulo", "categoria", "prazo", "status", "data_criacao", "autor", "descricao"]
            for col in required_cols:
                if col not in df.columns:
                    df[col] = ""

            # Remove linhas completamente vazias
            df = df.dropna(how="all")

            return df
        except Exception as e:
            print(f"Erro ao carregar tarefas: {e}")
            return pd.DataFrame(columns=["id", "titulo", "categoria", "prazo", "status", "data_criacao", "autor", "descricao"])

    def atualizar_status(self, tarefa_id: str, novo_status: str) -> bool:
        """Atualiza o status de uma tarefa no Google Sheets"""
        try:
            valores = self.sheet.get_all_values()
            headers = valores[0]
            id_idx = headers.index("id")
            status_idx = headers.index("status")

            for i, linha in enumerate(valores[1:], start=2):
                if len(linha) > id_idx and linha[id_idx] == tarefa_id:
                    self.sheet.update_cell(i, status_idx + 1, novo_status)
                    return True
            return False
        except Exception as e:
            print(f"Erro ao atualizar status: {e}")
            return False
