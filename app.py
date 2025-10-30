# ============================================================
# ✅ Controle de Tarefas – Filtros, Tema V2, IA Preditiva e Kanban (estático)
# ============================================================

import streamlit as st
import pandas as pd
import bcrypt
from datetime import datetime, date

from models.tarefa import Tarefa
from models.dashboard import Dashboard
from models.interface_ui import InterfaceUI   # <-- Tema V2
from models.ai_insights import AIInsights     # <-- IA com risco de atraso
from services.google_sheets_service import GoogleSheetsService


# ============================================================
# ⚙️ CONFIGURAÇÕES INICIAIS
# ============================================================
st.set_page_config(page_title="Controle de Tarefas", page_icon="✅", layout="wide")
InterfaceUI.page_header("🗂️ Controle de Tarefas")  # cabeçalho bonito


# ============================================================
# 🔐 AUTENTICAÇÃO MANUAL (bcrypt)
# ============================================================
creds = st.secrets["credentials"]["usernames"]
if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["user"] is None:
    InterfaceUI.section_title("🔐 Login de Usuário")
    username_input = st.text_input("Usuário")
    password_input = st.text_input("Senha", type="password")
    if st.button("Entrar"):
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
with st.sidebar:
    st.success(f"Bem-vindo(a), {nome}! 👋")
    if st.button("Sair"):
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
    """Adiciona nova linha na planilha conforme colunas reais:
    id, data_criacao, titulo, categoria, prazo, status, historico, ultima_atualizacao, autor
    """
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    linha = [
        tarefa.id, tarefa.data_criacao, tarefa.titulo, tarefa.categoria,
        tarefa.prazo, tarefa.status,
        historico or "",
        "",              # ultima_atualizacao (vazia na criação)
        autor
    ]
    sheet.append_row(linha)

def parse_prazo_safe(x):
    try:
        d = pd.to_datetime(x, dayfirst=True, errors="coerce")
        return d
    except Exception:
        return pd.NaT

def is_overdue(prazo_str, status_str):
    d = parse_prazo_safe(prazo_str)
    if pd.isna(d):
        return False
    if str(status_str).strip().lower() == "concluída":
        return False
    return d.date() < date.today()

def cor_status(status):
    if status == "Concluída": return "#90EE90"
    elif status == "Em andamento": return "#FFD700"
    return "#F08080"


# ============================================================
# 🎨 INTERFACE PRINCIPAL
# ============================================================
aba = st.sidebar.radio(
    "📍 Navegação",
    ["Nova Tarefa", "Minhas Tarefas", "Analytics", "Atualizar Tarefa", "Kanban"]
)

# ------------------------------------------------------------
# ➕ NOVA TAREFA
# ------------------------------------------------------------
if aba == "Nova Tarefa":
    InterfaceUI.section_title("➕ Adicionar Nova Tarefa")
    col_a, col_b = st.columns([2, 1])
    with col_a:
        titulo = st.text_input("Título da tarefa")
    with col_b:
        categoria = st.selectbox("Categoria", ["Pessoal", "Trabalho", "Estudo", "Outro"])
    prazo = st.date_input("Prazo")
    historico = st.text_area("Histórico (opcional)", height=140, placeholder="Adicione observações, contexto ou progresso...")

    if st.button("Salvar tarefa", type="primary", use_container_width=True):
        if titulo:
            tarefa = Tarefa(titulo, categoria, prazo.strftime("%d/%m/%Y"))
            append_row_with_optional_history(tarefa, nome, historico)
            st.success(f"Tarefa criada com sucesso ✅ (ID: {tarefa.id})")
        else:
            st.warning("⚠️ Preencha o título antes de salvar.")


