import json
import os
import urllib.request
import urllib.error

import numpy as np
from dotenv import load_dotenv

load_dotenv()

def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"缺少必需的环境变量 {name}，请检查 .env 文件")
    return value

OLLAMA_BASE_URL = _require_env("OLLAMA_BASE_URL").rstrip("/")
EMBED_MODEL = _require_env("EMBED_MODEL")

#文本向量化
def _embed_one(text: str) ->list[float]:
    payload = {"model": EMBED_MODEL, "input": text}

    request = urllib.request.Request(
        f"{OLLAMA_BASE_URL}/api/embed",
        data = json.dumps(payload).encode("utf-8"),
        headers = {"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        # 服务返回了 4xx / 5xx，比如模型不存在、请求格式错
        raise RuntimeError(f"Ollama 返回错误 {e.code}: {e.reason}") from e
    except urllib.error.URLError as e:
        # 连不上，比如 Ollama 没启动、代理没配好
        raise RuntimeError(f"无法连接 Ollama 服务: {e.reason}") from e
    except json.JSONDecodeError as e:
        # 返回的不是合法 JSON
        raise RuntimeError(f"Ollama 响应不是合法 JSON: {e}") from e

    return data["embeddings"][0]

#向量归一化
def embed_text(text: str) -> list[float]:
    vec = np.array(_embed_one(text), dtype=np.float32)
    norm = np.linalg.norm(vec)

    if norm == 0:
        raise ValueError("embedding 返回了零向量，无法归一化")
    vec = vec / norm

    return vec.tolist()

def cosine(a: list, b: list) -> float:
    a_arr = np.array(a)
    b_arr = np.array(b)

    denom = np.linalg.norm(a_arr)*np.linalg.norm(b_arr)

    if denom == 0:
        return 0.0
    return float(np.dot(a_arr, b_arr) / denom)

if __name__ == "__main__":
    vec = embed_text("这个项目是干什么的")
    print("维度:", len(vec))
    print("前 5 个值:", vec[:5])
    print("norm:", float(np.linalg.norm(np.asarray(vec, dtype=np.float32))))
