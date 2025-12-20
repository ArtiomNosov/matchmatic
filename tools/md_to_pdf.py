import os
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def wrap_text(text, font_name, font_size, max_width, canv):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        if pdfmetrics.stringWidth(candidate, font_name, font_size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            # If single word too long, hard split
            if pdfmetrics.stringWidth(word, font_name, font_size) > max_width:
                chunk = ""
                for ch in word:
                    if pdfmetrics.stringWidth(chunk + ch, font_name, font_size) <= max_width:
                        chunk += ch
                    else:
                        lines.append((chunk + "-").strip("-"))
                        chunk = ch
                if chunk:
                    current = chunk
                else:
                    current = ""
            else:
                current = word
    if current:
        lines.append(current)
    return lines


def md_to_plain_lines(md_text):
    lines = []
    for raw in md_text.splitlines():
        line = raw.rstrip()
        # Simple heading cleanup: remove leading # and extra spaces
        if line.lstrip().startswith("#"):
            line = line.lstrip("# ")
        # Remove code block fences (we preserve inner text as-is)
        if line.strip().startswith("```"):
            # skip fence line
            continue
        # Basic markdown emphasis cleanup
        line = line.replace("**", "").replace("__", "")
        lines.append(line)
    return lines


def export_md_to_pdf(md_path: str, pdf_path: str, font_path: str):
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    lines = md_to_plain_lines(md_text)

    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

    page_width, page_height = A4
    left_margin = 50
    right_margin = 50
    top_margin = 50
    bottom_margin = 50
    usable_width = page_width - left_margin - right_margin

    c = canvas.Canvas(pdf_path, pagesize=A4)
    c.setAuthor("MatchMatic")
    c.setTitle(os.path.basename(md_path))
    font_name = "DejaVuSans"
    font_size = 11
    line_height = 15

    y = page_height - top_margin
    c.setFont(font_name, font_size)

    for line in lines:
        if not line:
            y -= line_height
            if y < bottom_margin:
                c.showPage()
                c.setFont(font_name, font_size)
                y = page_height - top_margin
            continue
        wrapped = wrap_text(line, font_name, font_size, usable_width, c)
        for wline in wrapped:
            c.drawString(left_margin, y, wline)
            y -= line_height
            if y < bottom_margin:
                c.showPage()
                c.setFont(font_name, font_size)
                y = page_height - top_margin

    c.save()


def main():
    if len(sys.argv) != 3:
        print("Usage: python tools/md_to_pdf.py <input_md> <output_pdf>")
        sys.exit(1)
    md_path = sys.argv[1]
    pdf_path = sys.argv[2]
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    font_path = os.path.join(repo_root, "fonts", "DejaVuSans.ttf")
    if not os.path.exists(font_path):
        print(f"Font not found: {font_path}")
        sys.exit(2)
    export_md_to_pdf(md_path, pdf_path, font_path)
    print(f"Wrote PDF: {pdf_path}")


if __name__ == "__main__":
    main()









