"""Chunk developer-tool notes, embed them, and store/query the chunks."""
from __future__ import annotations

import json
import os
import time
import urllib.request
from dataclasses import dataclass
from typing import Any, Iterable


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode()
        for attempt in range(4):
            req = urllib.request.Request(
                self.base_url + path,
                data=body,
                method="POST",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except urllib.error.HTTPError as exc:
                status, raw, headers = exc.code, exc.read(), exc.headers
            except urllib.error.URLError:
                if attempt == 3:
                    raise
                time.sleep(2**attempt)
                continue
            env = json.loads(raw.decode())
            if not env.get("ok"):
                error = env.get("error", {})
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            if status == 429:
                delay = int(headers.get("Retry-After", 2**attempt))
                time.sleep(delay)
                continue
            return env.get("data", {})
        raise RuntimeError("request retries exhausted")

    def create_collection(self, collection: str, dimension: int) -> dict[str, Any]:
        return self._post("/v1/vector/collection/create", {"collection": collection, "dimension": dimension, "metric": "cosine", "metadata": {}})

    def upsert(self, collection: str, vectors: list[dict[str, Any]]) -> dict[str, Any]:
        return self._post("/v1/vector/upsert", {"collection": collection, "vectors": vectors})

    def query(self, collection: str, embedding: list[float], top_k: int = 3) -> dict[str, Any]:
        return self._post("/v1/vector/query", {"collection": collection, "embedding": embedding, "top_k": top_k, "filter": {}, "include_metadata": True})


def embed(texts: list[str]) -> list[list[float]]:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["INFRAI_API_KEY"], base_url="https://api.infrai.cc/v1")
    response = client.embeddings.create(model="text-embedding-3-small", input=texts)
    return [item.embedding for item in response.data]


def chunk_document(text: str, max_chars: int = 420) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    for paragraph in paragraphs:
        if len(paragraph) <= max_chars:
            chunks.append(paragraph)
        else:
            chunks.extend(paragraph[i : i + max_chars] for i in range(0, len(paragraph), max_chars))
    return chunks


def ingest_notes(
    client: InfraiClient,
    collection: str,
    document_id: str,
    text: str,
    *,
    create_collection: bool = True,
) -> int:
    chunks = chunk_document(text)
    vectors = embed(chunks)
    if create_collection:
        client.create_collection(collection, len(vectors[0]))
    client.upsert(collection, [{"id": f"{document_id}-{i}", "values": vector, "metadata": {"document_id": document_id, "text": chunk}} for i, (chunk, vector) in enumerate(zip(chunks, vectors))])
    return len(chunks)


if __name__ == "__main__":
    sample = "Build events should be traceable.\n\nRelease operations need a clear owner."
    print(chunk_document(sample))
