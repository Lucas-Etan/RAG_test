from pathlib import Path

def load_text(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"资料文件不存在：{path}") from None


def split_by_line(text: str,path: str) -> list[dict]:
    chunks = []

    for row, line in enumerate (text.splitlines()):
        line = line.strip()
        if not line:
            continue
        chunks.append({
            "id": f"chunk_{row:03d}",
            "text": line,
            "source": f"{path}"
        })

    return chunks