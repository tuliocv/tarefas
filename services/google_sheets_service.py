# services/google_sheets_service.py
import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

class GoogleSheetsService:
    def __init__(self, sheet_name: str):
        """Inicializa o serviço de conexão com Google Sheets"""
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scopes
        )
        client = gspread.authorize(credentials)
        self.sheet = client.open_by_key(sheet_name).sheet1

    def carregar_tarefas(self) -> pd.DataFrame:
    """Lê os registros da planilha, padroniza colunas e retorna DataFrame"""
    try:
        data = self.sheet.get_all_records()
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
    except Exception as e:
        st.error(f"Erro ao carregar planilha: {e}")
        return pd.DataFrame()

    # Padroniza nomes das colunas
    df.columns = [col.strip().lower() for col in df.columns]

    # Cria colunas obrigatórias se não existirem
    required_cols = [
        "id", "titulo", "categoria", "prazo", "status",
        "data_criacao", "autor", "descricao"
    ]
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""

    # Remove linhas completamente vazias
    df = df.dropna(how="all")

    # Ordena por data de criação (mais recentes primeiro)
    if "data_criacao" in df.columns:
        try:
            df["data_criacao"] = pd.to_datetime(df["data_criacao"], errors="coerce")
            df = df.sort_values("data_criacao", ascending=False)
        except Exception:
            pass

    return df.reset_index(drop=True)


    def atualizar_status(self, tarefa_id: str, novo_status: str) -> bool:
        """Atualiza o status da tarefa pelo ID"""
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
