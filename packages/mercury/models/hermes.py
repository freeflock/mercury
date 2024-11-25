import uuid

from ratatosk_errands.model import ChatInstructions
from transformers import AutoTokenizer

from mercury.discussant import Discussant


class Hermes(Discussant):
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

    def generate_instructions(self):
        return ChatInstructions(
            prompt=self.tokenizer.apply_chat_template(self.messages, add_generation_prompt=True, tokenize=False)
        )

    def add_message(self, message):
        self.messages.append({"role": "assistant", "content": message})

    def finished(self):
        return len(self.messages) >= self.discussion_length

    def get_dialog(self):
        return self.messages

    def get_identifier(self):
        return self.identifier
