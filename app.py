import streamlit as st
from models.tarefa import Tarefa
from services.google_sheets_service import GoogleSheetsService

# ===================================
# CONFIGURAÇÃO GERAL
# ===================================
st.set_page_config(page_title="Controle de Tarefas", page_icon="✅", layout="centered")

# Inicializa conexão com o Google Sheets via secrets
sheets_service = GoogleSheetsService(st.secrets["sheets"]["sheet_name"])

# ===================================
# INTERFACE
# ===================================
st.title("🗂️ Controle de Tarefas Pessoal (POO + Google Sheets)")

aba = st.sidebar.radio("Navegação", ["Nova Tarefa", "Minhas Tarefas", "Atualizar Status"])

# -----------------------------------
# ➕ Nova tarefa
# -----------------------------------
if aba == "Nova Tarefa":
    st.subheader("Adicionar nova tarefa")
    titulo = st.text_input("Título da tarefa")
    categoria = st.selectbox("Categoria", ["Pessoal", "Trabalho", "Estudo", "Outro"])
    prazo = st.date_input("Prazo")

    if st.button("Salvar"):
        if titulo:
            tarefa = Tarefa(titulo, categoria, prazo.strftime("%d/%m/%Y"))
            sheets_service.salvar_tarefa(tarefa)
            st.success(f"Tarefa criada com sucesso ✅ (ID: {tarefa.id})")
        else:
            st.warning("Preencha o título antes de salvar.")

# -----------------------------------
# 📋 Visualizar tarefas
# -----------------------------------
elif aba == "Minhas Tarefas":
    st.subheader("📊 Suas tarefas")
    df = sheets_service.carregar_tarefas()

    if not df.empty:
        filtro_status = st.multiselect("Filtrar por status", df["status"].unique())
        if filtro_status:
            df = df[df["status"].isin(filtro_status)]
        st.dataframe(df[["id", "titulo", "categoria", "prazo", "status"]], use_container_width=True)
    else:
        st.info("Nenhuma tarefa cadastrada ainda.")

# -----------------------------------
# 🔄 Atualizar status
# -----------------------------------
elif aba == "Atualizar Status":
    st.subheader("Atualizar status da tarefa")
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
