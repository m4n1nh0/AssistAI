import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.domain.contracts import DocumentCreateRequest

SUPPORTED_EXTENSIONS = {".json", ".md", ".markdown", ".txt"}


def load_documents(path: str | Path) -> list[DocumentCreateRequest]:
    base_path = Path(path)
    if not base_path.exists():
        return []

    files = [base_path] if base_path.is_file() else _iter_supported_files(base_path)
    documents: list[DocumentCreateRequest] = []
    for file_path in files:
        documents.extend(_load_file(file_path))
    return documents


def _iter_supported_files(base_path: Path) -> list[Path]:
    return sorted(
        file_path
        for file_path in base_path.rglob("*")
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def _load_file(path: Path) -> list[DocumentCreateRequest]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return _load_json(path)
    if suffix in {".md", ".markdown"}:
        return _load_markdown(path)
    if suffix == ".txt":
        return [_single_document(path, path.read_text(encoding="utf-8"))]
    return []


def _load_json(path: Path) -> list[DocumentCreateRequest]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    items: list[dict[str, Any]]

    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict) and isinstance(raw.get("documents"), list):
        items = raw["documents"]
    elif isinstance(raw, dict):
        items = [raw]
    else:
        raise ValueError(f"Unsupported JSON structure in {path}.")

    documents: list[DocumentCreateRequest] = []
    for item in items:
        payload = {"source": str(path), **item}
        try:
            documents.append(DocumentCreateRequest.model_validate(payload))
        except ValidationError as exc:
            raise ValueError(f"Invalid document payload in {path}: {exc}") from exc
    return documents


def _load_markdown(path: Path) -> list[DocumentCreateRequest]:
    text = path.read_text(encoding="utf-8")
    root_title, sections = _markdown_sections(text)
    if not sections:
        return [_single_document(path, text, title=root_title)]

    category = _slug(root_title or path.stem)
    return [
        DocumentCreateRequest(
            title=section_title,
            category=category,
            content=f"{section_title}\n\n{content}",
            source=str(path),
            owner="suporte",
            sensitivity="interno",
            tags=_tags_from_title(section_title),
        )
        for section_title, content in sections
        if content.strip()
    ]


def _single_document(
    path: Path,
    content: str,
    title: str | None = None,
) -> DocumentCreateRequest:
    document_title = title or path.stem.replace("_", " ").replace("-", " ").title()
    return DocumentCreateRequest(
        title=document_title,
        category=_slug(path.stem),
        content=content.strip(),
        source=str(path),
        owner="suporte",
        sensitivity="interno",
        tags=_tags_from_title(document_title),
    )


def _markdown_sections(text: str) -> tuple[str | None, list[tuple[str, str]]]:
    root_title: str | None = None
    current_title: str | None = None
    current_lines: list[str] = []
    sections: list[tuple[str, str]] = []

    def flush() -> None:
        if current_title and current_lines:
            sections.append((current_title, "\n".join(current_lines).strip()))

    for line in text.splitlines():
        if line.startswith("# "):
            root_title = line[2:].strip()
            continue
        if line.startswith("## "):
            flush()
            current_title = line[3:].strip()
            current_lines = []
            continue
        if current_title:
            current_lines.append(line)

    flush()
    return root_title, sections


def _slug(value: str) -> str:
    return (
        value.lower()
        .replace("ç", "c")
        .replace("ã", "a")
        .replace("á", "a")
        .replace("à", "a")
        .replace("é", "e")
        .replace("ê", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ô", "o")
        .replace("õ", "o")
        .replace("ú", "u")
        .replace(" ", "-")
    )


def _tags_from_title(title: str) -> list[str]:
    words = [
        word.strip(".,:;!?()[]{}").lower()
        for word in title.replace("-", " ").split()
    ]
    return [word for word in words if len(word) > 2]
