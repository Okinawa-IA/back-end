from app.bot.heuristic import choose_heuristic_move, choose_random_move


def choose_move(game_state: dict) -> str:
    """
    Função principal do bot.

    Fluxo:
    1. tenta escolher movimento por heurística;
    2. se falhar, usa fallback aleatório;
    3. se tudo falhar, retorna UP.
    """

    try:
        return choose_heuristic_move(game_state)
    except Exception as error:
        print(f"[AGENT ERROR] Erro ao escolher movimento por heurística: {error}")

    try:
        return choose_random_move()
    except Exception as error:
        print(f"[AGENT ERROR] Erro no fallback aleatório: {error}")

    return "UP"