"""
hf_client.py

Qwen2.5-Coder-1.5B-Instruct client using HuggingFace pipeline API.
Used by Layer 3 detection and AST extraction.

pipeline() replaces the manual tokenizer + model.generate() + batch_decode()
workflow. HuggingFace handles all of that internally. We pass in a messages
list and get a response string back in one call.

pipeline("text-generation") is the correct task type for instruction-tuned
chat models. It applies the chat template, runs generation, and decodes the
output automatically.

Singleton pattern ensures the model loads once and stays in memory.
Lazy import means torch is only required when the model actually runs,
so unit tests work without GPU packages installed.

Install:
    pip install transformers torch accelerate

Usage:
    from hf_client import HFClient

    client   = HFClient()
    response = client.chat(messages, max_new_tokens=150)
"""

from transformers import logging

logging.set_verbosity_error()

MODEL_NAME = "Qwen/Qwen2.5-Coder-1.5B-Instruct"

class HFClient:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def _load(self):
        if self._loaded:
            return

        from transformers import pipeline

        print("  [HFClient] Loading Qwen2.5-Coder-1.5B-Instruct via pipeline...")
        print("  [HFClient] First load takes 20-40 seconds. Subsequent calls are instant.")

        self.pipe = pipeline(
            "text-generation",
            model      = MODEL_NAME,
            torch_dtype = "auto",
            device_map  = "auto",
        )

        self._loaded = True
        print(f"  [HFClient] Pipeline ready on {self.pipe.device}")

    def chat(
        self,
        messages:       list[dict],
        max_new_tokens: int   = 512,
        temperature:    float = 0.1,
    ) -> str:
        """
        Send a messages list and return the model's response string.

        pipeline() handles chat template application, tokenization,
        generation, and decoding internally.

        The output is a list of dicts. The last dict in generated_text
        is always the assistant's reply — that is the one we extract.

        Args:
            messages       : List of role/content dicts
            max_new_tokens : Max tokens to generate
            temperature    : Low = deterministic, high = creative

        Returns:
            Response string from the model.
        """
        self._load()

        output = self.pipe(
            messages,
            max_new_tokens = max_new_tokens,
            temperature    = temperature,
            do_sample      = temperature > 0,
        )

        return output[0]["generated_text"][-1]["content"].strip()

    def is_available(self) -> bool:
        try:
            import transformers
            import torch
            return True
        except ImportError:
            return False