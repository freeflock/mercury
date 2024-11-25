import json
import uuid

from ratatosk_errands.model import PromptTemplateInstructions

from mercury.discussant import Discussant


class GPT(Discussant):
    def __init__(self, prompt_names, question, context, discussion_length):
        self.prompt_names = prompt_names
        self.prompt_name_index = 0
        self.question = question
        self.context = context
        self.messages = []
        self.discussion_length = discussion_length
        self.identifier = str(uuid.uuid4())

    def generate_instructions(self):
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

    def add_message(self, message):
        self.messages.append(message)

    def finished(self):
        return len(self.messages) >= self.discussion_length

    def get_dialog(self):
        return self.messages

    def get_identifier(self):
        return self.identifier
