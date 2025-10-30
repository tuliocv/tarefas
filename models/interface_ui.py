import streamlit as st

class InterfaceUI:
    @staticmethod
    def global_theme():
        st.markdown(
            """
            <style>
            :root {
              --bg:#f8fafc;
              --card:#ffffff;
              --muted:#64748b;
              --accent:#10b981;
              --accent-light:#d1fae5;
              --border:#e2e8f0;
              --shadow:0 2px 6px rgba(0,0,0,0.05);
            }

            .main {
              background-color: var(--bg);
              color:#0f172a;
              font-family: 'Inter', sans-serif;
            }

            /* Botões */
            .stButton>button {
              border-radius:8px;
              height:40px;
              background-color:var(--accent);
              color:white;
              border:none;
              font-weight:600;
              transition: all 0.2s ease;
            }
            .stButton>button:hover {
              background-color:#059669;
              transform: translateY(-1px);
            }

            /* Cards */
            .card {
              background-color: var(--card);
              border: 1px solid var(--border);
              border-radius:12px;
              padding:16px;
              margin-bottom:14px;
              box-shadow: var(--shadow);
              transition: box-shadow 0.2s ease;
            }
            .card:hover {
              box-shadow: 0 4px 10px rgba(0,0,0,0.08);
            }

            /* Chips */
            .chip {
              display:inline-block;
              background: var(--accent-light);
              color:#065f46;
              font-weight:500;
              padding:3px 10px;
              border-radius:999px;
              font-size:12px;
              border:1px solid #a7f3d0;
            }

            /* Textos */
            h1,h2,h3,h4 {
              color:#0f172a;
              font-family: 'Inter', sans-serif;
              font-weight:700;
            }
            .muted { color: var(--muted); }
            hr { border: none; border-top: 1px solid var(--border); margin: 1rem 0; }
            </style>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def page_title(texto: str):
        st.markdown(f"<h1 style='text-align:center; margin-bottom:0.5rem'>{texto}</h1>", unsafe_allow_html=True)

    @staticmethod
    def header(texto: str):
        st.markdown(f"<h2 style='margin:0.4rem 0 0.8rem 0'>{texto}</h2>", unsafe_allow_html=True)

    @staticmethod
    def section(texto: str):
        st.markdown(f"<h3 style='margin:0.4rem 0 0.6rem 0'>{texto}</h3>", unsafe_allow_html=True)

    @staticmethod
    def hr():
        st.markdown("<hr>", unsafe_allow_html=True)

    @staticmethod
    def chip(texto: str):
        st.markdown(f"<span class='chip'>{texto}</span>", unsafe_allow_html=True)

    @staticmethod
    def success(msg: str):
        st.success(msg)

    @staticmethod
    def warn(msg: str):
        st.warning(msg)

    @staticmethod
    def error(msg: str):
        st.error(msg)

    @staticmethod
    def info(msg: str):
        st.info(msg)

    @staticmethod
    def task_card(titulo: str, categoria: str, status: str, prazo: str, autor: str, data_criacao: str, cor: str, historico: str = ""):
        st.markdown(
            f"""
            <div class="card" style="border-left:6px solid {cor};">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <h4 style="margin:0;">{titulo}</h4>
                <span class="chip">{status}</span>
              </div>
              <div class="muted" style="margin:6px 0 8px 0">
                <b>Categoria:</b> {categoria} &nbsp;•&nbsp;
                <b>Prazo:</b> {prazo or '-'} &nbsp;•&nbsp;
                <b>Autor:</b> {autor}
              </div>
              <div style="font-size:12px;color:#64748b;"><i>Criado em {data_criacao}</i></div>
              {"<div style='margin-top:10px; color:#334155;'><i>"+historico+"</i></div>" if historico else ""}
            </div>
            """,
            unsafe_allow_html=True
        )
