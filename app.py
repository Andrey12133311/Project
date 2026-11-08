from fastapi import FastAPI
from models import ProcessRequest, ProcessResult
from agent import CorporateProcessAgent

app = FastAPI(title="ProcessForge Agent", version="0.1.0")
agent = CorporateProcessAgent()

@app.get("/health")
def health():
    return {"status": "ok", "llm_enabled": agent.llm.enabled}

@app.post("/process", response_model=ProcessResult)
def process(req: ProcessRequest):
    return agent.process(req)

@app.get("/demo")
def demo():
    return agent.process(ProcessRequest(text="Срочно: не работает доступ к корпоративной системе у отдела. Нужно восстановить сегодня."))
