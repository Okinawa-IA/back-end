import random


VALID_MOVES = ["UP", "DOWN", "LEFT", "RIGHT"]


def choose_random_move() -> str:
    return random.choice(VALID_MOVES)


def choose_heuristic_move(game_state: dict) -> str:
    """
    Heurística inicial.

    Por enquanto, como ainda não sabemos o formato real do payload enviado
    pela API do professor, usamos um movimento aleatório válido.

    Depois vamos evoluir essa função para:
    1. encontrar a posição do nosso jogador;
    2. encontrar professores no tabuleiro;
    3. calcular distância de Manhattan;
    4. andar em direção ao professor mais próximo.
    """

    return choose_random_move()