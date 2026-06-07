from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.bot.agent import process_request

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
        return {} #erro de leitura

    print(f"\n[FASE: {payload.get('turn_phase')}] PAYLOAD RECEBIDO")
    
    #devolucao do dict certinho
    response_data = process_request(payload)
    
    return response_data