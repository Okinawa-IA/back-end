import random
from app.bot.state_parser import get_espacos_vazios, get_professores_do_time

def get_posicionamento_aleatorio(payload: dict) -> dict:
    
    board = payload.get("board", [])
    espacos_vazios = get_espacos_vazios(board)
    
    if espacos_vazios:
        return random.choice(espacos_vazios)
    
    # se nao achar espaço
    return {"row": 0, "col": 0}

def get_acao_aleatoria_turno(payload: dict) -> dict: #usado em casos de erro para nao quebrar o backend
   
    nossos_professores = get_professores_do_time(payload)
    
    if not nossos_professores:
        return {}

    professor_escolhido = random.choice(list(nossos_professores.keys()))
    
    return {
        "professor": professor_escolhido, 
        "move_to": {
            "row": random.randint(0, 4),
            "col": random.randint(0, 4)
        },
        "mentor_at": {
            "row": random.randint(0, 4),
            "col": random.randint(0, 4)
        }
    }