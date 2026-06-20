#!/usr/bin/env python3
"""Render Brand Research Sprint markdown deliverables to PDF.

Usage:
    python3 render_pdf.py <input.md> <output.pdf> [--title "Title"] [--author "Author"]

Uses `markdown_pdf` (which wraps PyMuPDF). If the lib isn't installed, prints
install instructions and exits non-zero so the calling skill knows to fall back.

The CSS matches the visual style of the foundational docs — letter paper,
serif-free body, dense tables, blockquote highlights.
"""
import sys
import os
import argparse


CSS = """
body {
  font-family: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 10.5pt;
  line-height: 1.45;
  color: #1a1a1a;
}
h1 {
  font-size: 22pt;
  border-bottom: 2px solid #1a1a1a;
  padding-bottom: 8px;
  margin-top: 0;
}
h2 {
  font-size: 16pt;
  color: #1a1a1a;
  margin-top: 24px;
  page-break-after: avoid;
}
h3 {
  font-size: 13pt;
  color: #2a2a2a;
  margin-top: 20px;
  page-break-after: avoid;
}
h4 {
  font-size: 11.5pt;
  color: #2a2a2a;
  margin-top: 16px;
  page-break-after: avoid;
}
p { margin: 6px 0; }
ul, ol { padding-left: 22px; margin: 6px 0; }
li { margin: 3px 0; }
em { color: #2a2a2a; }
strong { color: #000; }
a { color: #06c; text-decoration: none; word-break: break-all; }
blockquote {
  border-left: 3px solid #888;
  padding: 4px 14px;
  margin: 8px 0;
  color: #555;
  font-style: italic;
}
code {
  background: #f0f0f0;
  padding: 1px 4px;
  border-radius: 3px;
  font-family: "SF Mono", Menlo, monospace;
  font-size: 0.92em;
}
pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}
hr { border: none; border-top: 1px solid #ccc; margin: 18px 0; }
table {
  border-collapse: collapse;
  margin: 10px 0;
  font-size: 9pt;
  width: 100%;
}
th, td {
  border: 1px solid #bbb;
  padding: 5px 7px;
  text-align: left;
  vertical-align: top;
}
th { background: #ececec; font-weight: 600; }
"""


def main():
    ap = argparse.ArgumentParser(description="Render markdown to PDF for brand-research-sprint deliverables.")
    ap.add_argument("input", help="Input markdown file")
    ap.add_argument("output", help="Output PDF file")
    ap.add_argument("--title", default=None, help="PDF title metadata")
    ap.add_argument("--author", default="Brand Research Sprint", help="PDF author metadata")
    ap.add_argument("--subject", default=None, help="PDF subject metadata")
    args = ap.parse_args()

    try:
        from markdown_pdf import MarkdownPdf, Section
    except ImportError:
        sys.stderr.write(
            "ERROR: markdown_pdf is not installed.\n"
            "Install it with: pip3 install markdown_pdf\n"
            "Or use the Python environment that already has it (Python 3.14 on this machine).\n"
        )
        return 2

    if not os.path.isfile(args.input):
        sys.stderr.write(f"ERROR: input file not found: {args.input}\n")
        return 3

    with open(args.input, "r", encoding="utf-8") as f:
        md = f.read()

    if not md.strip():
        sys.stderr.write(f"ERROR: input file is empty: {args.input}\n")
        return 4

    if "INCOMPLETE" in md.upper():
        sys.stderr.write(
            f"WARNING: input contains 'INCOMPLETE' marker — PDF will still be generated, but "
            f"the source file is flagged as a draft.\n"
        )

    pdf = MarkdownPdf(toc_level=2, optimize=True)
    pdf.add_section(Section(md, paper_size="Letter"), user_css=CSS)

    # Default the title to the first H1 line if not provided
    title = args.title
    if not title:
        for line in md.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
    if not title:
        title = os.path.splitext(os.path.basename(args.input))[0]

    pdf.meta["title"] = title
    pdf.meta["author"] = args.author
    if args.subject:
        pdf.meta["subject"] = args.subject

    pdf.save(args.output)
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
