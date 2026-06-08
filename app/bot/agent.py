import random
import json
from app.bot.heuristic import get_posicionamento_aleatorio, get_acao_aleatoria_turno
from app.bot.q_learning import escolher_acao_qlearning
from app.bot.state_parser import get_professores_do_time
from app.bot.q_learning import load_q_table, save_q_table
from app.bot.state_parser import get_acoes_validas, get_estado_local

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

def get_jogada_critica(tabuleiro: list, nossos_professores: dict) -> dict:
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

def get_professor_defensivo(tabuleiro: list, nossos_professores: dict) -> str:
    #pega o professor mais proximo de um inimigo em nivel 2 ou mais
    inimigos = []
    for r in range(5):
        for c in range(5):
            prof = tabuleiro[r][c].get("professor")
            if prof and prof not in nossos_professores:
                inimigos.append({"nome": prof, "row": r, "col": c, "level": tabuleiro[r][c].get("level", 0)})

    inimigos_perigosos = [i for i in inimigos if i["level"] >= 2]
    if not inimigos_perigosos:
        return None

    # pega o inimigo mais perto de ganhar
    alvo = None
    nivel_maximo = -1
    for i in inimigos_perigosos:
        if i["level"] > nivel_maximo:
            nivel_maximo = i["level"]
            alvo = i
    if not alvo:
        return None
    
    melhor_prof = None
    menor_distancia = 999

    for prof_nome, pos in nossos_professores.items():
        dist = max(abs(pos["row"] - alvo["row"]), abs(pos["col"] - alvo["col"]))
        if dist < menor_distancia:
            menor_distancia = dist
            melhor_prof = prof_nome

    return melhor_prof

def handle_turn_phase(payload: dict) -> dict:
    tabuleiro = payload.get("board", [])
    nossos_professores = get_professores_do_time(payload)
    
    if not nossos_professores:
        return get_acao_aleatoria_turno(payload) 
    
    jogada_critica = get_jogada_critica(tabuleiro, nossos_professores)
    if jogada_critica:
        print(f"\nJogada critica encontrada: {json.dumps(jogada_critica)}")
        return jogada_critica

    prof_defesa = get_professor_defensivo(tabuleiro, nossos_professores)

    professores_para_avaliar = [prof_defesa] if prof_defesa else list(nossos_professores.keys())

    melhor_acao = None
    melhor_nota = float('-inf')

    for prof_nome in professores_para_avaliar:
        pos_prof = nossos_professores[prof_nome]
        try:
            acao_q = escolher_acao_qlearning(
                tabuleiro, 
                prof_nome, 
                pos_prof["row"], 
                pos_prof["col"],
                tabela_q,
                epsilon=0.0
            )
            if acao_q:
                estado = get_estado_local(tabuleiro, pos_prof["row"], pos_prof["col"])
                acao_str = f"M{acao_q['move_to']['row']},{acao_q['move_to']['col']}_B{acao_q['mentor_at']['row']},{acao_q['mentor_at']['col']}"
                
                # resgata a nota da tabela q
                nota = tabela_q.get(estado, {}).get(acao_str, 0.0)

                if nota > melhor_nota or melhor_acao is None:
                    melhor_nota = nota
                    melhor_acao = acao_q

        except Exception as e:
            print(f"Erro no Q-Learning para {prof_nome}: {e}.")
    if melhor_acao:
        if prof_defesa:
            print(f"\n Foco no {prof_defesa} para bloquear inimigos")
        print(f"\nAção Q-Learning: {json.dumps(melhor_acao)} | Nota: {melhor_nota}")
        return melhor_acao
        
    # caso de none ou erro usa random
    return get_acao_aleatoria_turno(payload)


