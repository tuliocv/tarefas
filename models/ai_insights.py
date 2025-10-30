from textblob import TextBlob
import pandas as pd
import streamlit as st

class AIInsights:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def sentimento_historico(self):
        if "historico" not in self.df.columns or self.df["historico"].isna().all():
            st.info("Nenhum histórico disponível para análise.")
            return
        self.df["sentimento"] = self.df["historico"].astype(str).apply(lambda x: TextBlob(x).sentiment.polarity)
        media = self.df["sentimento"].mean()
        status = "😊 Positivo" if media > 0.2 else "😐 Neutro" if media > -0.2 else "😞 Negativo"
        st.metric("Humor geral das tarefas", status, f"{media:.2f}")

    def recomendacoes(self):
        if self.df.empty:
            st.info("Sem dados suficientes para recomendações.")
            return
        pendentes = self.df[self.df["status"] != "Concluída"]
        mais_categoria = pendentes["categoria"].mode()[0] if not pendentes.empty else None
        st.markdown("### 💡 Recomendações automáticas")
        if mais_categoria:
            st.write(f"- Você tem várias tarefas **pendentes** em **{mais_categoria}**. Considere priorizá-las.")
        if len(pendentes) > 5:
            st.write("- Muitas tarefas ainda estão pendentes. Tente concluir ou reagendar algumas.")
        if (self.df["status"] == "Concluída").sum() == 0:
            st.write("- Nenhuma tarefa concluída ainda — defina metas pequenas e diárias para iniciar o fluxo.")
