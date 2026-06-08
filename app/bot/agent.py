import random
import json
from app.bot.heuristic import get_posicionamento_aleatorio, get_acao_aleatoria_turno
from app.bot.q_learning import escolher_acao_qlearning
from app.bot.state_parser import get_professores_do_time
from app.bot.q_learning import load_q_table, save_q_table
from app.bot.state_parser import get_acoes_validas

tabela_q = load_q_table()

def process_request(payload: dict) -> dict:
    try:
        turn_phase = payload.get("turn_phase")
        if turn_phase == "setup_placement":
            return handle_setup_phase(payload)
        elif turn_phase == "player_turn":
            return handle_turn_phase(payload)
        else:
            return {}
    except Exception as error:
        print(f"Erro critico no processamento: {error}")
        return {"row": 0, "col": 0} 

def handle_setup_phase(payload: dict) -> dict:
    posicao = get_posicionamento_aleatorio(payload)
    print(f"\n Jogando em: {posicao}")
    return posicao

def buscar_jogada_critica(tabuleiro: list, nossos_professores: dict) -> dict:
    #busca vitoria imediata ou bloqueio contra vitoria inimiga, caso nao achar retorna none
    
    jogada_defensiva = None

    for prof_nome, pos_atual in nossos_professores.items():
        acoes = get_acoes_validas(tabuleiro, pos_atual["row"], pos_atual["col"])
        
        for acao in acoes:
            linha_destino = acao["move_to"]["row"]
            col_destino = acao["move_to"]["col"]
            linha_mentoria = acao["mentor_at"]["row"]
            col_mentoria = acao["mentor_at"]["col"]

            if tabuleiro[linha_destino][col_destino].get("level", 0) == 3: # ganhar
                return {
                    "professor": prof_nome,
                    "move_to": acao["move_to"],
                    "mentor_at": acao["mentor_at"]
                }

            
            if tabuleiro[linha_mentoria][col_mentoria].get("level", 0) == 3: #bloquear vitoria do oponente
                jogada_defensiva = {
                    "professor": prof_nome,
                    "move_to": acao["move_to"],
                    "mentor_at": acao["mentor_at"]
                }

    return jogada_defensiva

def handle_turn_phase(payload: dict) -> dict:
    tabuleiro = payload.get("board", [])
    nossos_professores = get_professores_do_time(payload)
    
    if not nossos_professores:
        return get_acao_aleatoria_turno(payload) 
    
    jogada_critica = buscar_jogada_critica(tabuleiro, nossos_professores)
    if jogada_critica:
        print(f"\nJogada critica encontrada: {json.dumps(jogada_critica)}")
        return jogada_critica

    #nao achou jogada critica - vai pro qlearning
    prof_escolhido_nome = random.choice(list(nossos_professores.keys()))
    pos_prof = nossos_professores[prof_escolhido_nome]

    try:
        acao_q = escolher_acao_qlearning(
            tabuleiro, 
            prof_escolhido_nome, 
            pos_prof["row"], 
            pos_prof["col"],
            tabela_q,
            epsilon=0.0
        )
        if acao_q:
            print(f"\n Ação Q-Learning: {json.dumps(acao_q)}")
            return acao_q
    except Exception as e:
        print(f"Erro no Q-Learning: {e}.")
        
    # caso de none ou erro usa random
    return get_acao_aleatoria_turno(payload)


