import json
import logging
import time
import uuid

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ratatosk_errands.model import Echo, ChatInstructions, Errand

from mercury.discussant import Discussant
from mercury.models.hermes import Hermes

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.INFO)

app = FastAPI()
discussant: Discussant | None = None


class DiscussionRequest(BaseModel):
    model: str = ""
    system_prompt: str = ""


@app.post("/discuss")
def discuss(discussant_request: DiscussionRequest):
    global discussant
    if discussant_request.model == "hermes":
        discussant = Hermes(system_prompt=discussant_request.system_prompt)
    else:
        raise HTTPException(status_code=400, detail=f"unknown model: {discussant_request.model}")
    instructions = ChatInstructions(
        prompt=discussant.generate_prompt()
    )
    errand = Errand(
        instructions=instructions,
        origin="mercury:33333",
        destination="mercury:33333",
        errand_identifier=str(uuid.uuid4()),
        timestamp=time.time()
    )
    requests.post("http://errand_runner:33333/give_errand", json=errand.model_dump())


@app.post("/receive_echo")
def receive_echo(echo: Echo):
    global discussant
    logger.info(f"(*) received echo: {json.dumps(echo.model_dump(), indent=4)}")
    discussant.add_message(echo.reply.message)
    instructions = ChatInstructions(
        prompt=discussant.generate_prompt()
    )
    errand = Errand(
        instructions=instructions,
        origin="mercury:33333",
        destination="mercury:33333",
        errand_identifier=str(uuid.uuid4()),
        timestamp=time.time()
    )
    requests.post("http://errand_runner:33333/give_errand", json=errand.model_dump())
