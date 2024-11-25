import json
import logging
import os
import time
from typing import List

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ratatosk_errands.model import Echo, Errand
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from mercury.discussant import Discussant
from mercury.models.gpt import GPT
from mercury.models.hermes import Hermes

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.INFO)


class ApiKeyValidator(BaseHTTPMiddleware):
    def __init__(self, app):
        self.api_key = os.getenv("API_KEY")
        super().__init__(app)

    async def dispatch(self, request, call_next):
        request_key = request.headers.get("x-api-key")
        if request_key == self.api_key:
            return await call_next(request)
        else:
            return JSONResponse(status_code=403, content={})


app = FastAPI()
app.add_middleware(ApiKeyValidator)
discussant: Discussant | None = None


class DiscussionRequest(BaseModel):
    model: str
    prompt_names: List[str] | None = None
    question: str | None = None
    context: str | None = None
    discussion_length: int | None = None


@app.post("/discuss")
def discuss(discussant_request: DiscussionRequest):
    global discussant
    if discussant_request.model == "hermes":
        discussant = Hermes(discussant_request.discussion_length)
    if discussant_request.model == "gpt":
        discussant = GPT(discussant_request.prompt_names,
                         discussant_request.question,
                         discussant_request.context,
                         discussant_request.discussion_length)
    else:
        raise HTTPException(status_code=400, detail=f"unknown model: {discussant_request.model}")
    instructions = discussant.generate_instructions()
    errand = Errand(
        instructions=instructions,
        origin="mercury:33333",
        destination="mercury:33333/receive_echo",
        errand_identifier=discussant.get_identifier(),
        timestamp=time.time()
    )
    requests.post("http://errand_runner:33333/give_errand", json=errand.model_dump())


@app.post("/receive_echo")
def receive_echo(echo: Echo):
    global discussant
    logger.info(f"(*) received echo: {json.dumps(echo.model_dump(), indent=4)}")
    if echo.errand.errand_identifier == discussant.get_identifier():
        discussant.add_message(echo.reply.message)
        if not discussant.finished():
            instructions = discussant.generate_instructions()
            errand = Errand(
                instructions=instructions,
                origin="mercury:33333",
                destination="mercury:33333/receive_echo",
                errand_identifier=discussant.get_identifier(),
                timestamp=time.time()
            )
            requests.post("http://errand_runner:33333/give_errand", json=errand.model_dump())
    else:
        logger.info(f"(*) ignoring echo with unknown identifier: {echo.errand.errand_identifier}")


class PollResponse(BaseModel):
    finished: bool
    dialog: List[str]


@app.post("/poll")
def poll():
    global discussant
    logger.info(f"(*) polling dialog")
    if not discussant.finished():
        return PollResponse(finished=False, dialog=[])
    else:
        return PollResponse(finished=True, dialog=discussant.get_dialog())
