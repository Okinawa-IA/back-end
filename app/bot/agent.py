from app.bot.heuristic import choose_heuristic_move


def choose_move(game_state: dict) -> str:
    """
    Função principal do bot.

    Por enquanto usamos heurística simples.
    Depois vamos encaixar Q-Learning aqui.
    """

    try:
        return choose_heuristic_move(game_state)
    except Exception as error:
        print(f"Erro ao escolher movimento: {error}")

        # fallback seguro
        return "UP"