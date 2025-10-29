import streamlit as st
import pandas as pd
import plotly.express as px

class Dashboard:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def kpi_cards(self):
        total = len(self.df)
        concluidas = len(self.df[self.df["status"] == "Concluída"])
        andamento = len(self.df[self.df["status"] == "Em andamento"])
        pendentes = len(self.df[self.df["status"] == "Pendente"])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total", total)
        col2.metric("✅ Concluídas", concluidas)
        col3.metric("⚙️ Em andamento", andamento)
        col4.metric("🕒 Pendentes", pendentes)

    def grafico_status(self):
        fig = px.pie(
            self.df,
            names="status",
            title="Distribuição de Tarefas por Status",
            color="status",
            color_discrete_map={
                "Concluída": "#90EE90",
                "Em andamento": "#FFD700",
                "Pendente": "#F08080",
            }
        )
        st.plotly_chart(fig, use_container_width=True)

    def grafico_categoria(self):
        fig = px.bar(
            self.df,
            x="categoria",
            color="status",
            title="Tarefas por Categoria",
            barmode="group",
            color_discrete_map={
                "Concluída": "#90EE90",
                "Em andamento": "#FFD700",
                "Pendente": "#F08080",
            }
        )
        st.plotly_chart(fig, use_container_width=True)
