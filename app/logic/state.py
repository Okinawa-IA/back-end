from typing import List, Tuple, Dict
from app.schemas import Cell, Position, TeamID

class BoardState:
    BOARD_SIZE = 5

    @staticmethod
    def adjacent_cells(row: int, col: int) -> List[Tuple[int, int]]:
        #retorna todas as casas vizinhas dentro dos limites do tabuleiro
        cells = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < BoardState.BOARD_SIZE and 0 <= nc < BoardState.BOARD_SIZE:
                    cells.append((nr, nc))
        return cells

    @staticmethod
    def get_empty_spaces(board: List[List[Cell]]) -> List[Position]:
        #retorna todas as posições de nível 0 e sem professor
        empty_spaces = []
        for r in range(BoardState.BOARD_SIZE):
            for c in range(BoardState.BOARD_SIZE):
                if board[r][c].level == 0 and board[r][c].professor is None:
                    empty_spaces.append(Position(row=r, col=c))
        return empty_spaces

    @staticmethod
    def get_team_professors(board: List[List[Cell]], team: TeamID) -> Dict[str, Position]:
        #retorna um dicionário com os professores vivos do time e suas posições
        allies = ["CLARO", "REY"] if team == TeamID.TURING else ["KARIN", "BEATRIZ"]
        found = {}
        for r in range(BoardState.BOARD_SIZE):
            for c in range(BoardState.BOARD_SIZE):
                prof_name = board[r][c].professor
                if prof_name in allies:
                    found[prof_name] = Position(row=r, col=c)
        return found

    @staticmethod
    def get_local_state(board: List[List[Cell]], pos_row: int, pos_col: int) -> str:
        #gera a string de visão 3x3 local 
        visao = []
        for r in range(pos_row - 1, pos_row + 2):
            for c in range(pos_col - 1, pos_col + 2):
                if r == pos_row and c == pos_col:
                    visao.append("X")
                elif 0 <= r < BoardState.BOARD_SIZE and 0 <= c < BoardState.BOARD_SIZE:
                    cell = board[r][c]
                    if cell.professor is not None:
                        visao.append("P")
                    else:
                        visao.append(str(cell.level))
                else:
                    visao.append("-1")
        return ",".join(visao)

    @staticmethod
    def get_valid_moves(board: List[List[Cell]], current_pos: Position, team: TeamID) -> List[Dict]:
        # retorna as ações válidas mapeadas.
        valid_actions = []
        current_level = board[current_pos.row][current_pos.col].level
        allies = ["CLARO", "REY"] if team == TeamID.TURING else ["KARIN", "BEATRIZ"]

        for dst_row, dst_col in BoardState.adjacent_cells(current_pos.row, current_pos.col):
            dst_cell = board[dst_row][dst_col]
            
            #valida movimento (vazio, não Graduada, sobe no máx 1)
            if dst_cell.professor is None and dst_cell.level <= current_level + 1 and dst_cell.level < 4:
                
                # valida Mentoria a partir do destino
                for men_row, men_col in BoardState.adjacent_cells(dst_row, dst_col):
                    men_cell = board[men_row][men_col]
                    is_source = (men_row == current_pos.row and men_col == current_pos.col)
                    
                    if (men_cell.professor is None or is_source) and men_cell.level < 4:
                        
                        # filtro Suicida
                        suicidal_move = False
                        if men_cell.level == 2:
                            for vr, vc in BoardState.adjacent_cells(men_row, men_col):
                                neighbor_cell = board[vr][vc]
                                neighbor_prof = neighbor_cell.professor
                                
                                if neighbor_prof is not None and neighbor_prof not in allies:
                                    # Impede que o próprio movimento seja considerado como adjacência segura
                                    if (vr != current_pos.row or vc != current_pos.col):
                                        if neighbor_cell.level >= 2:
                                            suicidal_move = True
                                            break
                        
                        if not suicidal_move:
                            valid_actions.append({
                                "move_to": Position(row=dst_row, col=dst_col),
                                "mentor_at": Position(row=men_row, col=men_col)
                            })
                            
        return valid_actions