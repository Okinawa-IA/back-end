# código gerado com ajuda de IA para fazer o treinamento do nosso modelo e preenchimento da tabela Q
# =============================================================================================
import random
from app.bot.q_learning import escolher_acao_qlearning, load_q_table, save_q_table
from app.bot.state_parser import get_acoes_validas

def criar_tabuleiro_vazio():
    return [[{"level": 0, "professor": None} for _ in range(5)] for _ in range(5)]

def aplicar_acao(tabuleiro, prof_nome, pos_antiga, acao):
    tabuleiro[pos_antiga["row"]][pos_antiga["col"]]["professor"] = None
    tabuleiro[acao["move_to"]["row"]][acao["move_to"]["col"]]["professor"] = prof_nome
    tabuleiro[acao["mentor_at"]["row"]][acao["mentor_at"]["col"]]["level"] += 1

def treinar(num_partidas=100000):
    vitorias_time1 = 0
    vitorias_time2 = 0
    empates = 0
    
    q_table = load_q_table()
    
    epsilon_inicial = 1.0
    epsilon_final = 0.1
    
    for partida in range(1, num_partidas + 1):
        tabuleiro = criar_tabuleiro_vazio()
        posicoes = random.sample([(r, c) for r in range(5) for c in range(5)], 4)
        profs = ["CLARO", "REY", "KARIN", "BEATRIZ"]
        prof_pos = {}
        
        for i, nome in enumerate(profs):
            r, c = posicoes[i]
            tabuleiro[r][c]["professor"] = nome
            prof_pos[nome] = {"row": r, "col": c}
            
        # Decaimento linear do Epsilon
        epsilon_atual = epsilon_inicial - (epsilon_inicial - epsilon_final) * (partida / num_partidas)
        
        turnos = 0
        ganhador = None
        
        while turnos < 100:
            turnos += 1
            
            # Time 1 ------
            prof_t1 = random.choice(["CLARO", "REY"])
            pos_t1 = prof_pos[prof_t1]
            acao_t1 = escolher_acao_qlearning(tabuleiro, prof_t1, pos_t1["row"], pos_t1["col"], q_table, epsilon_atual)
            if acao_t1:
                aplicar_acao(tabuleiro, prof_t1, pos_t1, acao_t1)
                prof_pos[prof_t1] = acao_t1["move_to"]
                if tabuleiro[acao_t1["move_to"]["row"]][acao_t1["move_to"]["col"]]["level"] == 3:
                    vitorias_time1 += 1
                    ganhador = 1
                    break
            
            # Time 2 (Self-play: Usa a mesma tabela e o mesmo epsilon)
            prof_t2 = random.choice(["KARIN", "BEATRIZ"])
            pos_t2 = prof_pos[prof_t2]
            acao_t2 = escolher_acao_qlearning(tabuleiro, prof_t2, pos_t2["row"], pos_t2["col"], q_table, epsilon_atual)
            if acao_t2:
                aplicar_acao(tabuleiro, prof_t2, pos_t2, acao_t2)
                prof_pos[prof_t2] = acao_t2["move_to"]
                if tabuleiro[acao_t2["move_to"]["row"]][acao_t2["move_to"]["col"]]["level"] == 3:
                    vitorias_time2 += 1
                    ganhador = 2
                    break
                    
        if not ganhador: empates += 1

        # Salva fisicamente a cada 5.000 partidas para não estressar o HD
        if partida % 5000 == 0:
            print(f"Partidas: {partida}/{num_partidas} | Vitórias T1: {vitorias_time1} | Vitórias T2: {vitorias_time2} | Empates: {empates} | Epsilon: {epsilon_atual:.2f}")
            save_q_table(q_table) 
            vitorias_time1 = vitorias_time2 = empates = 0 # Reseta parciais
            

    save_q_table(q_table) #salva fora do for

if __name__ == "__main__":
    qtd = 50000
    print(f"Iniciando treinamento turbo de {qtd} partidas...")
    treinar(qtd)
    print("\n✅ TREINAMENTO FINALIZADO COM SUCESSO!")