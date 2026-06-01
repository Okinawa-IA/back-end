from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.bot.agent import choose_move

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


@app.post("/move")
async def move(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    print("\nPAYLOAD RECEBIDO DA API DO PROFESSOR")
    print(payload)
  

    action = choose_move(payload)

    return {
        "move": action
    }