# models/interface_ui.py
import streamlit as st

class InterfaceUI:
    @staticmethod
    def header(texto):
        st.markdown(f"<h2 style='color:#0E1117;'>{texto}</h2>", unsafe_allow_html=True)

    @staticmethod
    def styled_card(titulo, categoria, status, prazo, autor, data_criacao, cor):
        st.markdown(
            f"""
            <div style="background-color:{cor}; padding:15px; border-radius:10px; margin-bottom:12px;">
                <h4>{titulo}</h4>
                <b>Categoria:</b> {categoria}<br>
                <b>Status:</b> {status}<br>
                <b>Prazo:</b> {prazo}<br>
                <b>Autor:</b> {autor}<br>
                <small><i>Criado em {data_criacao}</i></small>
            </div>
            """,
            unsafe_allow_html=True
        )
