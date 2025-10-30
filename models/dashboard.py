import streamlit as st
import plotly.express as px
import pandas as pd

class Dashboard:
    def __init__(self, df):
        self.df = df.copy()
        self.preprocess()

    def preprocess(self):
        for col in ["data_criacao", "prazo", "ultima_atualizacao"]:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors="coerce", dayfirst=True)
        self.df["status"] = self.df["status"].fillna("Pendente")

    def kpi_cards(self):
        total = len(self.df)
        concluidas = (self.df["status"] == "Concluída").sum()
        andamento = (self.df["status"] == "Em andamento").sum()
        pendentes = (self.df["status"] == "Pendente").sum()

        c1, c2, c3 = st.columns(3)
        c1.metric("✅ Concluídas", concluidas, f"{(concluidas/total*100):.1f}%" if total else "0%")
        c2.metric("⏳ Em andamento", andamento)
        c3.metric("🕒 Pendentes", pendentes)

    def tempo_medio_conclusao(self):
        df = self.df.copy()
        df = df[(df["status"] == "Concluída") & df["data_criacao"].notna() & df["ultima_atualizacao"].notna()]
        if df.empty:
            st.info("Nenhuma tarefa concluída ainda para calcular tempo médio.")
            return
        df["duracao_dias"] = (df["ultima_atualizacao"] - df["data_criacao"]).dt.days
        media = df["duracao_dias"].mean()
        st.metric("⏱️ Tempo médio de conclusão", f"{media:.1f} dias")

    def grafico_evolucao(self):
        df = self.df.copy()
        if df["data_criacao"].isna().all():
            st.warning("Sem dados de data para gerar gráfico temporal.")
            return
        df["mês"] = df["data_criacao"].dt.to_period("M").astype(str)
        evolucao = df.groupby("mês")["id"].count().reset_index(name="tarefas")
        fig = px.line(evolucao, x="mês", y="tarefas", title="📈 Tarefas criadas por mês", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    def grafico_categoria(self):
        if "categoria" in self.df.columns:
            categoria_counts = self.df["categoria"].value_counts().reset_index()
            categoria_counts.columns = ["Categoria", "Quantidade"]
            fig = px.bar(categoria_counts, x="Categoria", y="Quantidade", title="📊 Distribuição por Categoria", color="Categoria")
            st.plotly_chart(fig, use_container_width=True)

    def grafico_status(self):
        if "status" in self.df.columns:
            status_counts = self.df["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Quantidade"]
            fig = px.pie(status_counts, names="Status", values="Quantidade", title="📍 Distribuição por Status", color="Status")
            st.plotly_chart(fig, use_container_width=True)
