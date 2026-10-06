from src import devtools_ingest
from src.devtools_ingest import chunk_document


def test_chunks_keep_paragraph_boundaries_and_split_long_notes():
    text = "build event: compile and test\n\n" + ("release diagnostic " * 30)
    chunks = chunk_document(text, max_chars=80)
    assert chunks[0] == "build event: compile and test"
    assert len(chunks) == 9
    assert all(len(chunk) <= 80 for chunk in chunks)


def test_ingest_can_use_existing_collection_without_creating_it(monkeypatch):
    class Client:
        def create_collection(self, collection, dimension):
            raise AssertionError("must not create a collection")

        def upsert(self, collection, vectors):
            assert collection == "managed-notes"
            assert len(vectors) == 2

    monkeypatch.setattr(devtools_ingest, "embed", lambda texts: [[0.1, 0.2] for _ in texts])

    count = devtools_ingest.ingest_notes(
        Client(),
        "managed-notes",
        "doc-1",
        "first\n\nsecond",
        create_collection=False,
    )

    assert count == 2
