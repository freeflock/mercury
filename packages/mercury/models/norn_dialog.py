import time
import uuid

import requests
from ratatosk_errands.model import ChatInstructions, Echo, Errand
from transformers import AutoTokenizer

from mercury.dialog import Dialog


class NornDialog(Dialog):
    def __init__(self, discussion_length):
        self.tokenizer = AutoTokenizer.from_pretrained(
            "NousResearch/Hermes-3-Llama-3.1-70B",
            trust_remote_code=True)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "left"
        self.messages = [
            {"role": "system", "content": "hermes trismegistus"},
        ]
        self.discussion_length = discussion_length
        self.identifier = str(uuid.uuid4())

    def start(self):
        errand = Errand(
            instructions=ChatInstructions(
                prompt=self.tokenizer.apply_chat_template(self.messages, add_generation_prompt=True, tokenize=False)
            ),
            origin="mercury:33333",
            destination="mercury:33333/receive_echo",
            errand_identifier=self.get_identifier(),
            timestamp=time.time()
        )
        requests.post("http://errand_runner:33333/give_errand", json=errand.model_dump())

    def step(self, echo: Echo):
        self.messages.append({"role": "assistant", "content": echo.reply.message})
        if not self.finished():
            errand = Errand(
                instructions=ChatInstructions(
                    prompt=self.tokenizer.apply_chat_template(self.messages, add_generation_prompt=True, tokenize=False)
                ),
                origin="mercury:33333",
                destination="mercury:33333/receive_echo",
                errand_identifier=self.get_identifier(),
                timestamp=time.time()
            )
            requests.post("http://errand_runner:33333/give_errand", json=errand.model_dump())

    def finished(self):
        return len(self.messages) >= self.discussion_length

    def get_dialog(self):
        return self.messages

    def get_identifier(self):
        return self.identifier
