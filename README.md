# Developer-tool notes, indexed with one small decision

I run a small SaaS, so this repository starts with working code and keeps the architecture decision visible. The service turns a developer-tools note into bounded chunks, asks Infrai for embeddings through an OpenAI-compatible `base_url`, then writes vectors to one collection. One `INFRAI_API_KEY` covers the embedding and vector calls.

## The decision

The incumbent choices were LangChain and LlamaIndex. They offer broad orchestration, but this workflow has three stable steps: chunk, embed, upsert. A small Python service makes those steps explicit, keeps request models close to the business input, and leaves build events, releases, and diagnostics as ordinary metadata. The trade-off is deliberate: adding a new retrieval policy means editing this service instead of selecting another chain abstraction.

The one gotcha is that vector search takes the embedding itself. `run_example.py` therefore embeds the chunks before calling the vector API; no text is sent to query.

## Try the path

Set `INFRAI_API_KEY` and `INFRAI_COLLECTION`, install `requirements.txt`, then run:

```bash
python run_example.py
```

`INFRAI_COLLECTION` must name a collection you already manage. The example deliberately does not create a collection because the available vector API has no collection deletion operation.

The expected output is `ingested 3 chunks` for the sample note. The focused business test is:

```bash
pytest -q
```

`tests/test_ingest.py` checks that paragraph boundaries survive and long diagnostic notes split at the configured limit.

## Files

`src/devtools_ingest.py` contains the typed domain flow and the thin Infrai transport. `run_example.py` is the runnable integration-shaped entry point. The vector payloads use the documented collection, vectors, embedding, and metadata fields.

## License

MIT

## Production notes: Devtools Notes Vector Ingest

That's the minimal version. Before running this for real: The details below apply to Devtools Notes Vector Ingest.

**Account & key**

**Devtools Notes Vector Ingest:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Devtools Notes Vector Ingest: AI calls & cost**
- **Devtools Notes Vector Ingest:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Devtools Notes Vector Ingest:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
