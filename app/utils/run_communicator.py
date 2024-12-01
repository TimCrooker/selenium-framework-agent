
from .socket_manager import sio
from .orchestrator_communication import send_post
from .config import ORCHESTRATOR_URL

class RunCommunicator:
    def __init__(self, run_id):
        self.run_id = run_id

    async def send_run_event(self, message, screenshot=None, payload=None):
        if sio.connected:
            event_data = {
                "run_id": self.run_id,
                "message": message,
                "screenshot": screenshot,
                "payload": payload,
            }
            sio.emit('run_event', event_data, namespace='/agent')
        else:
            print("Socket.IO not connected. Event not sent.")

    async def send_run_log(self, log_message):
        await self.send_run_event(message=log_message)

    async def update_run_status(self, status):
        payload = {"status": status}
        await send_post(f"{ORCHESTRATOR_URL}/runs/{self.run_id}/status", payload)