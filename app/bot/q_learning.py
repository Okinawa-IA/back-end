import json
import os
import random
from app.bot.state_parser import get_estado_local, get_acoes_validas

Q_TABLE_PATH = os.path.join(os.path.dirname(__file__), "..", "storage", "q_table.json")
EPSILON = 0.2  #chance de testar movs novos

def load_q_table() -> dict:
    if not os.path.exists(Q_TABLE_PATH):
        return {}
    try:
        with open(Q_TABLE_PATH, "r") as file:
            return json.load(file)
    except:
        return {}

def save_q_table(q_table: dict): #cria o dir se nao existe
    os.makedirs(os.path.dirname(Q_TABLE_PATH), exist_ok=True)
    with open(Q_TABLE_PATH, "w") as file:
        json.dump(q_table, file, indent=4)

def escolher_acao_qlearning(tabuleiro: list, professor_nome: str, pos_linha: int, pos_col: int) -> dict:
    q_table = load_q_table()
    
    #pega estado local (3x3 em volta) e movs possiveis
    estado_atual = get_estado_local(tabuleiro, pos_linha, pos_col)
    acoes_validas = get_acoes_validas(tabuleiro, pos_linha, pos_col)
    
    if not acoes_validas:
        return None 
        
    if estado_atual not in q_table:
        q_table[estado_atual] = {}
        
    # sorteio de aleatorio x melhor nota
    if random.uniform(0, 1) < EPSILON:
        acao_escolhida = random.choice(acoes_validas)
    else:
        melhor_nota = float('-inf')
        acao_escolhida = acoes_validas[0]
        
        # avalia melhor opcao
        for acao in acoes_validas:
            # transformacao de texto
            acao_str = f"M{acao['move_to']['row']},{acao['move_to']['col']}_B{acao['mentor_at']['row']},{acao['mentor_at']['col']}"
            
            # sem movimento nesse estado = nota 0
            nota = q_table[estado_atual].get(acao_str, 0.0)
            
            if nota > melhor_nota:
                melhor_nota = nota
                acao_escolhida = acao
                
    return {
        "professor": professor_nome,
        "move_to": acao_escolhida["move_to"],
        "mentor_at": acao_escolhida["mentor_at"]
    }