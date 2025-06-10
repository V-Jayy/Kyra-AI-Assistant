from llama_cpp import Llama

try:
    _LLM = Llama(model_path="models/kyra-model.gguf", n_ctx=4096)
except Exception:  # pragma: no cover - optional during tests
    _LLM = None

def generate(prompt: str, temperature: float = 0.7, max_tokens: int = 256) -> str:
    """Direct, local inference.  Returns the generated text only."""
    if _LLM is None:
        return ""
    return _LLM(
        prompt,
        temperature=temperature,
        max_tokens=max_tokens
    )["choices"][0]["text"].strip()


