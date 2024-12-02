from typing import Any
import socketio
from .config import ORCHESTRATOR_URL

# Configure Socket.IO client
sio = socketio.Client(
    reconnection=True,
    reconnection_attempts=5,
    reconnection_delay=5,
    # Disable all logging
    logger=False,
    engineio_logger=False
)

# Define the connection URL for Socket.IO
SOCKET_IO_URL = f"{ORCHESTRATOR_URL.replace('http', 'ws')}/socket.io"

def connect_socketio() -> None:
    """Connect the Socket.IO client to the orchestrator."""
    try:
        print(f"Attempting to connect to Socket.IO server at {SOCKET_IO_URL}/agent...")
        sio.connect(SOCKET_IO_URL, namespaces=['/agent'], transports=['websocket'])
        print("Socket.IO connected successfully.")
    except Exception as e:
        print(f"Socket.IO connection failed: {e}")

# Event handlers for Socket.IO
@sio.event(namespace='/agent')
def connect() -> None:
    print("Connected to Socket.IO server in the agent namespace.")

@sio.event(namespace='/agent')
def connect_error(data: Any) -> None:
    print(f"Connection failed with data: {data}")

@sio.event(namespace='/agent')
def disconnect() -> None:
    print("Disconnected from Socket.IO server in the agent namespace.")
