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
