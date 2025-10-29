import streamlit as st

class InterfaceUI:
    @staticmethod
    def header(titulo: str):
        st.markdown(
            f"""
            <h2 style="text-align:center; color:#0078D7;">{titulo}</h2>
            <hr style="border:1px solid #0078D7;">
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def styled_card(titulo, categoria, status, prazo, autor, data_criacao, cor):
        st.markdown(
            f"""
            <div style="
                background-color:{cor};
                padding:15px;
                border-radius:10px;
                margin-bottom:10px;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
            ">
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
