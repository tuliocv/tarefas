# models/tarefa.py
from datetime import datetime
import uuid

class Tarefa:
    """Representa uma tarefa individual."""
    def __init__(self, titulo, categoria, prazo):
        self.id = str(uuid.uuid4())[:8]
        self.titulo = titulo
        self.categoria = categoria
        self.prazo = prazo
        self.status = "Pendente"
        self.data_criacao = datetime.now().strftime("%d/%m/%Y")

    def to_list(self):
        """Retorna os dados da tarefa em lista para salvar no Google Sheets."""
        return [self.id, self.titulo, self.categoria, self.prazo, self.status, self.data_criacao]
