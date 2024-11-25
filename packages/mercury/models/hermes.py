from transformers import AutoTokenizer

from mercury.discussant import Discussant


class Hermes(Discussant):
    def __init__(self, system_prompt):
        self.tokenizer = AutoTokenizer.from_pretrained(
            "NousResearch/Hermes-3-Llama-3.1-70B",
            trust_remote_code=True)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "left"
        self.messages = [
            {"role": "system", "content": system_prompt},
        ]

    def generate_prompt(self):
        return self.tokenizer.apply_chat_template(self.messages, add_generation_prompt=True, tokenize=False)

    def add_message(self, message):
        self.messages.append({"role": "assistant", "content": message})
