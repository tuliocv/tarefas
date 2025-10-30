from textblob import TextBlob
import pandas as pd
import streamlit as st
from datetime import date

class AIInsights:
    def __init__(self, df):
        self.df = df.copy()

    def sentimento_historico(self):
        if "historico" not in self.df.columns or self.df["historico"].isna().all():
            st.info("Nenhum histórico disponível para análise.")
            return
        self.df["sentimento"] = self.df["historico"].astype(str).apply(lambda x: TextBlob(x).sentiment.polarity)
        media = self.df["sentimento"].mean()
        status = "😊 Positivo" if media > 0.2 else "😐 Neutro" if media > -0.2 else "😞 Negativo"
        st.metric("Humor geral das tarefas", status, f"{media:.2f}")

    def risco_atraso(self):
        """Heurística simples de risco (0–100%): mais alto se próximo do prazo/atrasado e não concluída."""
        if self.df.empty:
            st.info("Sem dados suficientes para prever risco de atraso.")
            return

        df = self.df.copy()
        df["prazo_dt"] = pd.to_datetime(df.get("prazo", ""), errors="coerce", dayfirst=True)
        df["status"] = df.get("status", "").fillna("Pendente")
        hoje = pd.to_datetime(date.today())

        def score(row):
            if row["status"] == "Concluída" or pd.isna(row["prazo_dt"]):
                return 0
            dias = (row["prazo_dt"] - hoje).days
            base = 50
            if dias < 0:        # já atrasada
                base = 90
            elif dias <= 2:     # prazo muito próximo
                base = 75
            elif dias <= 7:     # prazo na semana
                base = 60
            # penalidade leve por status parado
            if row["status"] == "Pendente":
                base += 10
            return max(0, min(100, base))

        df["risco"] = df.apply(score, axis=1)
        risco_medio = df["risco"].mean() if len(df) else 0
        st.metric("📉 Risco médio de atraso", f"{risco_medio:.0f}%")
        atrasos = df.sort_values("risco", ascending=False).head(5)[["titulo", "prazo", "status", "risco"]]
        if not atrasos.empty:
            st.markdown("**Tarefas com maior risco:**")
            st.dataframe(atrasos, use_container_width=True)
