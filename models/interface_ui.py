import streamlit as st

class InterfaceUI:
    @staticmethod
    def global_theme():
        st.markdown(
            """
            <style>
            :root{
              --bg:#0f172a; --card:#111827; --muted:#9ca3af; --accent:#22c55e;
              --chip:#1f2937; --chipb:#374151;
            }
            .main { background: linear-gradient(180deg, #0b1220 0%, #0f172a 100%); color:#e5e7eb;}
            .stButton>button { border-radius:10px; height:42px; }
            .card {
              background: linear-gradient(180deg, #0b1220 0%, #111827 100%);
              border: 1px solid #1f2937; border-radius:14px; padding:16px; margin-bottom:12px;
            }
            .chip { display:inline-block; background:var(--chip); border:1px solid var(--chipb);
                    padding:4px 10px; border-radius:999px; color:#cbd5e1; margin-right:6px; font-size:12px;}
            h1,h2,h3,h4 { color:#e5e7eb; }
            .muted { color:#9ca3af; }
            </style>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def page_title(texto: str):
        st.markdown(f"<h1 style='text-align:center; margin-bottom:0.5rem'>{texto}</h1>", unsafe_allow_html=True)

    @staticmethod
    def header(texto: str):
        st.markdown(f"<h2 style='margin:0.2rem 0 0.6rem 0'>{texto}</h2>", unsafe_allow_html=True)

    @staticmethod
    def section(texto: str):
        st.markdown(f"<h3 style='margin:0.4rem 0 0.6rem 0'>{texto}</h3>", unsafe_allow_html=True)

    @staticmethod
    def hr():
        st.markdown("<hr style='border-color:#1f2937;'>", unsafe_allow_html=True)

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
              <div style="font-size:12px;color:#94a3b8;"><i>Criado em {data_criacao}</i></div>
              {"<div style='margin-top:10px; color:#cbd5e1;'><i>"+historico+"</i></div>" if historico else ""}
            </div>
            """,
            unsafe_allow_html=True
        )