# ------------------------------------------------------------
# 📋 MINHAS TAREFAS (com busca/ordenação/atrasadas)
# ------------------------------------------------------------
elif aba == "Minhas Tarefas":
    InterfaceUI.section_title("📋 Suas Tarefas")
    df = sheets_service.carregar_tarefas()
    for c in ["autor", "historico", "status", "categoria", "prazo", "titulo", "data_criacao"]:
        df = ensure_column(df, c, "")

    if df.empty:
        st.info("Nenhuma tarefa cadastrada ainda.")
    else:
        # Filtros avançados
        df = df[df["autor"].str.strip().str.lower() == nome.strip().lower()]

        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1.5, 1, 0.8])
            with col1:
                q = st.text_input("🔎 Buscar (título/histórico/categoria/status)").strip().lower()
            with col2:
                ordenar_por = st.selectbox("Ordenar por", ["Prazo (mais próximo)", "Data de criação (mais recente)", "Título (A→Z)"])
            with col3:
                only_overdue = st.checkbox("Somente atrasadas", value=False)
            with col4:
                if st.button("🔁 Recarregar"):
                    st.cache_data.clear()
                    st.rerun()

        if q:
            df = df[
                df["titulo"].str.lower().str.contains(q, na=False) |
                df["historico"].str.lower().str.contains(q, na=False) |
                df["categoria"].str.lower().str.contains(q, na=False) |
                df["status"].str.lower().str.contains(q, na=False)
            ]

        if only_overdue:
            df = df[df.apply(lambda r: is_overdue(r["prazo"], r["status"]), axis=1)]

        # Ordenação
        if ordenar_por == "Prazo (mais próximo)":
            df["_prazo_dt"] = df["prazo"].apply(parse_prazo_safe)
            df = df.sort_values(by="_prazo_dt", ascending=True, na_position="last").drop(columns=["_prazo_dt"])
        elif ordenar_por == "Data de criação (mais recente)":
            df["_criacao_dt"] = pd.to_datetime(df["data_criacao"], errors="coerce", dayfirst=True)
            df = df.sort_values(by="_criacao_dt", ascending=False, na_position="last").drop(columns=["_criacao_dt"])
        else:
            df = df.sort_values(by="titulo", ascending=True, na_position="last")

        # Cards
        if df.empty:
            st.info("Nada a exibir com esses filtros.")
        else:
            for _, row in df.iterrows():
                atrasada = is_overdue(row.get("prazo", ""), row.get("status", ""))
                badge = "🔥 Atrasada" if atrasada else ("✅ Concluída" if row.get("status") == "Concluída" else "⏳ Em andamento" if row.get("status") == "Em andamento" else "📝 Pendente")
                InterfaceUI.styled_card(
                    titulo=row.get("titulo", ""),
                    categoria=row.get("categoria", ""),
                    status=f"{row.get('status','')}  ·  {badge}",
                    prazo=row.get("prazo", ""),
                    autor=row.get("autor", nome),
                    data_criacao=row.get("data_criacao", ""),
                    cor=cor_status(row.get("status", "")),
                    highlight=atrasada
                )
                if str(row.get("historico", "")).strip():
                    st.markdown(f"<div style='margin-top:-8px; margin-bottom:18px;'><i>{row['historico']}</i></div>", unsafe_allow_html=True)


# ------------------------------------------------------------
# 📊 ANALYTICS (inclui IA preditiva)
# ------------------------------------------------------------
elif aba == "Analytics":
    InterfaceUI.section_title("📊 Dashboard de Tarefas")
    df = sheets_service.carregar_tarefas()
    for c in ["autor", "status", "data_criacao", "ultima_atualizacao", "historico", "categoria", "prazo"]:
        df = ensure_column(df, c, "")

    if df.empty:
        st.info("Nenhum dado disponível ainda.")
    else:
        df_user = df[df["autor"].str.strip().str.lower() == nome.strip().lower()]

        # KPI + Gráficos
        dashboard = Dashboard(df_user)
        dashboard.kpi_cards()
        dashboard.tempo_medio_conclusao()
        dashboard.grafico_evolucao()
        dashboard.grafico_categoria()
        dashboard.grafico_status()

        # IA – Sentimento + Risco de Atraso
        st.divider()
        InterfaceUI.section_title("🤖 IA – Insights")
        ai = AIInsights(df_user)
        ai.sentimento_historico()
        ai.risco_atraso()  # <- nova função: previsão simples de risco


