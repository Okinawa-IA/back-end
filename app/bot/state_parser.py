def get_espacos_vazios(tabuleiro: list) -> list:
    espacos_vazios = []
    
    if not tabuleiro:
        return espacos_vazios

    for r in range(5):
        for c in range(5):
            celula = tabuleiro[r][c]
            if celula.get("professor") is None:
                espacos_vazios.append({"row": r, "col": c})
                
    return espacos_vazios

def get_professores_do_time(payload: dict) -> dict:
    meu_time = payload.get("your_team")
    
    if meu_time == 1:
        nossos_nomes = ["CLARO", "REY"]
    elif meu_time == 2:
        nossos_nomes = ["KARIN", "BEATRIZ"]
    else:
        nossos_nomes = [] # Fallback de erro

    tabuleiro = payload.get("board", [])
    professores_encontrados = {}

    for r in range(5):
        for c in range(5):
            celula = tabuleiro[r][c]
            nome_professor = celula.get("professor")
            
            if nome_professor in nossos_nomes:
                professores_encontrados[nome_professor] = {"row": r, "col": c}
                
    return professores_encontrados