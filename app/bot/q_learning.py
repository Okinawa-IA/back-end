import json
import os
import random
import copy
from app.bot.state_parser import get_estado_local, get_acoes_validas

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q_TABLE_PATH = os.path.join(BASE_DIR, "storage", "q_table.json")

ALPHA = 0.5   
GAMMA = 0.9   

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

def calcular_recompensa(tabuleiro: list, pos_atual: dict, acao: dict) -> float:
    recompensa = 0.0
    nivel_atual = tabuleiro[pos_atual["row"]][pos_atual["col"]].get("level", 0)
    nivel_destino = tabuleiro[acao["move_to"]["row"]][acao["move_to"]["col"]].get("level", 0)
    
    if nivel_destino > nivel_atual: # subir de nivel
        recompensa += 10.0
        
    if nivel_destino == 3: #ganhar o jogo
        recompensa += 1000.0
        
    if nivel_destino < nivel_atual: # descer de nivel
        recompensa -= 5.0
        
    nivel_construcao = tabuleiro[acao["mentor_at"]["row"]][acao["mentor_at"]["col"]].get("level", 0)
    if nivel_construcao < 4: #incentivo para mentorar para cima
        recompensa += 1.0

    return recompensa


def escolher_acao_qlearning(tabuleiro: list, professor_nome: str, pos_linha: int, pos_col: int, q_table: dict, epsilon: float = 0.0) -> dict:
    #pega estado local (3x3 em volta) e movs possiveis
    estado_atual = get_estado_local(tabuleiro, pos_linha, pos_col)
    acoes_validas = get_acoes_validas(tabuleiro, pos_linha, pos_col)
    
    if not acoes_validas:
        return None 
        
    if estado_atual not in q_table:
        q_table[estado_atual] = {}
        
    # escolha da açao
    if random.uniform(0, 1) < epsilon:
        acao_escolhida = random.choice(acoes_validas)
    else:
        melhor_nota = float('-inf')
        acao_escolhida = acoes_validas[0]
        
        # avalia melhor opcao
        for acao in acoes_validas:
            # transformacao de texto
            acao_str = f"M{acao['move_to']['row']},{acao['move_to']['col']}_B{acao['mentor_at']['row']},{acao['mentor_at']['col']}"

            nota = q_table[estado_atual].get(acao_str, 0.0)  # sem movimento nesse estado = nota 0
            if nota > melhor_nota:
                melhor_nota = nota
                acao_escolhida = acao
                
    
    acao_str = f"M{acao_escolhida['move_to']['row']},{acao_escolhida['move_to']['col']}_B{acao_escolhida['mentor_at']['row']},{acao_escolhida['mentor_at']['col']}"
    q_atual = q_table[estado_atual].get(acao_str, 0.0) # nota antiga
    recompensa = calcular_recompensa(tabuleiro, {"row": pos_linha, "col": pos_col}, acao_escolhida)
    
    #previsao do estado futuro - essa parte de tab_futuro foi feita com ajuda de IA
    #antes simplificavamos a eq. de bellman usando recompensa imediata (greedy)
    tab_futuro = copy.deepcopy(tabuleiro)
    tab_futuro[pos_linha][pos_col]["professor"] = None #posicao antiga 
    tab_futuro[acao_escolhida["move_to"]["row"]][acao_escolhida["move_to"]["col"]]["professor"] = professor_nome # posicao nova
    tab_futuro[acao_escolhida["mentor_at"]["row"]][acao_escolhida["mentor_at"]["col"]]["level"] += 1 # aluno mentorado
    
    # estado local e opcoes futuras
    estado_futuro = get_estado_local(tab_futuro, acao_escolhida["move_to"]["row"], acao_escolhida["move_to"]["col"])
    acoes_futuras = get_acoes_validas(tab_futuro, acao_escolhida["move_to"]["row"], acao_escolhida["move_to"]["col"])
    
    # nota max futuro
    max_q_futuro = 0.0
    if acoes_futuras:
        if estado_futuro in q_table:
            notas_futuras = q_table[estado_futuro].values()
            if notas_futuras:
                max_q_futuro = max(notas_futuras)
                
    q_novo = q_atual + ALPHA * (recompensa + (GAMMA * max_q_futuro) - q_atual) #eq de bellman
    
    q_table[estado_atual][acao_str] = q_novo

    return {
        "professor": professor_nome,
        "move_to": acao_escolhida["move_to"],
        "mentor_at": acao_escolhida["mentor_at"]
    }