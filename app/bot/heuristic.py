import random


VALID_MOVES = ["UP", "DOWN", "LEFT", "RIGHT"]


def choose_heuristic_move(game_state: dict) -> str:
    """
    Primeira versão do bot.

    Como ainda não sabemos exatamente o formato do payload enviado
    pela API do professor, começamos retornando um movimento válido
    aleatório.

    Depois vamos ler board, player position, professores etc.
    """

    return random.choice(VALID_MOVES)