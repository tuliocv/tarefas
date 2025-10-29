import streamlit as st
import pandas as pd
import bcrypt
from datetime import datetime

from models.tarefa import Tarefa
from services.google_sheets_service import GoogleSheetsService

# ============================================================
# ⚙️ CONFIGURAÇÕES INICIAIS
# ============================================================
st.set_page_config(page_title="Controle de Tarefas", page_icon="✅", layout="wide")
st.title("🗂️ Controle de Tarefas")

# ============================================================
# 🔐 AUTENTICAÇÃO MANUAL (usando bcrypt)
# ============================================================
creds = st.secrets["credentials"]["usernames"]
cookie = st.secrets["cookie"]

if "user" not in st.session_state:
    st.session_state["user"] = None

# --- Tela de login ---
if st.session_state["user"] is None:
    st.subheader("🔐 Login")
    username_input = st.text_input("Usuário")
    password_input = st.text_input("Senha", type="password")
    login_button = st.button("Entrar")

    if login_button:
        if username_input in creds:
            stored_pw = creds[username_input]["password"].encode("utf-8")
            if bcrypt.checkpw(password_input.encode("utf-8"), stored_pw):
                st.session_state["user"] = creds[username_input]["name"]
                st.success("Login realizado com sucesso! ✅")
                st.rerun()
            else:
                st.error("❌ Senha incorreta.")
        else:
            st.error("❌ Usuário não encontrado.")
    st.stop()

# --- Sessão logada ---
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

# ============================================================
# 🧠 FUNÇÕES AUXILIARES
# ============================================================
def cor_status(status):
    if status == "Concluída":
        return "#90EE90"  # verde-claro
    elif status == "Em andamento":
        return "#FFFACD"  # amarelo-claro
    return "#F08080"      # vermelho-claro

# ============================================================
# 🎨 INTERFACE PRINCIPAL
# ============================================================
aba = st.sidebar.radio("📍 Navegação", ["Nova Tarefa", "Minhas Tarefas", "Atualizar Status"])

# ------------------------------------------------------------
# ➕ NOVA TAREFA
# ------------------------------------------------------------
if aba == "Nova Tarefa":
    st.subheader("➕ Adicionar nova tarefa")
    titulo = st.text_input("Título da tarefa")
    categoria = st.selectbox("Categoria", ["Pessoal", "Trabalho", "Estudo", "Outro"])
    prazo = st.date_input("Prazo")

    if st.button("Salvar tarefa"):
        if titulo:
            tarefa = Tarefa(titulo, categoria, prazo.strftime("%d/%m/%Y"))
            nova_linha = tarefa.to_list() + [nome]
            sheets_service.sheet.append_row(nova_linha)
            st.success(f"Tarefa criada com sucesso ✅ (ID: {tarefa.id})")
        else:
            st.warning("⚠️ Preencha o título antes de salvar.")

# ------------------------------------------------------------
# 📋 MINHAS TAREFAS
# ------------------------------------------------------------
elif aba == "Minhas Tarefas":
    st.subheader("📋 Suas tarefas")
    df = sheets_service.carregar_tarefas()

    if df.empty:
        st.info("Nenhuma tarefa cadastrada ainda.")
    else:
        if "autor" in df.columns:
            df = df[df["autor"] == nome]

        col1, col2 = st.columns(2)
        with col1:
            filtro_categoria = st.multiselect("Filtrar por categoria", df["categoria"].unique())
        with col2:
            filtro_status = st.multiselect("Filtrar por status", df["status"].unique())

        if filtro_categoria:
            df = df[df["categoria"].isin(filtro_categoria)]
        if filtro_status:
            df = df[df["status"].isin(filtro_status)]

        for _, row in df.iterrows():
            cor = cor_status(row["status"])
            st.markdown(
                f"""
                <div style="background-color:{cor}; padding:15px; border-radius:10px; margin-bottom:10px;">
                    <h4>{row['titulo']}</h4>
                    <b>Categoria:</b> {row['categoria']}<br>
                    <b>Status:</b> {row['status']}<br>
                    <b>Prazo:</b> {row['prazo']}<br>
                    <b>Autor:</b> {row.get('autor', nome)}<br>
                    <small><i>Criado em {row['data_criacao']}</i></small>
                </div>
                """,
                unsafe_allow_html=True
            )

# ------------------------------------------------------------
# 🔄 ATUALIZAR STATUS
# ------------------------------------------------------------
elif aba == "Atualizar Status":
    st.subheader("🔄 Atualizar status da tarefa")
    tarefa_id = st.text_input("ID da tarefa")
    novo_status = st.selectbox("Novo status", ["Pendente", "Em andamento", "Concluída"])

    if st.button("Atualizar"):
        if tarefa_id:
            ok = sheets_service.atualizar_status(tarefa_id, novo_status)
            if ok:
                st.success("Status atualizado com sucesso ✅")
            else:
                st.error("❌ Tarefa não encontrada.")
        else:
            st.warning("⚠️ Informe o ID da tarefa.")
