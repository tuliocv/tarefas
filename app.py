import streamlit as st
import pandas as pd
from models.tarefa import Tarefa
from services.google_sheets_service import GoogleSheetsService
from datetime import datetime

st.set_page_config(page_title="Controle de Tarefas", page_icon="✅", layout="wide")

# --- Inicializa conexão ---
sheets_service = GoogleSheetsService(st.secrets["sheets"]["sheet_name"])
st.title("🗂️ Controle de Tarefas Pessoal (v2.1 – Interface e UX)")

aba = st.sidebar.radio("Navegação", ["Nova Tarefa", "Minhas Tarefas", "Atualizar Status"])

# --- Função auxiliar de cor ---
def cor_status(status):
    if status == "Concluída":
        return "#90EE90"  # verde claro
    elif status == "Em andamento":
        return "#FFFACD"  # amarelo claro
    return "#F08080"      # vermelho claro

# --- Nova tarefa ---
if aba == "Nova Tarefa":
    st.subheader("➕ Adicionar nova tarefa")
    col1, col2 = st.columns([3, 1])
    with col1:
        titulo = st.text_input("Título da tarefa")
        categoria = st.selectbox("Categoria", ["Pessoal", "Trabalho", "Estudo", "Outro"])
        prazo = st.date_input("Prazo")
    if st.button("Salvar tarefa"):
        if titulo:
            tarefa = Tarefa(titulo, categoria, prazo.strftime("%d/%m/%Y"))
            sheets_service.salvar_tarefa(tarefa)
            st.success(f"Tarefa criada com sucesso ✅ (ID: {tarefa.id})")
        else:
            st.warning("Preencha o título antes de salvar.")

# --- Minhas tarefas ---
elif aba == "Minhas Tarefas":
    st.subheader("📋 Suas tarefas")
    df = sheets_service.carregar_tarefas()

    if df.empty:
        st.info("Nenhuma tarefa cadastrada ainda.")
    else:
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            filtro_categoria = st.multiselect("Filtrar por categoria", df["categoria"].unique())
        with col2:
            filtro_status = st.multiselect("Filtrar por status", df["status"].unique())

        if filtro_categoria:
            df = df[df["categoria"].isin(filtro_categoria)]
        if filtro_status:
            df = df[df["status"].isin(filtro_status)]

        # Exibição em cards
        for _, row in df.iterrows():
            cor = cor_status(row["status"])
            with st.container():
                st.markdown(
                    f"""
                    <div style="background-color:{cor}; padding:15px; border-radius:10px; margin-bottom:10px;">
                        <h4>{row['titulo']}</h4>
                        <b>Categoria:</b> {row['categoria']}<br>
                        <b>Status:</b> {row['status']}<br>
                        <b>Prazo:</b> {row['prazo']}<br>
                        <small><i>Criado em {row['data_criacao']}</i></small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# --- Atualizar status ---
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
                st.error("Tarefa não encontrada.")
        else:
            st.warning("Informe o ID da tarefa.")
