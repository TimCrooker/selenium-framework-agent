from typing import Optional
from app.models import AgentStatus, CreateRunEvent, RunStatus
from app.utils.config import SELENIUM_REMOTE_URL
from bots.base_bot import BaseBot
from bots.complex_bot import ComplexBot
from bots.google_bot import GoogleBot
from .utils.orchestrator_communication import send_agent_log, send_run_event, update_agent_status, update_run_status
from .utils.run_communicator import RunCommunicator

class BotExecutor:
    def __init__(self) -> None:
        self.current_bot: Optional[BaseBot] = None

    async def run_bot_script(self, bot_id: str, bot_script: str, run_id: str) -> None:
        if self.current_bot is not None:
            await send_agent_log("Another bot is already running.")
            return
        await send_agent_log(f"Running bot script: {bot_script}")
        communicator = RunCommunicator(run_id)
        await update_run_status(run_id, RunStatus.RUNNING)
        await update_agent_status(AgentStatus.BUSY)

        try:
            if bot_script == "google_bot":
                self.current_bot = GoogleBot(run_id=run_id, communicator=communicator, selenium_remote_url=SELENIUM_REMOTE_URL)
            elif bot_script == "complex_bot":
                self.current_bot = ComplexBot(run_id=run_id, communicator=communicator, selenium_remote_url=SELENIUM_REMOTE_URL)
            else:
                await update_run_status(run_id, RunStatus.ERROR)
                await send_agent_log(f"Bot script {bot_script} not found.")
                return

            await self.current_bot.run()

            await send_agent_log("Bot script completed successfully.")
            await update_run_status(run_id, RunStatus.COMPLETED)
        except Exception as e:
            await send_agent_log(f"Error running bot script: {str(e)}")
            await send_run_event(run_id=run_id, data=CreateRunEvent(event_type="error", message=str(e)))
            await update_run_status(run_id, RunStatus.ERROR)
        finally:
            await self.stop_bot(bot_id, run_id)
            await update_agent_status(AgentStatus.AVAILABLE)

    async def stop_bot(self, bot_id: str, run_id: str) -> None:
        if self.current_bot:
            await self.current_bot.teardown()
            self.current_bot = None
            await send_agent_log(f"Bot {bot_id} with run ID {run_id} has been stopped.")

    def get_status(self) -> AgentStatus:
        if self.current_bot:
            return AgentStatus.BUSY
        return AgentStatus.AVAILABLE

executor = BotExecutor()
