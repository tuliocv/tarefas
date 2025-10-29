# ============================================================
# ✅ Controle de Tarefas – UX + Edição por Tabela (AgGrid)
# ============================================================

import streamlit as st
import pandas as pd
import bcrypt
from datetime import datetime

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

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
# 🔐 AUTENTICAÇÃO MANUAL (usando bcrypt)
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
sheet = sheets_service.sheet  # gspread worksheet


# ============================================================
# 🔧 HELPERS – Google Sheets
# ============================================================
@st.cache_data(ttl=60)
def get_headers():
    try:
        return sheet.row_values(1)
    except Exception:
        return []

def ensure_column(df: pd.DataFrame, col: str, fill=""):
    if col not in df.columns:
        df[col] = fill
    return df

def id_to_row_map():
    """Mapeia id -> número da linha na planilha (para updates rápidos)."""
    values = sheet.get_all_values()
    if not values:
        return {}
    headers = values[0]
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
    """Atualiza campos específicos (coluna por coluna) conforme o cabeçalho."""
    headers = get_headers()
    if not headers or not row_num:
        return False
    cells = []
    for k, v in updates.items():
        if k in headers:
            col_idx = headers.index(k) + 1
            sheet.update_cell(row_num, col_idx, v if v is not None else "")
    return True

def append_row_with_optional_description(tarefa: Tarefa, autor: str, descricao: str):
    """
    Mantém compatibilidade: usa to_list() + [autor] e,
    se existir coluna 'descricao', atualiza a célula após o append.
    """
    headers = get_headers()
    # 1) Append base
    nova_linha = tarefa.to_list() + [autor]
    sheet.append_row(nova_linha)
    # 2) Se houver 'descricao', achar a linha da tarefa e atualizar
    if "descricao" in headers and descricao:
        # encontra linha pelo id
        row_map = id_to_row_map()
        row_num = row_map.get(tarefa.id)
        if row_num:
            col_idx = headers.index("descricao") + 1
            sheet.update_cell(row_num, col_idx, descricao)


# ============================================================
# 🧠 FUNÇÕES AUXILIARES (UI)
# ============================================================
def cor_status(status):
    if status == "Concluída":
        return "#90EE90"  # verde
    elif status == "Em andamento":
        return "#FFD700"  # amarelo
    return "#F08080"      # vermelho


# ============================================================
# 🎨 INTERFACE PRINCIPAL
# ============================================================
aba = st.sidebar.radio("📍 Navegação", ["Nova Tarefa", "Minhas Tarefas", "Analytics", "Atualizar via Tabela"])

# ------------------------------------------------------------
# ➕ NOVA TAREFA (com DESCRIÇÃO multilinha)
# ------------------------------------------------------------
if aba == "Nova Tarefa":
    InterfaceUI.header("➕ Adicionar Nova Tarefa")
    titulo = st.text_input("Título da tarefa")
    categoria = st.selectbox("Categoria", ["Pessoal", "Trabalho", "Estudo", "Outro"])
    prazo = st.date_input("Prazo")
    descricao = st.text_area("Descrição (opcional)", height=160, placeholder="Detalhe sua tarefa aqui...")

    if st.button("Salvar tarefa"):
        if titulo:
            tarefa = Tarefa(titulo, categoria, prazo.strftime("%d/%m/%Y"))
            append_row_with_optional_description(tarefa, nome, descricao)
            st.success(f"Tarefa criada com sucesso ✅ (ID: {tarefa.id})")
        else:
            st.warning("⚠️ Preencha o título antes de salvar.")


# ------------------------------------------------------------
# 📋 MINHAS TAREFAS (cards)
# ------------------------------------------------------------
elif aba == "Minhas Tarefas":
    InterfaceUI.header("📋 Suas Tarefas")
    df = sheets_service.carregar_tarefas()
    df = ensure_column(df, "autor", "")
    df = ensure_column(df, "descricao", "")

    if df.empty:
        st.info("Nenhuma tarefa cadastrada ainda.")
    else:
        df = df[df["autor"] == nome] if "autor" in df.columns else df

        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            filtro_categoria = st.multiselect("Filtrar por categoria", sorted(df["categoria"].dropna().unique().tolist()))
        with col2:
            filtro_status = st.multiselect("Filtrar por status", sorted(df["status"].dropna().unique().tolist()))

        if filtro_categoria:
            df = df[df["categoria"].isin(filtro_categoria)]
        if filtro_status:
            df = df[df["status"].isin(filtro_status)]

        # Cards
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
            if str(row.get("descricao", "")).strip():
                st.markdown(f"<div style='margin-top:-6px; margin-bottom:16px;'><i>{row['descricao']}</i></div>", unsafe_allow_html=True)


