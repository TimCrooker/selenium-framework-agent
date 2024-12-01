from bots.complex_bot import ComplexBot
from bots.google_bot import GoogleBot
from .utils.orchestrator_communication import send_agent_log
from .utils.run_communicator import RunCommunicator

class BotExecutor:
    def __init__(self):
        self.current_bot = None

    async def run_bot_script(self, bot_id, bot_script, run_id):
        if self.current_bot is not None:
            await send_agent_log("Another bot is already running.")
            return
        await send_agent_log(f"Running bot script: {bot_script}")
        communicator = RunCommunicator(run_id)
        await communicator.update_run_status("running")

        try:
            if bot_script == "google_bot":
                bot_instance = GoogleBot(run_id=run_id, communicator=communicator)
            elif bot_script == "complex_bot":
                bot_instance = ComplexBot(run_id=run_id, communicator=communicator)
            else:
                await communicator.update_run_status("error")
                return

            self.current_bot = bot_instance
            await bot_instance.run()

            await communicator.update_run_status("completed")
            await send_agent_log("Bot script completed successfully.")
        except Exception as e:
            await send_agent_log(f"Error running bot script: {str(e)}")
            await communicator.update_run_status("error")
        finally:
            await self.stop_bot(bot_id, run_id)

    async def stop_bot(self, bot_id, run_id):
        if self.current_bot:
            await self.current_bot.handle_termination()
            self.current_bot = None
            communicator = RunCommunicator(run_id)
            await communicator.update_run_status("stopped")
            await send_agent_log(f"Bot {bot_id} with run ID {run_id} has been stopped.")
