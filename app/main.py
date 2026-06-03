from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.bot.agent import choose_move
from app.models.schemas import MoveResponse, DebugMoveResponse

app = FastAPI(title="Okinawa IA Bot Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "bot": "Okinawa IA",
        "message": "Backend do bot rodando",
    }


@app.post("/move", response_model=MoveResponse)
async def move(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    print("\n PAYLOAD RECEBIDO DA API DO PROFESSOR")
    print(payload)

    action = choose_move(payload)

    return {
        "move": action
    }


@app.post("/debug/move", response_model=DebugMoveResponse)
async def debug_move(request: Request):
    """
    Endpoint local para testar o bot e visualizar o payload recebido.
    Não precisa ser cadastrado na API do professor.
    """

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    action = choose_move(payload)

    return {
        "move": action,
        "received_payload": payload,
    }