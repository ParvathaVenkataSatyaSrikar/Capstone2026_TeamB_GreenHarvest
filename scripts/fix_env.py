"""Normalize .env and remove deprecated keys."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
env_path = ROOT / ".env"
if not env_path.exists():
    print("No .env file found.")
    raise SystemExit(1)

REMOVED_KEYS = frozenset({
    "USE_OLLAMA",
    "OLLAMA_MODEL",
    "EMBEDDING_PROVIDER",
    "LANGSMITH_API_KEY",
    "LANGSMITH_PROJECT",
    "LANGCHAIN_TRACING_V2",
    "USE_PINECONE",
    "PINECONE_API_KEY",
    "PINECONE_INDEX",
    "PINECONE_DIMENSION",
})

lines_out = []
seen = set()
for line in env_path.read_text(encoding="utf-8-sig").splitlines():
    raw = line
    if "=" in line and not line.strip().startswith("#"):
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key in REMOVED_KEYS:
            print(f"Removed deprecated: {key}")
            continue
        lines_out.append(f"{key}={val}")
        seen.add(key)
    else:
        lines_out.append(raw)

defaults = [
    ("OPENAI_MODEL", "gpt-4o-mini"),
    ("OPENAI_VISION_MODEL", "gpt-4o-mini"),
    ("GEMINI_MODEL", "gemini-2.5-flash-lite"),
    ("GEMINI_VISION_MODEL", "gemini-2.5-flash-lite"),
    ("LLM_PROVIDER", "auto"),
    ("LLM_REQUEST_TIMEOUT_SEC", "45"),
    ("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001"),
    ("SKIP_LLM_INTAKE_WHEN_KEYWORDS", "true"),
]
for key, val in defaults:
    if key not in seen:
        lines_out.append(f"{key}={val}")
        print(f"Added default: {key}={val}")

env_path.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
print("Normalized .env — restart Streamlit if it is running.")
