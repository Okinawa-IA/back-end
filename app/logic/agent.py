import random
from typing import Optional, Dict
from app.schemas import AITurnRequest, SetupResponse, PlayerTurnResponse, Position, TeamID
from app.logic.state import BoardState
from app.logic.qtable import QLearningManager

class OkinawaAgent:
    def __init__(self):
        self.q_manager = QLearningManager()

    def handle_setup(self, request: AITurnRequest) -> SetupResponse:
        empty_spaces = BoardState.get_empty_spaces(request.board)
        if empty_spaces:
            pos = random.choice(empty_spaces)
            return SetupResponse(row=pos.row, col=pos.col)
        return SetupResponse(row=0, col=0)

    def get_random_turn(self, request: AITurnRequest) -> PlayerTurnResponse:
        """Heurística de fallback em caso de erro ou sem opções."""
        my_professors = BoardState.get_team_professors(request.board, request.your_team)
        if not my_professors:
            return PlayerTurnResponse(professor="UNKNOWN", move_to=Position(row=0, col=0))

        prof_name = random.choice(list(my_professors.keys()))
        return PlayerTurnResponse(
            professor=prof_name,
            move_to=Position(row=random.randint(0, 4), col=random.randint(0, 4)),
            mentor_at=Position(row=random.randint(0, 4), col=random.randint(0, 4))
        )

    def get_critical_move(self, request: AITurnRequest, my_professors: Dict[str, Position]) -> Optional[PlayerTurnResponse]:
        #busca vitoria imediata ou bloqueio
        defensive_move = None

        for prof_name, pos in my_professors.items():
            acoes = BoardState.get_valid_moves(request.board, pos, request.your_team)
            
            for acao in acoes:
                move_to = acao["move_to"]
                mentor_at = acao["mentor_at"]

                #ganhar
                if request.board[move_to.row][move_to.col].level == 3:
                    return PlayerTurnResponse(professor=prof_name, move_to=move_to, mentor_at=mentor_at)
                
                #bloquear inimigo
                if request.board[mentor_at.row][mentor_at.col].level == 3:
                    defensive_move = PlayerTurnResponse(professor=prof_name, move_to=move_to, mentor_at=mentor_at)

        return defensive_move

    def get_defensive_professor(self, request: AITurnRequest, my_professors: Dict[str, Position]) -> Optional[str]:
        #acha o professor mais próximo do inimigo mais perigoso
        enemies = []
        for r in range(5):
            for c in range(5):
                prof = request.board[r][c].professor
                if prof and prof not in my_professors:
                    level = request.board[r][c].level
                    enemies.append({"name": prof, "row": r, "col": c, "level": level})

        dangerous_enemies = [e for e in enemies if e["level"] >= 2]
        if not dangerous_enemies:
            return None

        #pega o inimigo mais evoluído
        alvo = max(dangerous_enemies, key=lambda e: e["level"])
        
        melhor_prof = None
        menor_distancia = 999

        for prof_name, pos in my_professors.items():
            dist = max(abs(pos.row - alvo["row"]), abs(pos.col - alvo["col"]))
            if dist < menor_distancia:
                menor_distancia = dist
                melhor_prof = prof_name

        return melhor_prof

    def handle_turn(self, request: AITurnRequest) -> PlayerTurnResponse:
        my_professors = BoardState.get_team_professors(request.board, request.your_team)
        
        if not my_professors:
            return self.get_random_turn(request)

        # vitoria ou bloqueio
        critical_move = self.get_critical_move(request, my_professors)
        if critical_move:
            print(f"Jogada crítica ativada para {critical_move.professor}")
            return critical_move

        #avalia defesa
        prof_defesa = self.get_defensive_professor(request, my_professors)
        profs_to_evaluate = [prof_defesa] if prof_defesa else list(my_professors.keys())

        melhor_acao_final = None
        melhor_nota_geral = float('-inf')
        prof_escolhido = None

        #consulta q learning
        for prof_name in profs_to_evaluate:
            pos = my_professors[prof_name]
            try:
                acao_q = self.q_manager.choose_action(request.board, prof_name, pos, epsilon=0.0)
                if acao_q:
                    estado = BoardState.get_local_state(request.board, pos.row, pos.col)
                    move = acao_q["move_to"]
                    mentor = acao_q["mentor_at"]
                    acao_str = f"M{move.row},{move.col}_B{mentor.row},{mentor.col}"
                    
                    nota = self.q_manager.q_table.get(estado, {}).get(acao_str, 0.0)

                    if nota > melhor_nota_geral or melhor_acao_final is None:
                        melhor_nota_geral = nota
                        melhor_acao_final = acao_q
                        prof_escolhido = prof_name
            except Exception as e:
                print(f"Erro no Q-Learning para {prof_name}: {e}")

        if melhor_acao_final and prof_escolhido:
            return PlayerTurnResponse(
                professor=prof_escolhido,
                move_to=melhor_acao_final["move_to"],
                mentor_at=melhor_acao_final["mentor_at"]
            )

        return self.get_random_turn(request)