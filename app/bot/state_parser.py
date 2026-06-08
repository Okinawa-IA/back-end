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
        nossos_nomes = [] #erro

    tabuleiro = payload.get("board", [])
    professores_encontrados = {}

    for r in range(5):
        for c in range(5):
            celula = tabuleiro[r][c]
            nome_professor = celula.get("professor")
            
            if nome_professor in nossos_nomes:
                professores_encontrados[nome_professor] = {"row": r, "col": c}
                
    return professores_encontrados


def get_estado_local(tabuleiro: list, pos_linha: int, pos_col: int) -> str: 
    #diminui o tabuleiro em um estado local de tamanho 3x3
    #retorna uma string com as posições
    visao = []
    for r in range(pos_linha - 1, pos_linha + 2):
        for c in range(pos_col - 1, pos_col + 2):
            if r == pos_linha and c == pos_col:
                visao.append("X") # posicao do prof
            elif 0 <= r < 5 and 0 <= c < 5:
                celula = tabuleiro[r][c]
                # celula ocupada
                if celula.get("professor") is not None:
                    visao.append("P")
                else:
                    visao.append(str(celula.get("level", 0)))
            else:
                visao.append("-1") # parede/fora do tabuleiro
                
    return ",".join(visao)

def get_acoes_validas(tabuleiro: list, pos_linha: int, pos_col: int) -> list: #calcula onde o professor pode ir e q aluno pode mentorar
    acoes = []
    movimentos_adjacentes = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]
    
    nivel_atual = tabuleiro[pos_linha][pos_col].get("level", 0)

    for dr, dc in movimentos_adjacentes:
        nova_linha, nova_col = pos_linha + dr, pos_col + dc
        
        if 0 <= nova_linha < 5 and 0 <= nova_col < 5:
            celula_destino = tabuleiro[nova_linha][nova_col]
            nivel_destino = celula_destino.get("level", 0)
            
            #verifica se pode mover (sem pisar em professor e subindo no max 1 nivel)
            if celula_destino.get("professor") is None and nivel_destino <= nivel_atual + 1 and nivel_destino < 4:
                
                #procura pra mentorar
                for br, bc in movimentos_adjacentes:
                    b_linha, b_col = nova_linha + br, nova_col + bc
                    if 0 <= b_linha < 5 and 0 <= b_col < 5:
                        # não pode mentorar onde tem prof
                        if tabuleiro[b_linha][b_col].get("professor") is None or (b_linha == pos_linha and b_col == pos_col):
                            if tabuleiro[b_linha][b_col].get("level", 0) < 4:
                                acoes.append({
                                    "move_to": {"row": nova_linha, "col": nova_col},
                                    "mentor_at": {"row": b_linha, "col": b_col}
                                })
                                
                                break 
    return acoes