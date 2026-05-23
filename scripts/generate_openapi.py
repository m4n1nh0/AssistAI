from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.main import create_app


def main():
    app = create_app()
    spec = app.openapi()
    out = Path("docs")
    out.mkdir(exist_ok=True)
    (out / "openapi.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False))
    print("Wrote docs/openapi.json")


if __name__ == "__main__":
    main()
