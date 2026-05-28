---
name: pdf-tools
description: Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents.
license: MIT
---

# PDF Tools

Toolkit for PDF document processing: extract text/tables, fill forms, merge/split PDFs.

## Setup

Install Python dependencies (run once):

```bash
pip install PyPDF2 pdfplumber reportlab
```

Optional for OCR:
```bash
pip install pytesseract pdf2image
```

## Usage

### Extract Text

```bash
python .pi/skills/pdf-tools/scripts/extract.py <pdf-file> --mode text
```

### Extract Tables

```bash
python .pi/skills/pdf-tools/scripts/extract.py <pdf-file> --mode tables
```

### Extract Both (Text + Tables)

```bash
python .pi/skills/pdf-tools/scripts/extract.py <pdf-file> --mode all
```

### Merge PDFs

```bash
python .pi/skills/pdf-tools/scripts/merge.py <output.pdf> <input1.pdf> <input2.pdf> ...
```

### Split PDF

```bash
python .pi/skills/pdf-tools/scripts/split.py <input.pdf> --pages 1-5,6-10
```

### Fill PDF Form

```bash
python .pi/skills/pdf-tools/scripts/fill-form.py <template.pdf> <fields.json> <output.pdf>
```

Where `fields.json` maps field names to values:
```json
{"name": "John Doe", "email": "john@example.com"}
```

## References

- [PyPDF2 Documentation](https://pypdf2.readthedocs.io/)
- [pdfplumber Documentation](https://github.com/jsvine/pdfplumber)
