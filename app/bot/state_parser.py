def get_espacos_vazios(board: list) -> list:
    """
    Varre a matriz 5x5 do payload e retorna uma lista com as coordenadas 
    [linha, coluna] de todos os quadrados que não têm professor.
    """
    empty_spaces = []
    for r in range(5):
        for c in range(5):
            # Acessa o dicionário da célula e verifica se o professor é null
            cell = board[r][c]
            if cell.get("professor") is None:
                empty_spaces.append({"row": r, "col": c})
                
    return empty_spaces