import time
import uuid

import requests
from ratatosk_errands.model import PromptTemplateInstructions, Errand, Echo

from mercury.dialog import Dialog


class DiscussantDialog(Dialog):
    def __init__(self, prompt_names, question, context, discussion_length):
        self.prompt_names = prompt_names
        self.prompt_name_index = 0
        self.question = question
        self.context = context
        self.messages = []
        self.discussion_length = discussion_length
        self.identifier = str(uuid.uuid4())

    def start(self):
        errand = Errand(
            instructions=self.advance_dialog(),
            origin="mercury:33333",
            destination="mercury:33333/receive_echo",
            errand_identifier=self.get_identifier(),
            timestamp=time.time()
        )
        requests.post("http://errand_runner:33333/give_errand", json=errand.model_dump())

    def step(self, echo: Echo):
        self.messages.append(echo.reply.message)
        if not self.finished():
            errand = Errand(
                instructions=self.advance_dialog(),
                origin="mercury:33333",
                destination="mercury:33333/receive_echo",
                errand_identifier=self.get_identifier(),
                timestamp=time.time()
            )
            requests.post("http://errand_runner:33333/give_errand", json=errand.model_dump())

    def advance_dialog(self):
        dialog = ""
        for message in self.messages:
            dialog += f"\n\n*message*\n{message}"
        prompt_name = self.prompt_names[self.prompt_name_index]
        self.prompt_name_index += 1
        if self.prompt_name_index > len(self.prompt_names) - 1:
            self.prompt_name_index = 0
        return PromptTemplateInstructions(
            prompt_name=prompt_name,
            input_variables={
                "question": self.question,
                "dialog": dialog,
                "context": self.context
            }
        )

    def finished(self):
        return len(self.messages) >= self.discussion_length

    def get_dialog(self):
        return self.messages

    def get_identifier(self):
        return self.identifier
