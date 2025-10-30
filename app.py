# ============================================================
# ✅ Controle de Tarefas – compatível com estrutura real da planilha
# ============================================================

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
st.markdown("<h1 style='text-align:center;'>🗂️ Controle de Tarefas</h1>", unsafe_allow_html=True)


# ============================================================
# 🔐 AUTENTICAÇÃO MANUAL (bcrypt)
# ============================================================
creds = st.secrets["credentials"]["usernames"]
if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["user"] is None:
    InterfaceUI.header("🔐 Login de Usuário")
    username_input = st.text_input("Usuário")
    password_input = st.text_input("Senha", type="password")
    login_button = st.button("Entrar")

    if login_button:
        if username_input in creds:
            stored_pw = creds[username_input]["password"].encode("utf-8")
            if bcrypt.checkpw(password_input.encode("utf-8"), stored_pw):
                st.session_state["user"] = creds[username_input]["name"]
                st.success("✅ Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("❌ Senha incorreta.")
        else:
            st.error("❌ Usuário não encontrado.")
    st.stop()

nome = st.session_state["user"]
st.sidebar.success(f"Bem-vindo(a), {nome}! 👋")
if st.sidebar.button("Sair"):
    st.session_state["user"] = None
    st.rerun()


# ============================================================
# 🔗 CONEXÃO COM O GOOGLE SHEETS
# ============================================================
@st.cache_resource
def get_service():
    sheet_id = st.secrets["sheets"]["sheet_name"]
    return GoogleSheetsService(sheet_id)

sheets_service = get_service()
sheet = sheets_service.sheet


# ============================================================
# 🔧 UTILITÁRIOS
# ============================================================
@st.cache_data(ttl=60)
def get_headers():
    try:
        return [h.strip().lower() for h in sheet.row_values(1)]
    except Exception:
        return []

def ensure_column(df: pd.DataFrame, col: str, fill=""):
    if col not in df.columns:
        df[col] = fill
    return df

def id_to_row_map():
    values = sheet.get_all_values()
    if not values:
        return {}
    headers = [h.strip().lower() for h in values[0]]
    try:
        id_idx = headers.index("id")
    except ValueError:
        return {}
    mapping = {}
    for i, row in enumerate(values[1:], start=2):
        if len(row) > id_idx:
            mapping[row[id_idx]] = i
    return mapping

def update_row_fields(row_num: int, updates: dict):
    headers = get_headers()
    if not headers or not row_num:
        return False
    for k, v in updates.items():
        if k in headers:
            col_idx = headers.index(k) + 1
            sheet.update_cell(row_num, col_idx, v if v is not None else "")
    # Atualiza timestamp
    if "ultima_atualizacao" in headers:
        col_idx = headers.index("ultima_atualizacao") + 1
        sheet.update_cell(row_num, col_idx, datetime.now().strftime("%d/%m/%Y %H:%M"))
    return True

def append_row_with_optional_history(tarefa: Tarefa, autor: str, historico: str):
    """Adiciona nova linha na planilha com histórico e autor"""
    nova_linha = tarefa.to_list() + [historico, "", autor]  # histórico + ultima_atualização + autor
    sheet.append_row(nova_linha)

def cor_status(status):
    if status == "Concluída": return "#90EE90"
    elif status == "Em andamento": return "#FFD700"
    return "#F08080"


# ============================================================
# 🎨 INTERFACE PRINCIPAL
# ============================================================
aba = st.sidebar.radio("📍 Navegação", ["Nova Tarefa", "Minhas Tarefas", "Analytics", "Atualizar Tarefa"])

# ------------------------------------------------------------
# ➕ NOVA TAREFA
# ------------------------------------------------------------
if aba == "Nova Tarefa":
    InterfaceUI.header("➕ Adicionar Nova Tarefa")
    titulo = st.text_input("Título da tarefa")
    categoria = st.selectbox("Categoria", ["Pessoal", "Trabalho", "Estudo", "Outro"])
    prazo = st.date_input("Prazo")
    historico = st.text_area("Histórico (opcional)", height=160, placeholder="Adicione observações, contexto ou progresso...")

    if st.button("Salvar tarefa"):
        if titulo:
            tarefa = Tarefa(titulo, categoria, prazo.strftime("%d/%m/%Y"))
            append_row_with_optional_history(tarefa, nome, historico)
            st.success(f"Tarefa criada com sucesso ✅ (ID: {tarefa.id})")
        else:
            st.warning("⚠️ Preencha o título antes de salvar.")


# ------------------------------------------------------------
# 📋 MINHAS TAREFAS
# ------------------------------------------------------------
elif aba == "Minhas Tarefas":
    InterfaceUI.header("📋 Suas Tarefas")
    df = sheets_service.carregar_tarefas()
    df = ensure_column(df, "autor", "")
    df = ensure_column(df, "historico", "")

    if df.empty:
        st.info("Nenhuma tarefa cadastrada ainda.")
    else:
        df = df[df["autor"].str.strip().str.lower() == nome.strip().lower()]

        col1, col2 = st.columns(2)
        with col1:
            filtro_categoria = st.multiselect("Filtrar por categoria", sorted(df["categoria"].unique().tolist()))
        with col2:
            filtro_status = st.multiselect("Filtrar por status", sorted(df["status"].unique().tolist()))

        if filtro_categoria:
            df = df[df["categoria"].isin(filtro_categoria)]
        if filtro_status:
            df = df[df["status"].isin(filtro_status)]

        for _, row in df.iterrows():
            cor = cor_status(row.get("status", "Pendente"))
            InterfaceUI.styled_card(
                titulo=row.get("titulo", ""),
                categoria=row.get("categoria", ""),
                status=row.get("status", ""),
                prazo=row.get("prazo", ""),
                autor=row.get("autor", nome),
                data_criacao=row.get("data_criacao", ""),
                cor=cor
            )
            if str(row.get("historico", "")).strip():
                st.markdown(f"<div style='margin-top:-6px; margin-bottom:16px;'><i>{row['historico']}</i></div>", unsafe_allow_html=True)


# ------------------------------------------------------------
# 📊 ANALYTICS
# ------------------------------------------------------------
elif aba == "Analytics":
    InterfaceUI.header("📊 Dashboard de Tarefas")
    df = sheets_service.carregar_tarefas()
    df = ensure_column(df, "autor", "")

    if df.empty:
        st.info("Nenhum dado disponível ainda.")
    else:
        df = df[df["autor"].str.strip().str.lower() == nome.strip().lower()]
        dashboard = Dashboard(df)
        dashboard.kpi_cards()
        dashboard.grafico_status()
        dashboard.grafico_categoria()


# ------------------------------------------------------------
# ✍️ ATUALIZAR TAREFA
# ------------------------------------------------------------
elif aba == "Atualizar Tarefa":
    InterfaceUI.header("✍️ Atualizar Tarefas")
    df = sheets_service.carregar_tarefas()
    df = ensure_column(df, "autor", "")
    df = ensure_column(df, "historico", "")

    if df.empty:
        st.info("Nenhuma tarefa cadastrada ainda.")
        st.stop()

    df_user = df[df["autor"].str.strip().str.lower() == nome.strip().lower()]
    if df_user.empty:
        st.info("Você ainda não possui tarefas.")
        st.stop()

    st.dataframe(df_user[["id", "titulo", "categoria", "prazo", "status", "historico"]], use_container_width=True)
    tarefa_id = st.selectbox("Selecione a tarefa a editar:", df_user["id"].tolist())

    tarefa = df_user[df_user["id"] == tarefa_id].iloc[0]
    novo_titulo = st.text_input("Título", value=tarefa["titulo"])
    nova_categoria = st.selectbox("Categoria", ["Pessoal", "Trabalho", "Estudo", "Outro"],
                                  index=["Pessoal","Trabalho","Estudo","Outro"].index(tarefa["categoria"])
                                  if tarefa["categoria"] in ["Pessoal","Trabalho","Estudo","Outro"] else 0)
    novo_prazo = st.date_input("Prazo", value=pd.to_datetime(tarefa["prazo"], dayfirst=True))
    novo_status = st.selectbox("Status", ["Pendente", "Em andamento", "Concluída"],
                               index=["Pendente", "Em andamento", "Concluída"].index(tarefa["status"])
                               if tarefa["status"] in ["Pendente", "Em andamento", "Concluída"] else 0)
    novo_hist = st.text_area("Histórico", value=tarefa.get("historico", ""), height=150)

    if st.button("💾 Salvar alterações"):
        try:
            updates = {
                "titulo": novo_titulo,
                "categoria": nova_categoria,
                "prazo": novo_prazo.strftime("%d/%m/%Y"),
                "status": novo_status,
                "historico": novo_hist
            }
            row_map = id_to_row_map()
            row_num = row_map.get(tarefa_id)
            if row_num:
                update_row_fields(row_num, updates)
                st.success("✅ Tarefa atualizada com sucesso!")
                st.rerun()
            else:
                st.error("Tarefa não encontrada na planilha.")
        except Exception as e:
            st.error(f"Erro ao atualizar tarefa: {e}")
