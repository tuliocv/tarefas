# ============================================================
# ✅ Controle de Tarefas v4.0 — Kanban + AI + Logs + UI moderna
# ============================================================

import streamlit as st
import pandas as pd
import bcrypt
from datetime import datetime

from models.tarefa import Tarefa
from models.dashboard import Dashboard
from models.interface_ui import InterfaceUI
from models.ai_insights import AIInsights
from models.kanban_board import KanbanBoard
from services.google_sheets_service import GoogleSheetsService

# -----------------------------
# Configurações iniciais + CSS
# -----------------------------
st.set_page_config(page_title="Controle de Tarefas", page_icon="✅", layout="wide")
InterfaceUI.global_theme()  # injeta CSS
InterfaceUI.page_title("🗂️ Controle de Tarefas — v4.0")

# -----------------------------
# Autenticação manual (bcrypt)
# -----------------------------
creds = st.secrets["credentials"]["usernames"]
if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["user"] is None:
    with st.container():
        InterfaceUI.header("🔐 Login de Usuário")
        c1, c2 = st.columns([1, 1])
        with c1:
            username_input = st.text_input("Usuário", placeholder="ex: tuliocv")
        with c2:
            password_input = st.text_input("Senha", type="password", placeholder="••••••••")

        if st.button("Entrar", use_container_width=True, type="primary"):
            if username_input in creds:
                stored_pw = creds[username_input]["password"].encode("utf-8")
                if bcrypt.checkpw(password_input.encode("utf-8"), stored_pw):
                    st.session_state["user"] = creds[username_input]["name"]
                    st.success("✅ Login realizado com sucesso!")
                    st.rerun()
                else:
                    InterfaceUI.error("❌ Senha incorreta.")
            else:
                InterfaceUI.error("❌ Usuário não encontrado.")
    st.stop()

nome = st.session_state["user"]
with st.sidebar:
    st.success(f"Bem-vindo(a), {nome}! 👋")
    if st.button("Sair", use_container_width=True):
        st.session_state["user"] = None
        st.rerun()

# -----------------------------
# Conexão com Google Sheets
# -----------------------------
@st.cache_resource
def get_service():
    sheet_id = st.secrets["sheets"]["sheet_name"]  # <- é o ID da planilha
    return GoogleSheetsService(sheet_id)

sheets_service = get_service()
sheet = sheets_service.sheet

# -----------------------------
# Utilitários
# -----------------------------
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
        if len(row) > id_idx and row[id_idx]:
            mapping[row[id_idx]] = i
    return mapping

def update_row_fields(row_num: int, updates: dict, usuario: str = "Sistema"):
    """Atualiza campos, carimba 'ultima_atualizacao' e registra logs por campo alterado."""
    headers = get_headers()
    if not headers or not row_num:
        return False

    # captura valor anterior
    valores_antigos = sheet.row_values(row_num)
    if len(valores_antigos) < len(headers):
        valores_antigos += [""] * (len(headers) - len(valores_antigos))
    antigo_dict = dict(zip(headers, valores_antigos))

    # atualiza campos com log
    for k, v in updates.items():
        kl = k.strip().lower()
        if kl in headers:
            col_idx = headers.index(kl) + 1
            antigo = antigo_dict.get(kl, "")
            novo = "" if v is None else str(v)
            if str(antigo) != novo:
                sheet.update_cell(row_num, col_idx, novo)
                sheets_service.registrar_log(
                    usuario=usuario,
                    id_tarefa=antigo_dict.get("id", "N/A"),
                    campo=kl,
                    valor_antigo=antigo,
                    valor_novo=novo
                )

    # atualiza timestamp + log
    if "ultima_atualizacao" in headers:
        col_idx = headers.index("ultima_atualizacao") + 1
        agora = datetime.now().strftime("%d/%m/%Y %H:%M")
        sheet.update_cell(row_num, col_idx, agora)
        sheets_service.registrar_log(
            usuario=usuario,
            id_tarefa=antigo_dict.get("id", "N/A"),
            campo="ultima_atualizacao",
            valor_antigo=antigo_dict.get("ultima_atualizacao", ""),
            valor_novo=agora
        )
    return True

def append_row_with_history(tarefa: Tarefa, autor: str, historico: str):
    """Adiciona nova linha conforme a ordem oficial de colunas."""
    nova_linha = tarefa.to_list() + [historico or "", "", autor]
    sheet.append_row(nova_linha)
    # log de criação
    try:
        sheets_service.registrar_log(autor, tarefa.id, "criação", "", f"Tarefa '{tarefa.titulo}' criada")
    except Exception:
        pass

def cor_status(status: str):
    return {"Concluída": "#90EE90", "Em andamento": "#FFD700"}.get(status, "#F08080")

