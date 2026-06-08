#logger feito com ajuda de IA para registrar a chamada da API no render
#usado para debugação e entendimento dos requisitos da chamada e devolução
import json
import os
from datetime import datetime

CAMINHO_LOG = "historico_partida.jsonl"

def registrar_payload(payload: dict):
    """
    Imprime o payload formatado no terminal e salva num arquivo de texto.
    """
    fase = payload.get("turn_phase", "DESCONHECIDA")
    turno = payload.get("turn_number", "?")
    
    print(f"\n{'='*50}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] TURNO {turno} | FASE: {fase}")
    print(f"{'='*50}")
    print(json.dumps(payload, indent=2)) 
    print(f"{'='*50}\n")

    try:
        with open(CAMINHO_LOG, "a") as arquivo:
            json.dump(payload, arquivo)
            arquivo.write("\n")
    except Exception as erro:
        print(f"Aviso: Não foi possível salvar o log no arquivo. Erro: {erro}")