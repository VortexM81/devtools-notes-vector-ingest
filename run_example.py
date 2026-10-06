import os

from src.devtools_ingest import InfraiClient, ingest_notes


def main() -> None:
    client = InfraiClient()
    collection = os.environ["INFRAI_COLLECTION"]
    count = ingest_notes(
        client,
        collection=collection,
        document_id="release-adr-001",
        text="Build events are recorded with their commit.\n\nRelease operations publish a version and owner.\n\nDiagnostics stay close to the developer workflow.",
        create_collection=False,
    )
    print(f"ingested {count} chunks")


if __name__ == "__main__":
    main()
