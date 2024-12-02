import asyncio
from typing import NoReturn

from .utils.orchestrator_communication import send_heartbeat, send_agent_log
from .utils.config import HEARTBEAT_INTERVAL
from .bot_executor import executor

async def execute_bot(bot_id: str, bot_script: str, run_id: str) -> None:
    """Start executing a bot."""
    await send_agent_log(f"Executing bot {bot_id} with script {bot_script} and run ID {run_id}.")
    await executor.run_bot_script(bot_id, bot_script, run_id)

async def maintain_heartbeat() -> NoReturn:
    """Send periodic heartbeat to the orchestrator."""
    while True:
        try:
            status = executor.get_status()
            await send_heartbeat(status)
        except Exception as e:
            await send_agent_log(f"Failed to send heartbeat: {e}")
        await asyncio.sleep(HEARTBEAT_INTERVAL)
