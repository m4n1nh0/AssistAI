from app.ai.knowledge_base import SEED_DOCUMENTS


def main() -> None:
    for document in SEED_DOCUMENTS:
        print(f"{document.id} - {document.title}")


if __name__ == "__main__":
    main()
