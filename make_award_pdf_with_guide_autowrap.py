from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A3, B4, B3
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
from PyPDF2 import PdfReader, PdfWriter
import io

PAGE_SIZES = {"A4": A4, "A3": A3, "B4": B4, "B3": B3}
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))

def make_award_pdf(
    bg_pdf_path,
    output_size,
    name,
    award_date,
    title,
    presenter,
    body_text,
    output_path,
    show_guide=False
):
    bg_reader = PdfReader(bg_pdf_path)
    bg_page = bg_reader.pages[0]
    page_width, page_height = PAGE_SIZES[output_size]

    coord = {
        "name": (page_width / 2, page_height * 0.65),
        "body_start": (page_width * 0.2, page_height * 0.52),
        "date": (page_width * 0.8, page_height * 0.22),
        "presenter": (page_width * 0.8, page_height * 0.16)
    }

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(page_width, page_height))

    can.setFont("HeiseiMin-W3", 36)
    can.drawCentredString(coord["name"][0], coord["name"][1], name)

    font_name = "HeiseiMin-W3"
    font_size = 16
    can.setFont(font_name, font_size)
    text_obj = can.beginText(coord["body_start"][0], coord["body_start"][1])
    max_width = page_width * 0.6
    wrapped_lines = simpleSplit(body_text, font_name, font_size, max_width)
    for line in wrapped_lines:
        text_obj.textLine(line)
    can.drawText(text_obj)

    can.setFont("HeiseiMin-W3", 14)
    can.drawRightString(coord["date"][0], coord["date"][1], award_date)
    can.drawRightString(coord["presenter"][0], coord["presenter"][1], f"{title}　{presenter}")

    if show_guide:
        can.setDash(3, 3)
        can.setStrokeColorRGB(1, 0, 0)
        can.setFont("Helvetica", 10)
        for label, (x, y) in coord.items():
            can.line(0, y, page_width, y)
            can.line(x, 0, x, page_height)
            can.drawString(x + 10, y + 5, f"{label} ({x:.1f}, {y:.1f})")
        can.setStrokeColorRGB(0, 0, 1)
        can.rect(0, 0, page_width, page_height, stroke=1, fill=0)
        can.drawString(20, 20, "⚙ 位置ガイド表示中（印刷時はOFFにしてください）")

    can.save()
    packet.seek(0)
    overlay_pdf = PdfReader(packet)
    writer = PdfWriter()
    bg_page.merge_page(overlay_pdf.pages[0])
    writer.add_page(bg_page)

    with open(output_path, "wb") as f_out:
        writer.write(f_out)