def append_note_to_history(row_num: int, usuario: str, nota: str, acao: str = ""):
    """Concatena nota no campo 'historico' com timestamp/autor."""
    headers = get_headers()
    if "historico" not in headers:
        return
    idx_hist = headers.index("historico") + 1
    texto_atual = sheet.cell(row_num, idx_hist).value or ""
    stamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    linha = f"[{stamp}] {usuario}: {acao} {nota}".strip()
    novo_texto = (texto_atual + ("\n" if texto_atual else "") + linha)
    sheet.update_cell(row_num, idx_hist, novo_texto)
    sheets_service.registrar_log(usuario, sheet.cell(row_num, headers.index("id") + 1).value, "historico", texto_atual, novo_texto)

# ------------------------------------------------------------
# Navegação
# ------------------------------------------------------------
aba = st.sidebar.radio(
    "📍 Navegação",
    ["Nova Tarefa", "Minhas Tarefas", "Kanban", "Analytics", "AI Insights", "Atualizar Tarefa", "Logs"]
)

# ------------------------------------------------------------
# ➕ Nova Tarefa
# ------------------------------------------------------------
if aba == "Nova Tarefa":
    InterfaceUI.section("➕ Adicionar Nova Tarefa")
    col1, col2 = st.columns([2, 1])
    with col1:
        titulo = st.text_input("Título da tarefa")
        historico = st.text_area("Histórico (opcional)", height=140, placeholder="Observações, contexto, links...")
    with col2:
        categoria = st.selectbox("Categoria", ["Pessoal", "Trabalho", "Estudo", "Outro"])
        prazo = st.date_input("Prazo")

    if st.button("Salvar tarefa", type="primary", use_container_width=True):
        if titulo.strip():
            tarefa = Tarefa(titulo.strip(), categoria, prazo.strftime("%d/%m/%Y"))
            append_row_with_history(tarefa, nome, historico)
            InterfaceUI.success(f"Tarefa criada com sucesso ✅ (ID: {tarefa.id})")
        else:
            InterfaceUI.warn("⚠️ Preencha o título antes de salvar.")

# ------------------------------------------------------------
# 📋 Minhas Tarefas (lista)
# ------------------------------------------------------------
elif aba == "Minhas Tarefas":
    InterfaceUI.section("📋 Suas Tarefas")
    df = sheets_service.carregar_tarefas()
    df = ensure_column(df, "autor", "")
    df = ensure_column(df, "historico", "")

    if df.empty:
        InterfaceUI.info("Nenhuma tarefa cadastrada ainda.")
    else:
        df = df[df["autor"].astype(str).str.strip().str.lower() == nome.strip().lower()]
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            filtro_categoria = st.multiselect("Categoria", sorted(df["categoria"].dropna().unique().tolist()))
        with c2:
            filtro_status = st.multiselect("Status", sorted(df["status"].dropna().unique().tolist()))
        with c3:
            if st.button("🔄 Atualizar lista", use_container_width=True):
                st.cache_data.clear()
                st.rerun()

        if filtro_categoria:
            df = df[df["categoria"].isin(filtro_categoria)]
        if filtro_status:
            df = df[df["status"].isin(filtro_status)]

        for _, row in df.iterrows():
            InterfaceUI.task_card(
                titulo=row.get("titulo", ""),
                categoria=row.get("categoria", ""),
                status=row.get("status", ""),
                prazo=row.get("prazo", ""),
                autor=row.get("autor", nome),
                data_criacao=row.get("data_criacao", ""),
                cor=cor_status(row.get("status", "Pendente")),
                historico=row.get("historico", "")
            )

# ------------------------------------------------------------
# 🗂 Kanban
# ------------------------------------------------------------
elif aba == "Kanban":
    InterfaceUI.section("🗂 Kanban de Tarefas")
    df = sheets_service.carregar_tarefas()
    if df.empty:
        InterfaceUI.info("Nenhuma tarefa cadastrada ainda.")
        st.stop()

    df = df[df["autor"].astype(str).str.strip().str.lower() == nome.strip().lower()]

    def mover_callback(task_id: str, novo_status: str, nota: str):
        # resolve linha
        row_map = id_to_row_map()
        row_num = row_map.get(task_id)
        if not row_num:
            InterfaceUI.error("Tarefa não encontrada na planilha.")
            return
        # atualiza status + opcionalmente histórico
        update_row_fields(row_num, {"status": novo_status}, usuario=nome)
        if nota.strip():
            append_note_to_history(row_num, usuario=nome, nota=nota, acao=f"[Kanban] → {novo_status}")

    KanbanBoard(df).render(on_move=mover_callback)

# ------------------------------------------------------------
# 📊 Analytics
# ------------------------------------------------------------
elif aba == "Analytics":
    InterfaceUI.section("📊 Dashboard de Tarefas")
    df = sheets_service.carregar_tarefas()
    if df.empty:
        InterfaceUI.info("Nenhum dado disponível ainda.")
    else:
        df = df[df["autor"].astype(str).str.strip().str.lower() == nome.strip().lower()]
        dash = Dashboard(df)
        dash.kpi_cards()
        dash.tempo_medio_conclusao()
        dash.grafico_evolucao()
        dash.grafico_categoria()
        dash.grafico_status()