# ------------------------------------------------------------
# ✍️ ATUALIZAR TAREFA
# ------------------------------------------------------------
elif aba == "Atualizar Tarefa":
    InterfaceUI.section_title("✍️ Atualizar Tarefas")
    df = sheets_service.carregar_tarefas()
    for c in ["autor", "historico"]:
        df = ensure_column(df, c, "")

    if df.empty:
        st.info("Nenhuma tarefa cadastrada ainda.")
        st.stop()

    df_user = df[df["autor"].str.strip().str.lower() == nome.strip().lower()]
    if df_user.empty:
        st.info("Você ainda não possui tarefas.")
        st.stop()

    st.dataframe(
        df_user[["id", "titulo", "categoria", "prazo", "status", "historico"]],
        use_container_width=True
    )
    tarefa_id = st.selectbox("Selecione a tarefa a editar:", df_user["id"].tolist())

    tarefa = df_user[df_user["id"] == tarefa_id].iloc[0]
    novo_titulo = st.text_input("Título", value=tarefa["titulo"])
    nova_categoria = st.selectbox(
        "Categoria", ["Pessoal", "Trabalho", "Estudo", "Outro"],
        index=["Pessoal","Trabalho","Estudo","Outro"].index(tarefa["categoria"])
        if tarefa["categoria"] in ["Pessoal","Trabalho","Estudo","Outro"] else 0
    )

    # Prazo seguro
    prazo_value = parse_prazo_safe(tarefa["prazo"])
    if pd.isna(prazo_value):
        prazo_value = datetime.today()
    novo_prazo = st.date_input("Prazo", value=prazo_value)

    novo_status = st.selectbox(
        "Status", ["Pendente", "Em andamento", "Concluída"],
        index=["Pendente", "Em andamento", "Concluída"].index(tarefa["status"])
        if tarefa["status"] in ["Pendente", "Em andamento", "Concluída"] else 0
    )
    novo_hist = st.text_area("Histórico", value=tarefa.get("historico", ""), height=150)

    if st.button("💾 Salvar alterações", type="primary"):
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


# ------------------------------------------------------------
# 🧩 KANBAN (estático)
# ------------------------------------------------------------
elif aba == "Kanban":
    InterfaceUI.section_title("🧩 Kanban – Visualização de Status")
    df = sheets_service.carregar_tarefas()
    for c in ["autor", "status", "titulo", "prazo", "categoria"]:
        df = ensure_column(df, c, "")

    if df.empty:
        st.info("Nenhuma tarefa cadastrada ainda.")
        st.stop()

    df_user = df[df["autor"].str.strip().str.lower() == nome.strip().lower()]
    cols = st.columns(3)
    buckets = {
        "Pendente": df_user[df_user["status"] == "Pendente"],
        "Em andamento": df_user[df_user["status"] == "Em andamento"],
        "Concluída": df_user[df_user["status"] == "Concluída"],
    }
    for col, (status_lbl, dfi) in zip(cols, buckets.items()):
        with col:
            InterfaceUI.pill_title(status_lbl)
            if dfi.empty:
                InterfaceUI.empty_card("Sem tarefas")
            else:
                for _, row in dfi.iterrows():
                    atrasada = is_overdue(row.get("prazo",""), row.get("status",""))
                    badge = "🔥 Atrasada" if atrasada else "🟢 OK"
                    InterfaceUI.small_task_card(
                        titulo=row.get("titulo",""),
                        extra=f"{row.get('categoria','')} · {row.get('prazo','')} · {badge}",
                        highlight=atrasada
                    )
