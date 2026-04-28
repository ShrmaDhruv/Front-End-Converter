"""
phi3_client.py

Phi-3 3.8B client using Ollama's local REST API.
Used by the translation pipeline to generate target framework code.

Phi-3 is a completion-style model well suited for code generation tasks.
It receives a structured prompt containing the IR and target framework
instructions and returns the translated code.

Singleton pattern ensures one HTTP session is reused across calls.
Lazy import means the requests package is only required at runtime,
so unit tests work without it installed.

Prereqs:
    ollama pull phi3:3.8b
    ollama serve          # runs on localhost:11434 by default

Install:
    pip install requests
"""

MODEL_NAME   = "phi3:3.8b"
OLLAMA_URL   = "http://localhost:11434/api/chat"
TIMEOUT_SECS = 180


class Phi3Client:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def _load(self):
        if self._loaded and hasattr(self, "_session"):
            return

        import requests

        self._loaded = False

        print(f"Connecting to Ollama ({MODEL_NAME})...")

        try:
            session = requests.Session()
            probe   = session.get("http://localhost:11434", timeout=5)
            probe.raise_for_status()
            self._session = session
            self._loaded  = True
            print("Phi3 connection ready.")

        except Exception as e:
            raise RuntimeError(f"[Phi3Client] Ollama unreachable: {e}")

    def chat(
        self,
        messages:       list[dict],
        max_new_tokens: int   = 2048,
        temperature:    float = 0.1,
    ) -> str:
        self._load()

        payload = {
            "model":    MODEL_NAME,
            "messages": messages,
            "stream":   False,
            "options": {
                "num_predict": max_new_tokens,
                "temperature": temperature,
            },
        }

        try:
            response = self._session.post(
                OLLAMA_URL,
                json    = payload,
                timeout = TIMEOUT_SECS,
            )
            response.raise_for_status()

        except Exception as e:
            raise RuntimeError(f"[Phi3Client] Ollama request failed: {e}")

        return response.json()["message"]["content"].strip()

    def is_available(self) -> bool:
        try:
            import requests
            requests.get("http://localhost:11434", timeout=3).raise_for_status()
            return True
        except Exception:
            return False
