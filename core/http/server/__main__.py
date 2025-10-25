from threading import Thread
from typing import Callable, Self

import uvicorn
import websockets
from fastapi import FastAPI, WebSocket


class HTTPIPC:
    """
    Using this class to register events and other kind of http services
    """

    WS_BASE_NAME = "ws_base"

    def __new__(cls, address: str, port: int, base_route: str = "/ws") -> Self:
        cls._inst = getattr(
            cls,
            "_inst",
            super().__new__(
                cls,
            ),
        )
        return cls._inst

    def __init__(self, address: str, port: int, base_route: str = "/ws"):
        self._app = FastAPI()
        self._app.websocket(base_route, name=self.WS_BASE_NAME)(self.handle_websocket)
        self._address = address
        self._port = port
        self._events: dict[str, list[Callable[..., None]]] = {}

    def start(
        self,
    ):
        """
        Initialize the event loop for the web server
        """
        thread = (
            Thread(  # Starts the event loop in another thread hope this is possible
                target=uvicorn.run,
                args=(self._app,),
                name="HTTP IPC: Forge",
                kwargs={"host": self._address, "port": self._port},
            )
        )
        thread.start()
        return self._app

    async def subscribe(self, gsql_schema: str, callback: Callable[..., None]):
        """
        Using GraphQL, subscribe to a real time websocket event and process the result
        """
        async with websockets.connect(
            self._app.url_path_for(self.WS_BASE_NAME)
        ) as ws_client:
            await ws_client.send(gsql_schema)
            while True:
                result = await ws_client.recv()
                callback(result)

    async def query(self, gsql_schema: str):
        """
        Make a GraphQL query to the HTTP IPC class and obtain a data from the server
        """
        async with websockets.connect(
            self._app.url_path_for(self.WS_BASE_NAME)
        ) as ws_client:
            await ws_client.send(gsql_schema)
            return ws_client.recv()

    async def mutate(self, gsql_schema: str):
        """
        Mutate the GraphQL server state
        """
        async with websockets.connect(
            self._app.url_path_for(self.WS_BASE_NAME)
        ) as ws_client:
            await ws_client.send(gsql_schema)
            return ws_client.recv()

    def create_event(self, name: str):
        """
        Create an event which is translated in the WS context to a channel, on the event of trigger on that channel,
        the channel must broadcast to all listening (subscribed) clients for the event
        usage:
        ```py
        ipc = HTTPIPC()
        ipc.create_event("exit")
        ipc.subscribe()
        ```
        """
        self._events[name] = self._events.get("name", [])

    def trigger_event(self, name: str, *args: str, **kwargs: str):
        """
        Trigger an event to all listening clients
        """
        for callback in self._events.get(name, []):
            callback(*args, **kwargs)

    async def handle_websocket(self, websocket: WebSocket):
        await websocket.accept()
        await websocket.send_text("Hello from server!")
        message = await websocket.receive_text()
        print(f"Server received: {message}")
        await websocket.close()
