# Okinawa Bot API - PI5

Backend em Python com FastAPI para o agente do projeto PI5.

Este serviço expõe um endpoint público de movimento do jogador, que é cadastrado na API principal do torneio como `ai_player_move_endpoint`. O agente utiliza uma arquitetura de Inteligência Híbrida (Heurísticas Globais + Q-Learning Local).

## Objetivo

O objetivo deste backend é receber o estado atual da partida enviado pela API do professor e retornar, em tempo real (menos de 5 segundos), uma ação de movimento e mentoria para o time **Okinawa IA**.

Fluxo esperado:

```txt
API do professor
        ↓
POST /move (JSON com tabuleiro 5x5)
        ↓
Backend Okinawa Bot API (Pydantic -> State -> Agent -> Q-Table)
        ↓
Resposta com movimento do jogador e mentoria
```

## Tecnologias utilizadas

* **Python 3**
* **FastAPI** 
* **Uvicorn** 
* **Pydantic** 
* **Pickle** 

## Estrutura do projeto

O projeto segue os princípios de Orientação a Objetos:

```txt
BACK-END/
├── app/
│   ├── logic/
│   │   ├── agent.py      # Cérebro estratégico (Heurísticas e Delegação)
│   │   ├── qtable.py     # Gerenciador do modelo de Machine Learning (Bellman)
│   │   └── state.py      # Motor físico (Limites, validações e visão 3x3)
│   │
│   ├── main.py           # Roteador da API FastAPI
│   └── schemas.py        # Contratos DTO e validação Pydantic
│
├── storage/
│   └── q_table.pickle    # Arquivo binário (Cérebro treinado do bot)
│
├── .gitignore
├── README.md
├── REPORT.md
├── requirements.txt
└── treinar_offline.py    # Script de treinamento Self-Play
```

## Instalação

### 1. Criar ambiente virtual

No Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

No Linux/Mac:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instalar dependências

Com o ambiente virtual ativado, instale as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

## Como rodar localmente

Na raiz do projeto, execute o servidor de desenvolvimento:

```bash
uvicorn app.main:app --reload
```

A API ficará disponível em: `http://127.0.0.1:8000`
A documentação interativa (Swagger) ficará em: `http://127.0.0.1:8000/docs`

## Endpoints

### Health Check

```http
GET /
```

Retorna o status da infraestrutura. Exemplo de resposta:

```json
{
  "status": "ok",
  "bot": "Okinawa IA",
  "message": "Backend do bot rodando"
}
```

### Movimento do bot

```http
POST /move
```

Endpoint que recebe o `AITurnRequest` completo e devolve a próxima jogada calculada pela IA.

Exemplo de resposta de sucesso (`PlayerTurnResponse`):

```json
{
  "professor": "CLARO",
  "move_to": {
    "row": 1,
    "col": 2
  },
  "mentor_at": {
    "row": 1,
    "col": 3
  }
}
```

## Estratégia da Inteligência (Okinawa IA)

Para contornar os limites de RAM na nuvem e o timeout da partida, o bot foi estruturado em três camadas táticas de Inteligência Híbrida:

1. **Heurística Global (Visão Macro):** O bot rastreia o tabuleiro 5x5 inteiro. Se encontrar uma condição de vitória garantida, ou se precisar bloquear a vitória iminente do inimigo (fechando um Nível 3), ele age instantaneamente, ignorando a Tabela Q.
2. **Q-Learning Tabular (Visão Micro):** Sem emergências globais, a IA corta uma matriz 3x3 focada no professor e consulta o arquivo `q_table.pickle`. Treinado com mais de 150.000 partidas em Self-Play, o algoritmo toma a decisão de posicionamento e combate de curto alcance que possuir a maior nota histórica (Q-Value).
3. **Fallback Aleatório:** Uma rede de segurança. Se o professor ficar totalmente encurralado pela física do jogo e o Q-Learning não retornar nada, o bot calcula um movimento aleatório estritamente dentro das leis do tabuleiro para não quebrar a partida e evitar desclassificação.

## Deploy no Railway

A API está publicada no Railway e atende diretamente às requisições do servidor central da disciplina.

* **URL Base:** `https://back-end-production-f7ba.up.railway.app/`
* **URL do Endpoint de Jogada:** `https://back-end-production-f7ba.up.railway.app/move`

Campo de endpoint de movimento abaixo:

```json
{
  "ai_player_move_endpoint": "https://back-end-production-f7ba.up.railway.app/move"
}
```