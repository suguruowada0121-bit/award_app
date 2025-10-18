# create_award_app_zip.py
import os
import zipfile

# === プロジェクトディレクトリ作成 ===
project_dir = r"C:\02_賞状"#"award_app"
os.makedirs(project_dir, exist_ok=True)

# --- award_app.py ---
award_app_code = """\
import streamlit as st
import tempfile
import os
import pandas as pd
import shutil
from make_award_pdf_with_guide_autowrap import make_award_pdf

st.set_page_config(page_title="表彰状作成ツール", page_icon="🏅", layout="centered")

st.title("🏅 表彰状PDF作成ツール")
st.write("背景PDFとCSVをアップロードして、複数の表彰状を自動生成します。")

bg_pdf = st.file_uploader("背景PDFファイルを選択", type=["pdf"])
csv_file = st.file_uploader("CSVファイルを選択（出力サイズ・名前の列）", type=["csv"])

award_date = st.text_input("表彰日付", "2025年10月10日")
title = st.text_input("表彰者肩書", "代表取締役社長")
presenter = st.text_input("表彰者名", "山田 太郎")

body_text = st.text_area(
    "本文",
    "あなたは業務において優秀な成果をおさめ、"
    "他の模範となりました。よってここにその功績を称え表彰します。",
    height=150
)

show_guide = st.checkbox("ガイド表示（位置確認用）", value=False)

st.markdown("---")

if st.button("📄 表彰状PDFを生成"):
    if not bg_pdf or not csv_file:
        st.warning("背景PDFとCSVを両方アップロードしてください。")
    else:
        with st.spinner("PDFを作成中..."):
            df = pd.read_csv(csv_file)
            out_dir = tempfile.mkdtemp()

            bg_path = os.path.join(out_dir, "background.pdf")
            with open(bg_path, "wb") as f:
                f.write(bg_pdf.getvalue())

            for i, row in df.iterrows():
                size = row["出力サイズ"]
                name = row["名前"]
                output_path = os.path.join(out_dir, f"{name}_表彰状.pdf")

                make_award_pdf(
                    bg_pdf_path=bg_path,
                    output_size=size,
                    name=name,
                    award_date=award_date,
                    title=title,
                    presenter=presenter,
                    body_text=body_text,
                    output_path=output_path,
                    show_guide=show_guide
                )

            zip_path = os.path.join(out_dir, "awards.zip")
            shutil.make_archive(zip_path.replace(".zip", ""), "zip", out_dir)

            with open(zip_path, "rb") as f:
                st.success("✅ 表彰状の作成が完了しました。")
                st.download_button("📥 ZIPをダウンロード", f, file_name="awards.zip")
"""

# --- make_award_pdf_with_guide_autowrap.py ---
pdf_module_code = """\
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
"""

# --- requirements.txt ---
requirements_text = """\
streamlit
reportlab
PyPDF2
pandas
"""

# --- sample_award_list.csv ---
csv_text = "出力サイズ,名前\nA4,佐藤 花子\nB4,鈴木 一郎\nA4,田中 太一\n"

# --- ダミー背景PDF ---
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

dummy_bg_path = os.path.join(project_dir, "background.pdf")
c = canvas.Canvas(dummy_bg_path, pagesize=A4)
c.setFont("Helvetica", 24)
c.drawCentredString(300, 400, "（背景デザインサンプル）")
c.save()

# === ファイル生成 ===
files = {
    "award_app.py": award_app_code,
    "make_award_pdf_with_guide_autowrap.py": pdf_module_code,
    "requirements.txt": requirements_text,
    "sample_award_list.csv": csv_text,
}

for filename, content in files.items():
    with open(os.path.join(project_dir, filename), "w", encoding="utf-8") as f:
        f.write(content)

# === ZIP化 ===
zip_filename = "award_app_project.zip"
with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(project_dir):
        for file in files:
            path = os.path.join(root, file)
            zipf.write(path, os.path.relpath(path, os.path.dirname(project_dir)))

print(f"✅ プロジェクトZIPを作成しました → {zip_filename}")
print("このZIPをGitHubにアップロードし、Streamlit Cloudで 'award_app/award_app.py' を指定すれば公開可能です。")
