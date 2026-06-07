import random
from app.bot.state_parser import get_espacos_vazios

def get_posicionamento_aleatorio(payload: dict) -> dict:
    
    board = payload.get("board", [])
    espacos_vazios = get_espacos_vazios(board)
    
    if espacos_vazios:
        return random.choice(espacos_vazios)
    
    # Fallback extremo se não achar espaço
    return {"row": 0, "col": 0}

def get_acao_aleatoria_turno(payload: dict) -> dict:
    
    return {
            "professor": "CLARO",
            "move": {
                "row": 1,
                "col": 0
            },
            "build": {
                "row": 1,
                "col": 1
            }
        }