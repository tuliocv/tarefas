# models/interface_ui.py
import streamlit as st

class InterfaceUI:
    @staticmethod
    def header(texto: str):
        st.markdown(f"<h2 style='margin-top:0'>{texto}</h2>", unsafe_allow_html=True)

    @staticmethod
    def section_title(texto: str):
        st.markdown(f"<h3 style='margin-top:0.5rem'>{texto}</h3>", unsafe_allow_html=True)

    @staticmethod
    def styled_card(titulo: str, categoria: str, status: str, prazo: str, autor: str, data_criacao: str, cor: str = "#FFF"):
        st.markdown(
            f"""
            <div style="
                background-color:{cor};
                padding:15px; border-radius:10px; margin-bottom:10px;
                border:1px solid #ddd;">
                <h4 style="margin:0 0 6px 0;">{titulo}</h4>
                <b>Categoria:</b> {categoria} &nbsp;&nbsp;
                <b>Status:</b> {status} &nbsp;&nbsp;
                <b>Prazo:</b> {prazo} &nbsp;&nbsp;
                <b>Autor:</b> {autor} <br>
                <small><i>Criado em {data_criacao}</i></small>
            </div>
            """,
            unsafe_allow_html=True
        )