# ------------------------------------------------------------
# 📊 DASHBOARD ANALYTICS
# ------------------------------------------------------------
elif aba == "Analytics":
    InterfaceUI.header("📊 Dashboard de Tarefas")
    df = sheets_service.carregar_tarefas()
    df = ensure_column(df, "autor", "")

    if df.empty:
        st.info("Nenhum dado disponível ainda.")
    else:
        df = df[df["autor"] == nome] if "autor" in df.columns else df
        dashboard = Dashboard(df)
        dashboard.kpi_cards()
        dashboard.grafico_status()
        dashboard.grafico_categoria()


# ------------------------------------------------------------
# ✍️ ATUALIZAR VIA TABELA (seleciona linha e clica salvar)
# ------------------------------------------------------------
elif aba == "Atualizar via Tabela":
    InterfaceUI.header("✍️ Atualizar Tarefas em Tabela")
    df = sheets_service.carregar_tarefas()
    df = ensure_column(df, "autor", "")
    df = ensure_column(df, "descricao", "")

    if df.empty:
        st.info("Nenhuma tarefa cadastrada ainda.")
        st.stop()

    # Filtra por autor logado, se existir coluna
    if "autor" in df.columns:
        df = df[df["autor"] == nome].copy()

    if df.empty:
        st.info("Você ainda não possui tarefas.")
        st.stop()

    # Ajustes de tipos
    # Mantemos 'prazo' como string (dd/mm/aaaa). Se vier como datetime, converte.
    if "prazo" in df.columns:
        def _fmt_date(x):
            if pd.isna(x):
                return ""
            if isinstance(x, str):
                return x
            try:
                return pd.to_datetime(x).strftime("%d/%m/%Y")
            except Exception:
                return str(x)
        df["prazo"] = df["prazo"].apply(_fmt_date)

    # Constrói grid editável
    gb = GridOptionsBuilder.from_dataframe(df)
    # Editáveis
    editable_cols = ["titulo", "categoria", "prazo", "status", "descricao"]
    for c in editable_cols:
        if c in df.columns:
            gb.configure_column(c, editable=True, wrapText=True, autoHeight=True)

    # Selectbox para status com domínios
    if "status" in df.columns:
        gb.configure_column(
            "status",
            cellEditor="agSelectCellEditor",
            cellEditorParams={"values": ["Pendente", "Em andamento", "Concluída"]}
        )

    # Seleção de única linha
    gb.configure_selection(selection_mode="single", use_checkbox=True)
    gb.configure_grid_options(domLayout="normal")

    grid_options = gb.build()
    grid_resp = AgGrid(
        df,
        gridOptions=grid_options,
        height=420,
        data_return_mode=DataReturnMode.AS_INPUT,
        update_mode=GridUpdateMode.MODEL_CHANGED | GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=False
    )

    df_editado = pd.DataFrame(grid_resp["data"])
    selecionadas = grid_resp["selected_rows"]

    st.markdown("---")
    colA, colB = st.columns([1,1])

    with colA:
        st.info("Selecione uma linha, edite as colunas desejadas e clique em **Salvar alterações**.")

    with colB:
        salvar = st.button("💾 Salvar alterações", type="primary")

    if salvar:
        try:
            headers = get_headers()
            if "id" not in df_editado.columns or "id" not in headers:
                st.error("A coluna 'id' é necessária para atualizar a planilha.")
                st.stop()

            # Mapa id -> linha
            row_map = id_to_row_map()
            if not row_map:
                st.error("Não foi possível localizar as linhas na planilha pelo 'id'.")
                st.stop()

            # Detecta diferenças (linha a linha)
            # Compara df_editado com df (original mostrado antes do AgGrid)
            original = df.reset_index(drop=True)
            editado = df_editado.reset_index(drop=True)

            changes = []  # lista de dicts: {row_num, updates{col:val}}
            for i in range(len(editado)):
                row_o = original.iloc[i]
                row_n = editado.iloc[i]
                diffs = {}
                for c in editable_cols:
                    if c in editado.columns:
                        vo = str(row_o.get(c, "") if row_o.get(c, "") is not None else "")
                        vn = str(row_n.get(c, "") if row_n.get(c, "") is not None else "")
                        if vo != vn:
                            diffs[c] = vn
                if diffs:
                    tarefa_id = str(row_n["id"])
                    row_num = row_map.get(tarefa_id)
                    if row_num:
                        changes.append({"row_num": row_num, "updates": diffs})

            if not changes:
                st.info("Nenhuma alteração para salvar.")
            else:
                for ch in changes:
                    update_row_fields(ch["row_num"], ch["updates"])
                st.success(f"Alterações salvas com sucesso ✅ ({len(changes)} linha(s) atualizada(s))")
                st.rerun()

        except Exception as e:
            st.error(f"Falha ao salvar alterações: {e}")
