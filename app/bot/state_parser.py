from typing import Any, Dict, List, Optional, Tuple


Position = Tuple[int, int]


def get_board(game_state: Dict[str, Any]) -> List[List[Dict[str, Any]]]:
    """
    Tenta extrair o tabuleiro do payload.

    Aceita formatos comuns:
    - payload["board"]
    - payload["game"]["board"]
    - payload["state"]["board"]
    """

    if "board" in game_state:
        return game_state.get("board") or []

    if "game" in game_state and isinstance(game_state["game"], dict):
        return game_state["game"].get("board") or []

    if "state" in game_state and isinstance(game_state["state"], dict):
        return game_state["state"].get("board") or []

    return []


def find_professors(board: List[List[Dict[str, Any]]]) -> List[Position]:
    professors = []

    for row_index, row in enumerate(board):
        for column_index, cell in enumerate(row):
            if cell.get("professor"):
                professors.append((row_index, column_index))

    return professors


def manhattan_distance(origin: Position, target: Position) -> int:
    return abs(origin[0] - target[0]) + abs(origin[1] - target[1])


def find_nearest_position(origin: Position, targets: List[Position]) -> Optional[Position]:
    if not targets:
        return None

    return min(targets, key=lambda target: manhattan_distance(origin, target))