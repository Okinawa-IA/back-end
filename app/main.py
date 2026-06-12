from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import AITurnRequest, TurnPhase
from app.logic.agent import OkinawaAgent

app = FastAPI(title="Okinawa IA Bot Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = OkinawaAgent()

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "bot": "Okinawa IA",
        "message": "Backend do bot rodando",
    }

@app.post("/move")
async def move(body: AITurnRequest):
    """
    Recebe o estado completo tipado (AITurnRequest) e roteia para o agente.
    """
    if body.turn_phase == TurnPhase.SETUP:
        return agent.handle_setup(body)
    else:
        return agent.handle_turn(body)