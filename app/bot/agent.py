from app.bot.heuristic import get_posicionamento_aleatorio, get_acao_aleatoria_turno

def process_request(payload: dict) -> dict:
    """
    Função principal que roteia a requisição dependendo da fase do jogo.
    """
    try:
        turn_phase = payload.get("turn_phase")
        
        if turn_phase == "setup_placement":
            return handle_setup_phase(payload)
            
        elif turn_phase == "player_turn":
            return handle_turn_phase(payload)
            
        else:
            print(f"Fase desconhecida: {turn_phase}")
            return {}

    except Exception as error:
        print(f"Erro crítico no processamento: {error}")
        # Se tudo explodir, tenta mandar a posição 0,0 para não dar timeout
        return {"row": 0, "col": 0} 

def handle_setup_phase(payload: dict) -> dict:
    """
    Lida com o turno 0 (Colocar professores no tabuleiro).
    """
    return get_posicionamento_aleatorio(payload)

def handle_turn_phase(payload: dict) -> dict:
    """
    Lida com os turnos normais (Mover e Construir).
    """
    
    return get_acao_aleatoria_turno(payload)