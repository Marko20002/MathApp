import pdfplumber
import json
import argparse
from pathlib import Path


def pdf_to_json(pdf_path: str, json_path: str | None = None):
    pdf_path = Path(pdf_path)

    if json_path is None:
        out_dir = Path("jason")
        out_dir.mkdir(exist_ok=True)
        json_path = out_dir / (pdf_path.stem + ".json")
    else:
        json_path = Path(json_path)

    data = {
        "file_name": pdf_path.name,
        "file_path": str(pdf_path),
        "pages": []
    }

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            raw_lines = text.splitlines()
            paragraphs = []
            current = []

            for line in raw_lines:
                if line.strip() == "":
                    if current:
                        paragraphs.append(" ".join(current).strip())
                        current = []
                else:
                    current.append(line.strip())

            if current:
                paragraphs.append(" ".join(current).strip())

            data["pages"].append({
                "page_number": i,
                "text": text,
                "paragraphs": paragraphs
            })

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Готово! JSON снимен во: {json_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf")
    parser.add_argument("-o", "--output")

    args = parser.parse_args()
    pdf_to_json(args.pdf, args.output)


if __name__ == "__main__":
    main()