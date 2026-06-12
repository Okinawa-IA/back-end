import os
import pickle
import random
from app.schemas import Cell, Position, TeamID
from app.logic.state import BoardState
from app.logic.qtable import QLearningManager

# pega o caminho absoluto da pasta storage
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")

def criar_tabuleiro_vazio() -> list[list[Cell]]:
    return [[Cell(level=0, professor=None) for _ in range(5)] for _ in range(5)]

def aplicar_acao(tabuleiro: list[list[Cell]], prof_nome: str, pos_antiga: Position, acao: dict):
    move_to = acao["move_to"]
    mentor_at = acao["mentor_at"]
    
    tabuleiro[pos_antiga.row][pos_antiga.col].professor = None
    tabuleiro[move_to.row][move_to.col].professor = prof_nome
    tabuleiro[mentor_at.row][mentor_at.col].level += 1

def treinar(num_partidas=1000000):
    vitorias_t1 = 0
    vitorias_t2 = 0
    empates = 0
    
    q_manager = QLearningManager()
    
    epsilon_inicial = 1.0
    epsilon_final = 0.1
    
    snapshot_count = 1 # contador para os arquivos pickle
    
    #garante que a pasta existe antes de salvar
    os.makedirs(STORAGE_DIR, exist_ok=True)
    
    for partida in range(1, num_partidas + 1):
        tabuleiro = criar_tabuleiro_vazio()
        posicoes = random.sample([(r, c) for r in range(5) for c in range(5)], 4)
        profs = ["CLARO", "REY", "KARIN", "BEATRIZ"]
        prof_pos = {}
        
        for i, nome in enumerate(profs):
            r, c = posicoes[i]
            tabuleiro[r][c].professor = nome
            prof_pos[nome] = Position(row=r, col=c)
            
        epsilon_atual = epsilon_inicial - (epsilon_inicial - epsilon_final) * (partida / num_partidas)
        
        turnos = 0
        ganhador = None
        
        while turnos < 100:
            turnos += 1
            
            # --- TURNO DO TIME 1 (TURING) ---
            prof_t1_nome = random.choice(["CLARO", "REY"])
            pos_t1 = prof_pos[prof_t1_nome]
            
            acao_t1 = q_manager.choose_action(tabuleiro, prof_t1_nome, pos_t1, epsilon_atual)
            if acao_t1:
                aplicar_acao(tabuleiro, prof_t1_nome, pos_t1, acao_t1)
                prof_pos[prof_t1_nome] = acao_t1["move_to"]
                if tabuleiro[acao_t1["move_to"].row][acao_t1["move_to"].col].level == 3:
                    vitorias_t1 += 1
                    ganhador = 1
                    break
            
            # --- TURNO DO TIME 2 (LOVELACE) ---
            prof_t2_nome = random.choice(["KARIN", "BEATRIZ"])
            pos_t2 = prof_pos[prof_t2_nome]
            
            acao_t2 = q_manager.choose_action(tabuleiro, prof_t2_nome, pos_t2, epsilon_atual)
            if acao_t2:
                aplicar_acao(tabuleiro, prof_t2_nome, pos_t2, acao_t2)
                prof_pos[prof_t2_nome] = acao_t2["move_to"]
                if tabuleiro[acao_t2["move_to"].row][acao_t2["move_to"].col].level == 3:
                    vitorias_t2 += 1
                    ganhador = 2
                    break
                    
        if not ganhador: empates += 1

        if partida % 50000 == 0:
            print(f"\n[{partida}/{num_partidas}] Vitórias T1: {vitorias_t1} | Vitórias T2: {vitorias_t2} | Empates: {empates} | Epsilon: {epsilon_atual:.2f}")
            
            snapshot_path = os.path.join(STORAGE_DIR, f"qtable{snapshot_count}.pickle")
            with open(snapshot_path, "wb") as file:
                pickle.dump(q_manager.q_table, file)
                
            tamanho_kb = os.path.getsize(snapshot_path) / 1024
            print(f"Salvo: {snapshot_path} ({tamanho_kb:.2f} KB)")
            
            snapshot_count += 1
            vitorias_t1 = vitorias_t2 = empates = 0

if __name__ == "__main__":
    print(f"Iniciando treinamento Self-Play...")
    treinar(1000000)
    print("\nTreinamento Finalizado!")