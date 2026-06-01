
````
# Okinawa Bot API

Backend em Python com FastAPI para o bot do projeto PI5.

Este serviço expõe um endpoint público de movimento do jogador, que será cadastrado na API principal do professor como `ai_player_move_endpoint`.

## Objetivo

O objetivo deste backend é receber o estado atual da partida enviado pela API do professor e retornar uma ação de movimento para o jogador inteligente do grupo **Okinawa IA**.

Fluxo esperado:

```txt
API do professor
        ↓
POST /move
        ↓
Backend Okinawa Bot API
        ↓
Resposta com movimento do jogador
````

## Tecnologias utilizadas

* Python
* FastAPI
* Uvicorn
* Pydantic
* Python Dotenv

## Estrutura do projeto

```txt
bot-backend/
├── app/
│   ├── main.py
│   │
│   ├── bot/
│   │   ├── agent.py
│   │   ├── heuristic.py
│   │   ├── q_learning.py
│   │   └── state_parser.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   └── storage/
│       └── q_table.json
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## Instalação

### 1. Criar ambiente virtual

No Windows:

```bash
python -m venv .venv
```

Ativar o ambiente virtual:

```bash
.venv\Scripts\activate
```

No Linux/Mac:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instalar dependências

Com o ambiente virtual ativado, rode:

```bash
pip install -r requirements.txt
```

## Arquivo `requirements.txt`

O arquivo `requirements.txt` deve conter:

```txt
fastapi
uvicorn
python-dotenv
pydantic
```

Essas dependências são responsáveis por:

```txt
fastapi        → criação da API
uvicorn        → servidor para rodar o FastAPI
python-dotenv  → leitura de variáveis de ambiente
pydantic       → validação de dados
```

## Como rodar localmente

Na raiz do projeto, execute:

```bash
uvicorn app.main:app --reload
```

A API ficará disponível em:

```txt
http://127.0.0.1:8000
```

A documentação automática ficará disponível em:

```txt
http://127.0.0.1:8000/docs
```

## Endpoints

### Health Check

```http
GET /
```

Retorna uma mensagem indicando que o backend está rodando.

Exemplo de resposta:

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

Endpoint chamado pela API do professor para solicitar o próximo movimento do jogador.

Resposta atual:

```json
{
  "move": "UP"
}
```

Neste primeiro momento, o bot retorna um movimento simples. Depois, a lógica será evoluída para heurística e Q-Learning.

## Estratégia do bot

A estratégia planejada é seguir três etapas:

```txt
1. Heurística simples
2. Q-Learning
3. Fallback aleatório
```

### Heurística

A heurística inicial deve analisar o estado do tabuleiro e tentar mover o jogador em direção ao professor mais próximo.

### Q-Learning

Depois da heurística inicial, será implementado Q-Learning para permitir que o bot aprenda melhores ações a partir dos estados da partida.

### Fallback

Caso ocorra algum erro na escolha da jogada, o bot deve retornar um movimento válido padrão para não quebrar a partida.

## Deploy

O backend precisa estar publicado em uma URL pública, pois a API do professor não consegue acessar o ambiente local:

```txt
http://127.0.0.1:8000/move
```

Exemplo de URL pública esperada:

```txt
https://okinawa-bot-api.onrender.com/move
```

Depois do deploy, essa URL deve ser cadastrada no jogador usando o endpoint da API principal:

```json
{
  "ai_player_move_endpoint": "https://okinawa-bot-api.onrender.com/move"
}
```

## Comando de deploy no Render

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Próximos passos

* Publicar o backend no Render.
* Atualizar o endpoint de movimento do jogador.
* Iniciar uma partida.
* Verificar nos logs qual payload a API do professor envia para o `/move`.
* Implementar o parser do estado da partida.
* Criar a heurística de movimento.
* Evoluir para Q-Learning.

````

E confere se o `requirements.txt` está assim:

```txt
fastapi
uvicorn
python-dotenv
pydantic
````
