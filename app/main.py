import asyncio
from app.utils.socket_manager import connect_socketio
from app.models import BotRunRequest, RunStatus
from fastapi import FastAPI, HTTPException
from app.agent_service import executor, execute_bot, maintain_heartbeat
from app.utils.orchestrator_communication import register_agent, send_agent_log, update_run_status

app = FastAPI()

@app.on_event("startup")
async def startup_event() -> None:
    await connect_socketio()
    await register_agent()
    asyncio.create_task(maintain_heartbeat())
    await send_agent_log("Agent started and connected to orchestrator.")

@app.post("/run")
async def run_bot(request: BotRunRequest) -> bool:
    if executor.current_bot is not None:
        await send_agent_log("Attempted to start a new bot while another is running.")
        raise HTTPException(status_code=400, detail="Another bot is already running on this agent.")

    await update_run_status(run_id=request.run_id, status=RunStatus.STARTING)
    asyncio.create_task(execute_bot(request.bot_id, request.bot_script, request.run_id))
    await send_agent_log(f"Started bot {request.bot_id} with run ID {request.run_id}.")
    return True