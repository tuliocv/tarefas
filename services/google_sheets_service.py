# ============================================================
# ✅ Google Sheets Service – Alinhado ao cabeçalho real
# ============================================================

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

    # ============================================================
    # 📥 Carregar tarefas
    # ============================================================
    def carregar_tarefas(self) -> pd.DataFrame:
        """Lê a planilha, padroniza colunas e retorna DataFrame"""
        try:
            data = self.sheet.get_all_records()
            if not data:
                return pd.DataFrame()
            df = pd.DataFrame(data)
        except Exception as e:
            st.error(f"Erro ao carregar planilha: {e}")
            return pd.DataFrame()

        # Normaliza colunas
        df.columns = [col.strip().lower() for col in df.columns]

        # Garante colunas esperadas (baseado no seu cabeçalho real)
        required_cols = [
            "id", "data_criacao", "titulo", "categoria",
            "prazo", "status", "historico", "ultima_atualizacao", "autor"
        ]
        for col in required_cols:
            if col not in df.columns:
                df[col] = ""

        # Limpeza básica
        df = df.dropna(how="all")
        df["autor"] = df["autor"].astype(str).str.strip().str.lower()
        df["titulo"] = df["titulo"].astype(str).str.strip()
        df["status"] = df["status"].replace("", "Pendente")
        df["categoria"] = df["categoria"].replace("", "Outro")
        df["historico"] = df["historico"].astype(str).fillna("")

        # Ordena por data_criacao, se existir
        try:
            df["data_criacao"] = pd.to_datetime(df["data_criacao"], errors="coerce")
            df = df.sort_values("data_criacao", ascending=False)
        except Exception:
            pass

        return df.reset_index(drop=True)

    # ============================================================
    # 🔄 Atualizar status
    # ============================================================
    def atualizar_status(self, tarefa_id: str, novo_status: str) -> bool:
        """Atualiza o status da tarefa pelo ID"""
        try:
            valores = self.sheet.get_all_values()
            headers = [h.strip().lower() for h in valores[0]]

            if "id" not in headers or "status" not in headers:
                st.error("Planilha sem colunas esperadas: 'id' e 'status'.")
                return False

            id_idx = headers.index("id")
            status_idx = headers.index("status")

            for i, linha in enumerate(valores[1:], start=2):
                if len(linha) > id_idx and linha[id_idx] == tarefa_id:
                    self.sheet.update_cell(i, status_idx + 1, novo_status)
                    self.sheet.update_cell(i, headers.index("ultima_atualizacao") + 1, pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"))
                    return True
            return False
        except Exception as e:
            st.error(f"Erro ao atualizar status: {e}")
            return False
