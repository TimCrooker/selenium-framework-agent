from enum import Enum
from typing import Optional
from pydantic import BaseModel

class RunStatus(str, Enum):
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    STARTING = "starting"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AgentStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    STOPPED = "stopped"
    OFFLINE = "offline"

class AgentRegistration(BaseModel):
    agent_id: str
    status: str
    resources: dict

class RunStatusUpdate(BaseModel):
    run_id: str
    status: str
    message: Optional[str] = None

class BotRunRequest(BaseModel):
    bot_id: str
    bot_script: str
    run_id: str

class CreateRunLog(BaseModel):
    level: LogLevel = LogLevel.INFO
    message: str
    payload: Optional[dict] = None

class CreateRunEvent(BaseModel):
    event_type: str
    message: str
    screenshot: Optional[str] = None
    payload: Optional[dict] = None