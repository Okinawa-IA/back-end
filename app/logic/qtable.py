import os
import pickle
import random
import copy
from typing import Optional
from app.schemas import Position, Cell
from app.logic.state import BoardState

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
Q_TABLE_PATH = os.path.join(BASE_DIR, "storage", "q_table.pickle")

class QLearningManager:
    def __init__(self):
        self.q_table = self.load_q_table()
        self.alpha = 0.5   
        self.gamma = 0.9   

    def load_q_table(self) -> dict:
        if not os.path.exists(Q_TABLE_PATH):
            return {}
        try:
            with open(Q_TABLE_PATH, "rb") as file:
                return pickle.load(file)
        except Exception as e:
            print(f"Erro ao carregar Pickle: {e}")
            return {}

    def save_q_table(self):
        os.makedirs(os.path.dirname(Q_TABLE_PATH), exist_ok=True)
        with open(Q_TABLE_PATH, "wb") as file:
            pickle.dump(self.q_table, file)

    def calculate_reward(self, board: list[list[Cell]], current_pos: Position, action: dict) -> float:
        recompensa = 0.0
        nivel_atual = board[current_pos.row][current_pos.col].level
        
        move_to = action["move_to"]
        mentor_at = action["mentor_at"]
        nivel_destino = board[move_to.row][move_to.col].level
        
        if nivel_destino > nivel_atual: 
            recompensa += 10.0
        if nivel_destino == 3: 
            recompensa += 1000.0
        if nivel_destino < nivel_atual: 
            recompensa -= 5.0
            
        nivel_construcao = board[mentor_at.row][mentor_at.col].level
        if nivel_construcao < 4: 
            recompensa += 1.0

        return recompensa

    def choose_action(self, board: list[list[Cell]], prof_name: str, pos: Position, epsilon: float = 0.0) -> Optional[dict]:
        estado_atual = BoardState.get_local_state(board, pos.row, pos.col)
        # O time passado aqui só importa para o filtro suicida saber quem é aliado
        team = 1 if prof_name in ["CLARO", "REY"] else 2 
        acoes_validas = BoardState.get_valid_moves(board, pos, team)
        
        if not acoes_validas:
            return None 
            
        if estado_atual not in self.q_table:
            self.q_table[estado_atual] = {}
            
        if random.uniform(0, 1) < epsilon:
            acao_escolhida = random.choice(acoes_validas)
        else:
            melhor_nota = float('-inf')
            acao_escolhida = acoes_validas[0]
            
            for acao in acoes_validas:
                move = acao["move_to"]
                mentor = acao["mentor_at"]
                acao_str = f"M{move.row},{move.col}_B{mentor.row},{mentor.col}"
                nota = self.q_table[estado_atual].get(acao_str, 0.0)
                
                if nota > melhor_nota:
                    melhor_nota = nota
                    acao_escolhida = acao
                    
        # Simulação de Bellman (Atualização online - mantida do seu código original)
        move = acao_escolhida["move_to"]
        mentor = acao_escolhida["mentor_at"]
        acao_str = f"M{move.row},{move.col}_B{mentor.row},{mentor.col}"
        
        q_atual = self.q_table[estado_atual].get(acao_str, 0.0)
        recompensa = self.calculate_reward(board, pos, acao_escolhida)
        
        # Deepcopy seguro com Pydantic
        tab_futuro = copy.deepcopy(board)
        tab_futuro[pos.row][pos.col].professor = None 
        tab_futuro[move.row][move.col].professor = prof_name 
        tab_futuro[mentor.row][mentor.col].level += 1 
        
        estado_futuro = BoardState.get_local_state(tab_futuro, move.row, move.col)
        acoes_futuras = BoardState.get_valid_moves(tab_futuro, move, team)
        
        max_q_futuro = 0.0
        if acoes_futuras and estado_futuro in self.q_table:
            notas_futuras = self.q_table[estado_futuro].values()
            if notas_futuras:
                max_q_futuro = max(notas_futuras)
                
        q_novo = q_atual + self.alpha * (recompensa + (self.gamma * max_q_futuro) - q_atual)
        self.q_table[estado_atual][acao_str] = q_novo

        return {
            "move_to": move,
            "mentor_at": mentor
        }