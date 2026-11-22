import json
from pathlib import Path

REGISTRY_PATH = Path(__file__).resolve().parent.parent / "models" / "registry.json"

def load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        return {"models": []}
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
