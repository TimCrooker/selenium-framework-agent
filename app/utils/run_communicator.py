from app.models import CreateRunEvent, CreateRunLog, RunStatus
from .socket_manager import sio
from enum import Enum

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class RunCommunicator:
    def __init__(self, run_id: str) -> None:
        self.run_id = run_id

    async def send_run_log(self, data: CreateRunLog) -> None:
        if sio.connected:
            log_data = data.dict()
            log_data['run_id'] = self.run_id
            await sio.emit('run_log', log_data, namespace='/agent')
        else:
            print("Socket.IO not connected. Log not sent.")

    async def send_run_event(self, data: CreateRunEvent) -> None:
        if sio.connected:
            event_data = data.dict()
            event_data['run_id'] = self.run_id
            await sio.emit('run_event', event_data, namespace='/agent')
        else:
            print("Socket.IO not connected. Event not sent.")

    async def update_run_status(self, status: RunStatus) -> None:
        if sio.connected:
            await sio.emit('update_run_status', {"run_id": self.run_id, "status": status}, namespace='/agent')
        else:
            print("Socket.IO not connected. Status not updated.")