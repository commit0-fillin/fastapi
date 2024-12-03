from typing import Any, Dict, Optional, Sequence, Type, Union
from pydantic import BaseModel, create_model
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.exceptions import WebSocketException as StarletteWebSocketException
from typing_extensions import Annotated, Doc

class HTTPException(StarletteHTTPException):
    """
    An HTTP exception you can raise in your own code to show errors to the client.

    This is for client errors, invalid authentication, invalid data, etc. Not for server
    errors in your code.

    Read more about it in the
    [FastAPI docs for Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/).

    ## Example

    ```python
    from fastapi import FastAPI, HTTPException

    app = FastAPI()

    items = {"foo": "The Foo Wrestlers"}


    @app.get("/items/{item_id}")
    async def read_item(item_id: str):
        if item_id not in items:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"item": items[item_id]}
    ```
    """

    def __init__(self, status_code: Annotated[int, Doc('\n                HTTP status code to send to the client.\n                ')], detail: Annotated[Any, Doc('\n                Any data to be sent to the client in the `detail` key of the JSON\n                response.\n                ')]=None, headers: Annotated[Optional[Dict[str, str]], Doc('\n                Any headers to send to the client in the response.\n                ')]=None) -> None:
        super().__init__(status_code=status_code, detail=detail)
        self.headers = headers

class WebSocketException(StarletteWebSocketException):
    """
    A WebSocket exception you can raise in your own code to show errors to the client.

    This is for client errors, invalid authentication, invalid data, etc. Not for server
    errors in your code.

    Read more about it in the
    [FastAPI docs for WebSockets](https://fastapi.tiangolo.com/advanced/websockets/).

    ## Example

    ```python
    from typing import Annotated

    from fastapi import (
        Cookie,
        FastAPI,
        WebSocket,
        WebSocketException,
        status,
    )

    app = FastAPI()

    @app.websocket("/items/{item_id}/ws")
    async def websocket_endpoint(
        *,
        websocket: WebSocket,
        session: Annotated[str | None, Cookie()] = None,
        item_id: str,
    ):
        if session is None:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Session cookie is: {session}")
            await websocket.send_text(f"Message text was: {data}, for item ID: {item_id}")
    ```
    """

    def __init__(self, code: Annotated[int, Doc('\n                A closing code from the\n                [valid codes defined in the specification](https://datatracker.ietf.org/doc/html/rfc6455#section-7.4.1).\n                ')], reason: Annotated[Union[str, None], Doc('\n                The reason to close the WebSocket connection.\n\n                It is UTF-8-encoded data. The interpretation of the reason is up to the\n                application, it is not specified by the WebSocket specification.\n\n                It could contain text that could be human-readable or interpretable\n                by the client code, etc.\n                ')]=None) -> None:
        super().__init__(code=code, reason=reason)
RequestErrorModel: Type[BaseModel] = create_model('Request')
WebSocketErrorModel: Type[BaseModel] = create_model('WebSocket')

class FastAPIError(RuntimeError):
    """
    A generic, FastAPI-specific error.
    """

class ValidationException(Exception):

    def __init__(self, errors: Sequence[Any]) -> None:
        self._errors = errors

class RequestValidationError(ValidationException):

    def __init__(self, errors: Sequence[Any], *, body: Any=None) -> None:
        super().__init__(errors)
        self.body = body

class WebSocketRequestValidationError(ValidationException):
    pass

class ResponseValidationError(ValidationException):

    def __init__(self, errors: Sequence[Any], *, body: Any=None) -> None:
        super().__init__(errors)
        self.body = body

    def __str__(self) -> str:
        message = f'{len(self._errors)} validation errors:\n'
        for err in self._errors:
            message += f'  {err}\n'
        return message
