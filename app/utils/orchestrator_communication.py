from typing import Any
import aiohttp
import asyncio

from app.models import AgentStatus, CreateRunEvent, CreateRunLog, RunStatus

from .config import AGENT_URL, ORCHESTRATOR_URL, AGENT_ID
from .socket_manager import connect_socketio, sio

# API Communication

async def send_post(url: str, data: dict[str, Any]) -> Any:
    """Send a POST request to the given URL with retry logic."""
    attempts = 0
    while attempts < 5:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, timeout=10) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            print(f"Error sending POST to {url}: {e}. Attempt {attempts + 1}/5")
            attempts += 1
            await asyncio.sleep(5)  # Add a delay before retrying
    return None


async def register_agent() -> None:
    payload = {
        "agent_id": AGENT_ID,
        "status": "available",
        "resources": {"cpu": "normal", "memory": "normal"},
        "public_url": AGENT_URL
    }
    await send_post(f"{ORCHESTRATOR_URL}/agents/register", payload)

# OUTGOING SOCKET.IO EVENTS FROM AGENT

async def send_run_log(run_id: str, data: CreateRunLog) -> None:
    if sio.connected:
        log_data = data.dict()
        log_data['run_id'] = run_id
        await sio.emit('run_log', log_data, namespace='/agent')
    else:
        print("Socket.IO not connected. Log not sent.")

async def send_run_event(run_id: str, data: CreateRunEvent) -> None:
    if sio.connected:
        event_data = data.dict()
        event_data['run_id'] = run_id
        await sio.emit('run_event', event_data, namespace='/agent')
    else:
        print("Socket.IO not connected. Event not sent.")

async def update_run_status(run_id: str, status: RunStatus) -> None:
    if sio.connected:
        await sio.emit('update_run_status', {'run_id': run_id, 'status': status.value}, namespace='/agent')
    else:
        print("Socket.IO not connected. Run status not sent.")

async def send_agent_log(log_message: str) -> None:
    if sio.connected:
        await sio.emit('agent_log', {'agent_id': AGENT_ID, 'log': log_message}, namespace='/agent')
    else:
        print("Socket.IO not connected. Agent log update not sent.")

async def update_agent_status(status: AgentStatus) -> None:
    if sio.connected:
        payload = {
            "agent_id": AGENT_ID,
            "status": status.value,
        }
        await sio.emit('agent_status_update', payload, namespace='/agent')
    else:
        print("Socket.IO not connected. Agent status not sent.")

async def send_heartbeat(status: AgentStatus) -> None:
    if sio.connected:
        await sio.emit('agent_heartbeat', {'agent_id': AGENT_ID, "status": status.value}, namespace='/agent')
    else:
        print("Socket.IO not connected. Heartbeat not sent.")
        await connect_socketio()