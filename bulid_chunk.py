import json

from pathlib import Path
from chunker import load_text, split_by_line

source_path = "docs/test.json"

text = load_text(source_path)

chunks = split_by_line(text, source_path)
Path("index").mkdir(exist_ok=True)

def bulid_chunks():
    Path("index/chunks.json").write_text(
        json.dumps(chunks,ensure_ascii=False,indent=2),
        encoding="utf-8"
    )