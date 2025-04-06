import json
import asyncio
from typing import Dict
from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse


class SSEService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SSEService, cls).__new__(cls)
            cls._instance.clients = {}
            cls._instance.notification_queue = asyncio.Queue()
        return cls._instance

    async def stream(self, client_id: str, client_type: str):
        if client_id not in self.clients:
            self.clients[client_id] = {
                "type": client_type,
                "queue": asyncio.Queue(),
            }

        client_queue = self.clients[client_id]["queue"]

        async def event_generator():
            try:
                while True:
                    if client_queue.empty():
                        # Keep connection alive with comment
                        yield {"event": "ping", "data": ""}
                        await asyncio.sleep(15)
                        continue

                    message = await client_queue.get()
                    yield {
                        "event": "message",
                        "data": json.dumps(message, default=str),
                    }

            except asyncio.CancelledError:
                # Client disconnected
                if client_id in self.clients:
                    del self.clients[client_id]

        return EventSourceResponse(event_generator())

    def send_notification(self, data: Dict, priority: str = "normal"):
        """
        Send notification to appropriate clients
        """
        # Push notifications to queues for specific types of clients (nurse, doctor)
        for client_id, client_info in self.clients.items():
            # For normal appointments, notify just doctors and nurses
            # For emergencies, notify all connected clients
            if priority == "high" or client_info["type"] in [
                "nurse",
                "doctor",
            ]:
                client_info["queue"].put_nowait(data)


def setup_sse_routes(app: FastAPI):
    """
    Setup SSE routes for the FastAPI app
    """
    sse_service = SSEService()

    @app.get("/api/notifications/{client_id}/{client_type}")
    async def sse_client(client_id: str, client_type: str):
        return await sse_service.stream(client_id, client_type)
