import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class PhiMiniModel:
    def __init__(self):
        self.model_id = "microsoft/phi-2"

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_id,
            trust_remote_code=True
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=torch.float32,
            device_map="cpu",
            trust_remote_code=True
        )

    def rewrite(self, text: str) -> str:
        prompt = f"""You are an English editor.

The input text is ALREADY IN ENGLISH.
Rewrite it into clear, natural English.

Rules:
- Do NOT translate languages
- Do NOT explain
- Do NOT add examples
- Output ONE sentence only

Text:
{text}

Clean English:
"""

        inputs = self.tokenizer(prompt, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=60,
                do_sample=False,
                temperature=0.0,
                eos_token_id=self.tokenizer.eos_token_id
            )

        decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract only rewritten sentence
        return decoded.split("Clean English:")[-1].strip()


# -----------------------------
# Singleton
# -----------------------------
_phi_model = None


def get_phi_model():
    global _phi_model
    if _phi_model is None:
        _phi_model = PhiMiniModel()
    return _phi_model
