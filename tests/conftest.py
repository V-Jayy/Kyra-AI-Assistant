import sys, types
import types as _types

sys.modules.setdefault('vosk', types.SimpleNamespace(Model=lambda *a, **k: None, KaldiRecognizer=lambda *a, **k: None))
sys.modules.setdefault('pyaudio', types.SimpleNamespace(PyAudio=lambda: None, paInt16=0))
sys.modules.setdefault('rapidfuzz', types.SimpleNamespace(fuzz=types.SimpleNamespace(partial_ratio=lambda a, b: 0)))
sys.modules.setdefault('pydantic', types.SimpleNamespace(BaseModel=object))

dummy_jsonschema = _types.ModuleType('jsonschema')
dummy_jsonschema.ValidationError = Exception
dummy_jsonschema.validate = lambda inst, schema: None
sys.modules.setdefault('jsonschema', dummy_jsonschema)

class _DummyResp:
    status_code = 200
    text = ""
    def json(self):
        return {"choices": [{}]}

dummy_requests = _types.ModuleType('requests')
dummy_requests.get = lambda *a, **k: _DummyResp()
dummy_requests.post = lambda *a, **k: _DummyResp()
dummy_requests.exceptions = _types.SimpleNamespace(RequestException=Exception)
sys.modules.setdefault('requests', dummy_requests)
sys.modules.setdefault('requests.exceptions', dummy_requests.exceptions)
