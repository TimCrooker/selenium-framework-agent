import asyncio
import requests

from .bot_executor import BotExecutor
from .utils.orchestrator_communication import send_post, send_agent_log
from .utils.config import AGENT_URL, HEARTBEAT_INTERVAL, ORCHESTRATOR_URL, AGENT_ID

executor = BotExecutor()

async def execute_bot(bot_id, bot_script, run_id):
    """Start executing a bot."""
    await send_agent_log(f"Executing bot {bot_id} with script {bot_script} and run ID {run_id}.")
    await executor.run_bot_script(bot_id, bot_script, run_id)

async def stop_bot(bot_id, run_id):
    """Stop a running bot."""
    await send_agent_log(f"Stopping bot {bot_id} with run ID {run_id}.")
    await executor.stop_bot(bot_id, run_id)

async def register_agent():
    """Register the agent with the orchestrator."""
    payload = {
        "agent_id": AGENT_ID,
        "status": "available",
        "resources": {
            "cpu": "normal",
            "memory": "normal"
        },
        "public_url": AGENT_URL
    }
    try:
        await send_post(f"{ORCHESTRATOR_URL}/agents/register", payload)
        await send_agent_log(f"Agent {AGENT_ID} successfully registered.")
    except requests.RequestException as e:
        await send_agent_log(f"Error registering agent: {e}")

async def send_heartbeat():
    """Send periodic heartbeat to the orchestrator."""
    while True:
        try:
            await send_post(f"{ORCHESTRATOR_URL}/agents/{AGENT_ID}/heartbeat", {})
            await send_agent_log(f"Heartbeat sent from agent {AGENT_ID}")
        except Exception as e:
            await send_agent_log(f"Failed to send heartbeat: {e}")
        await asyncio.sleep(HEARTBEAT_INTERVAL)
