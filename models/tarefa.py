from datetime import datetime

class Tarefa:
    def __init__(self, titulo, categoria, prazo, status="Pendente", id=None, historico=None):
        self.id = id or f"T-{int(datetime.now().timestamp())}"
        self.data_criacao = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.titulo = titulo
        self.categoria = categoria
        self.prazo = prazo
        self.status = status
        self.historico = historico or f"{self.data_criacao} - Criada"
        self.ultima_atualizacao = self.data_criacao

    def atualizar_status(self, novo_status):
        """Atualiza o status e registra histórico."""
        self.status = novo_status
        self.ultima_atualizacao = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.historico += f"\n{self.ultima_atualizacao} - Status alterado para {novo_status}"

    def to_list(self):
        """Converte a tarefa para lista (usada no append_row)."""
        return [
            self.id,
            self.data_criacao,
            self.titulo,
            self.categoria,
            self.prazo,
            self.status,
            self.historico,
            self.ultima_atualizacao,
        ]
