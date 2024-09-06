import json
import logging
import time
import uuid

import requests
from fastapi import FastAPI
from ratatosk_errands.model import Echo, ChatInstructions, Errand
from transformers import AutoTokenizer

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.INFO)

app = FastAPI()

tokenizer = AutoTokenizer.from_pretrained(
    "NousResearch/Hermes-3-Llama-3.1-70B",
    trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "left"
messages = [
    {"role": "system", "content": "hermes trismegistus"},
]


def kickoff_chat():
    instructions = ChatInstructions(
        prompt=tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
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
    logger.info(f"(*) received echo: {json.dumps(echo.model_dump(), indent=4)}")
    messages.append({"role": "assistant", "content": echo.reply.message})
    instructions = ChatInstructions(
        prompt=tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
    )
    errand = Errand(
        instructions=instructions,
        origin="mercury:33333",
        destination="mercury:33333",
        errand_identifier=str(uuid.uuid4()),
        timestamp=time.time()
    )
    requests.post("http://errand_runner:33333/give_errand", json=errand.model_dump())


kickoff_chat()
