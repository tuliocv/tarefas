import streamlit as st

class InterfaceUI:
    @staticmethod
    def page_header(text: str):
        st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, #1f7a8c 0%, #20BF55 100%);
            padding: 18px 24px;
            border-radius: 12px;
            color: white;
            font-size: 26px;
            font-weight: 700;
            text-align: center;
            margin-bottom: 14px;">
            {text}
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def section_title(text: str):
        st.markdown(f"""
        <h3 style="margin-top:8px; margin-bottom:4px;">{text}</h3>
        <hr style="margin-top:4px; margin-bottom:16px; opacity:0.15;">
        """, unsafe_allow_html=True)

    @staticmethod
    def styled_card(titulo, categoria, status, prazo, autor, data_criacao, cor="#EAF2F8", highlight=False):
        shadow = "0 6px 20px rgba(0,0,0,0.12)" if highlight else "0 2px 10px rgba(0,0,0,0.08)"
        border = "2px solid #ff6b6b" if highlight else "1px solid rgba(0,0,0,0.06)"
        st.markdown(f"""
        <div style="
            background-color:{cor}; padding:16px; border-radius:12px; margin-bottom:12px;
            border:{border}; box-shadow:{shadow}">
            <div style="font-size:18px; font-weight:700; margin-bottom:6px;">{titulo}</div>
            <div><b>Categoria:</b> {categoria} &nbsp;•&nbsp; <b>Status:</b> {status} &nbsp;•&nbsp; <b>Prazo:</b> {prazo}</div>
            <div style="color:#333; font-size:12.5px; margin-top:6px;">
                <b>Autor:</b> {autor} &nbsp;•&nbsp; <i>Criado em {data_criacao}</i>
            </div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def small_task_card(titulo: str, extra: str, highlight=False):
        border = "2px solid #ff6b6b" if highlight else "1px solid rgba(0,0,0,0.08)"
        st.markdown(f"""
        <div style="
            background:#fff; padding:12px; border-radius:10px; margin-bottom:10px;
            border:{border}; box-shadow:0 2px 10px rgba(0,0,0,0.06)">
            <div style="font-size:15px; font-weight:700;">{titulo}</div>
            <div style="font-size:12.5px; color:#444;">{extra}</div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def pill_title(text: str):
        st.markdown(f"""
        <div style="
            display:inline-block;
            background: linear-gradient(90deg, #0ea5e9 0%, #22c55e 100%);
            color:white; padding:8px 14px; border-radius:999px; font-weight:700; margin-bottom:10px;">
            {text}
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def empty_card(text: str):
        st.markdown(f"""
        <div style="
            background:#f7f7f9; padding:14px; border-radius:10px; color:#666;
            text-align:center; border:1px dashed #ddd;">
            {text}
        </div>
        """, unsafe_allow_html=True)
