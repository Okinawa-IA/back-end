import random
import json
from app.bot.heuristic import get_posicionamento_aleatorio, get_acao_aleatoria_turno
from app.bot.q_learning import escolher_acao_qlearning, load_q_table
from app.bot.state_parser import get_professores_do_time

# =================================================================
# CARREGAMENTO GLOBAL: O cérebro sobe para a RAM apenas UMA VEZ
# =================================================================
print("🧠 Carregando a Tabela Q para a Memória...")
tabela_q = load_q_table()
print("✅ Cérebro carregado com sucesso!")

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
        print(f"Erro crítico no processamento: {error}")
        return {"row": 0, "col": 0} 

def handle_setup_phase(payload: dict) -> dict:
    posicao = get_posicionamento_aleatorio(payload)
    print(f"\n [SETUP] Posicionando em: {posicao}")
    return posicao

def handle_turn_phase(payload: dict) -> dict:
    tabuleiro = payload.get("board", [])
    nossos_professores = get_professores_do_time(payload)
    
    if not nossos_professores:
        return get_acao_aleatoria_turno(payload) 
        
    prof_escolhido_nome = random.choice(list(nossos_professores.keys()))
    pos_prof = nossos_professores[prof_escolhido_nome]

    try:
        # Usa o tabela_q global em vez de ler do HD de novo
        acao_q = escolher_acao_qlearning(
            tabuleiro, 
            prof_escolhido_nome, 
            pos_prof["row"], 
            pos_prof["col"],
            tabela_q,
            epsilon=0.0
        )
        if acao_q:
            # REMOVEMOS O save_q_table() AQUI!
            print(f"\n [BOT - TURNO] {json.dumps(acao_q)}")
            return acao_q
    except Exception as e:
        print(f"Erro no Q-Learning: {e}.")
        
    return get_acao_aleatoria_turno(payload)