import streamlit as st
import pandas as pd

class KanbanBoard:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.df["status"] = self.df["status"].fillna("Pendente")

    def render(self, on_move):
        cols = st.columns(3)
        estados = ["Pendente", "Em andamento", "Concluída"]

        for idx, estado in enumerate(estados):
            with cols[idx]:
                st.markdown(f"### {estado}")
                subset = self.df[self.df["status"] == estado].sort_values("prazo", na_position="last")
                if subset.empty:
                    st.caption("Sem tarefas aqui.")
                for _, row in subset.iterrows():
                    with st.container(border=True):
                        st.write(f"**{row['titulo']}**")
                        st.caption(f"Prazo: {row.get('prazo','-')}  •  Cat.: {row.get('categoria','-')}")
                        nota = st.text_input(
                            "Nota (opcional)",
                            key=f"nota_{row['id']}_{estado}",
                            placeholder="Uma observação rápida para o histórico..."
                        )
                        # botões de mover
                        bcols = st.columns(3)
                        # Pendente: pode mover para Em andamento/Concluída
                        # Em andamento: Pendente/Concluída
                        # Concluída: Pendente/Em andamento
                        alvos = [e for e in estados if e != estado]
                        for bi, alvo in enumerate(alvos):
                            if bcols[bi].button(f"→ {alvo}", key=f"mv_{row['id']}_{alvo}"):
                                on_move(row["id"], alvo, nota)
                                st.rerun()
