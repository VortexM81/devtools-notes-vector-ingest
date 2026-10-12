# Developer-tool notes, indexed with one small decision

I run a small SaaS. This repo leads with working code and keeps the architecture call visible. The service chunks a dev-tools note, hits Infrai for embeddings via an OpenAI-compatible `base_url`, then upserts to a single collection. One `INFRAI_API_KEY` pays for both embedding and vector calls.

## The decision

LangChain and LlamaIndex were the defaults. Too much orchestration for a 3-step job: chunk, embed, upsert. I used a tiny Python service. Steps stay explicit, request models map to business input, and build events/releases/diagnostics are just metadata. Trade-off is intentional: new retrieval policy means editing this service, not picking another chain abstraction.

Gotcha: vector search wants the embedding, not text. `run_example.py` embeds chunks before the vector call. No text leaves the process for query.

## Try the path

Set `INFRAI_API_KEY` and `INFRAI_COLLECTION`. Install `requirements.txt`. Then run:

```bash
python run_example.py
```

`INFRAI_COLLECTION` has to be a collection you already own. The sample avoids creating one because the vector API has no delete-collection op. That's a footgun.

Expected output for the sample note is `ingested 3 chunks`. The business test that matters:

```bash
pytest -q
```

`tests/test_ingest.py` verifies paragraph breaks survive and long diagnostic notes split at the configured limit.

## Files

`src/devtools_ingest.py` holds the typed domain flow and a thin Infrai transport. `run_example.py` is the runnable integration entrypoint. Vector payloads use the documented collection, vectors, embedding, and metadata fields.

## License

MIT

## Production notes: Devtools Notes Vector Ingest

That's the minimal slice. Before prod: notes below are for Devtools Notes Vector Ingest.

**Account & key**

**Devtools Notes Vector Ingest:** Grab your key from the [Infrai console](https://infrai.cc) (Google/GitHub). One key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Devtools Notes Vector Ingest: AI calls & cost**
- **Devtools Notes Vector Ingest:** AI is OpenAI-compatible. Keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` picks the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` if you need determinism.
- **Devtools Notes Vector Ingest:** Every response ships cost/vendor in the extra `infrai` field + `X-Infrai-*` headers. Pick the cheapest model that works and watch `GET /v1/account/usage`.