# ------------------------------------------------------------
# 🧠 AI Insights
# ------------------------------------------------------------
elif aba == "AI Insights":
    InterfaceUI.section("🧠 Insights Automáticos")
    df = sheets_service.carregar_tarefas()
    if df.empty:
        InterfaceUI.info("Nenhum dado disponível ainda.")
    else:
        df = df[df["autor"].astype(str).str.strip().str.lower() == nome.strip().lower()]
        ai = AIInsights(df)
        ai.sentimento_historico()
        InterfaceUI.hr()
        ai.recomendacoes()

# ------------------------------------------------------------
# ✍️ Atualizar Tarefa
# ------------------------------------------------------------
elif aba == "Atualizar Tarefa":
    InterfaceUI.section("✍️ Atualizar Tarefas")
    df = sheets_service.carregar_tarefas()
    if df.empty:
        InterfaceUI.info("Nenhuma tarefa cadastrada ainda.")
        st.stop()
    df_user = df[df["autor"].astype(str).str.strip().str.lower() == nome.strip().lower()]
    if df_user.empty:
        InterfaceUI.info("Você ainda não possui tarefas.")
        st.stop()

    st.dataframe(df_user[["id", "titulo", "categoria", "prazo", "status", "historico"]], use_container_width=True)
    tarefa_id = st.selectbox("Selecione a tarefa:", df_user["id"].tolist())

    tarefa = df_user[df_user["id"] == tarefa_id].iloc[0]
    novo_titulo = st.text_input("Título", value=tarefa["titulo"])
    categorias_padrao = ["Pessoal", "Trabalho", "Estudo", "Outro"]
    idx_cat = categorias_padrao.index(tarefa["categoria"]) if tarefa["categoria"] in categorias_padrao else 0
    nova_categoria = st.selectbox("Categoria", categorias_padrao, index=idx_cat)

    # data robusta
    try:
        prazo_value = pd.to_datetime(tarefa["prazo"], dayfirst=True, errors="coerce")
        if pd.isna(prazo_value):
            prazo_value = datetime.today()
    except Exception:
        prazo_value = datetime.today()
    novo_prazo = st.date_input("Prazo", value=prazo_value)

    status_padrao = ["Pendente", "Em andamento", "Concluída"]
    idx_status = status_padrao.index(tarefa["status"]) if tarefa["status"] in status_padrao else 0
    novo_status = st.selectbox("Status", status_padrao, index=idx_status)

    novo_hist = st.text_area("Histórico", value=tarefa.get("historico", ""), height=150)

    if st.button("💾 Salvar alterações", type="primary"):
        updates = {
            "titulo": novo_titulo,
            "categoria": nova_categoria,
            "prazo": novo_prazo.strftime("%d/%m/%Y"),
            "status": novo_status,
            "historico": novo_hist,
        }
        row_map = id_to_row_map()
        row_num = row_map.get(tarefa_id)
        if row_num:
            ok = update_row_fields(row_num, updates, usuario=nome)
            if ok:
                InterfaceUI.success("✅ Tarefa atualizada com sucesso!")
                st.rerun()
        else:
            InterfaceUI.error("Tarefa não encontrada na planilha.")

# ------------------------------------------------------------
# 📜 Logs
# ------------------------------------------------------------
elif aba == "Logs":
    InterfaceUI.section("📜 Histórico de Alterações")
    try:
        log_sheet = sheet.spreadsheet.worksheet("Logs")
        data = log_sheet.get_all_records()
        if not data:
            InterfaceUI.info("Nenhum log registrado ainda.")
        else:
            df_logs = pd.DataFrame(data)
            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                filtro_usuario = st.selectbox("Usuário", ["(todos)"] + sorted(df_logs["usuario"].unique()))
            with c2:
                filtro_tarefa = st.text_input("ID da tarefa contém", "")
            with c3:
                if st.button("⬇️ Baixar CSV", use_container_width=True):
                    st.download_button(
                        label="Baixar agora",
                        data=df_logs.to_csv(index=False).encode("utf-8"),
                        file_name="logs_tarefas.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

            if filtro_usuario != "(todos)":
                df_logs = df_logs[df_logs["usuario"] == filtro_usuario]
            if filtro_tarefa.strip():
                df_logs = df_logs[df_logs["id_tarefa"].astype(str).str.contains(filtro_tarefa.strip(), case=False)]

            st.dataframe(df_logs.sort_values("data_hora", ascending=False), use_container_width=True)
    except Exception:
        InterfaceUI.warn("A aba 'Logs' ainda não existe. Ela será criada automaticamente na primeira atualização de tarefa.")
