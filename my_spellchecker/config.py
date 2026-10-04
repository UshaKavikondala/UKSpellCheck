MAX_CHUNK_CHARS = 1200   # about 300 tokens; tune this using your token telemetry
MAX_CHUNKS = 3           # development limit because CPU-only Ollama is slow; 0 = no limit

# Languages the detector may choose from (restricting the list makes detection more accurate)
EXPECTED_LANGUAGES = ["English", "Dutch", "Polish", "German", "French",
                      "Spanish", "Italian", "Romanian", "Turkish", "Slovak"]