# models/tarefa.py
from datetime import datetime
import uuid

class Tarefa:
    def __init__(self, titulo: str, categoria: str, prazo_str: str):
        self.id = str(uuid.uuid4())[:8]
        self.data_criacao = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.titulo = titulo
        self.categoria = categoria
        self.prazo = prazo_str
        self.status = "Pendente"

    def to_list(self):
        # id | data_criacao | titulo | categoria | prazo | status
        return [self.id, self.data_criacao, self.titulo, self.categoria, self.prazo, self.status]
