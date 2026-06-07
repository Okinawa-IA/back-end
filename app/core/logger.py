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
    
    # 1. Imprime bonito no terminal do VSCode ou Render
    print(f"\n{'='*50}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] TURNO {turno} | FASE: {fase}")
    print(f"{'='*50}")
    # json.dumps com indent=2 deixa o dicionário formatado igual você me mandou
    print(json.dumps(payload, indent=2)) 
    print(f"{'='*50}\n")

    # 2. Salva no arquivo local (muito útil quando rodar no seu PC)
    # Abre em modo "a" (append) para adicionar no final sem apagar o que já tem
    try:
        with open(CAMINHO_LOG, "a") as arquivo:
            # Salva em uma linha só para não misturar no arquivo, 
            # padrão chamado JSONL (JSON Lines)
            json.dump(payload, arquivo)
            arquivo.write("\n")
    except Exception as erro:
        print(f"Aviso: Não foi possível salvar o log no arquivo. Erro: {erro}")