#!/usr/bin/env python3
"""Extract text and/or tables from PDF files.

Usage:
    python extract.py <pdf-file> --mode [text|tables|all]
"""

import argparse
import sys


def extract_text_pypdf2(pdf_path: str) -> str:
    """Extract text using PyPDF2."""
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        return "[ERROR] PyPDF2 not installed. Run: pip install PyPDF2"

    reader = PdfReader(pdf_path)
    text_parts = []
    for i, page in enumerate(reader.pages, 1):
        page_text = page.extract_text()
        if page_text:
            text_parts.append(f"--- Page {i} ---\n{page_text}")
    return "\n\n".join(text_parts)


def extract_text_pdfplumber(pdf_path: str) -> str:
    """Extract text using pdfplumber (better quality)."""
    try:
        import pdfplumber
    except ImportError:
        return "[ERROR] pdfplumber not installed. Run: pip install pdfplumber"

    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(f"--- Page {i} ---\n{page_text}")
    return "\n\n".join(text_parts)


def extract_tables(pdf_path: str) -> str:
    """Extract tables using pdfplumber."""
    try:
        import pdfplumber
    except ImportError:
        return "[ERROR] pdfplumber not installed. Run: pip install pdfplumber"

    all_tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            if tables:
                for j, table in enumerate(tables, 1):
                    all_tables.append(f"--- Page {i}, Table {j} ---")
                    # Format as markdown table
                    if table:
                        # Header row
                        header = table[0]
                        all_tables.append("| " + " | ".join(str(c or "") for c in header) + " |")
                        all_tables.append("|" + "|".join("---" for _ in header) + "|")
                        # Data rows
                        for row in table[1:]:
                            all_tables.append("| " + " | ".join(str(c or "") for c in row) + " |")
                    all_tables.append("")
    return "\n".join(all_tables)


def main():
    parser = argparse.ArgumentParser(description="Extract content from PDF files")
    parser.add_argument("pdf_file", help="Path to the PDF file")
    parser.add_argument(
        "--mode", "-m",
        choices=["text", "tables", "all"],
        default="all",
        help="Extraction mode: text, tables, or all (default: all)",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)",
    )
    args = parser.parse_args()

    # Try pdfplumber first (better), fall back to PyPDF2
    try:
        import pdfplumber  # noqa: F401
        text_extractor = extract_text_pdfplumber
    except ImportError:
        text_extractor = extract_text_pypdf2

    output_parts = []

    if args.mode in ("text", "all"):
        text = text_extractor(args.pdf_file)
        output_parts.append(text)

    if args.mode in ("tables", "all"):
        tables = extract_tables(args.pdf_file)
        if tables:
            output_parts.append(tables)
        elif args.mode == "tables":
            output_parts.append("[INFO] No tables found in the PDF.")

    result = "\n\n".join(output_parts)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Output saved to: {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
