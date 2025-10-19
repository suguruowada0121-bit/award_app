import streamlit as st
import io, zipfile, pandas as pd
from make_award_pdf_with_guide_autowrap import make_award_pdf

st.title("🏅 表彰状PDF作成ツール")

bg_pdf = st.file_uploader("背景PDFを選択", type=["pdf"])
csv_file = st.file_uploader("CSVを選択", type=["csv"])

if st.button("生成開始"):
    if not bg_pdf or not csv_file:
        st.warning("ファイルを選択してください。")
    else:
        df = pd.read_csv(csv_file)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for _, row in df.iterrows():
                pdf_buffer = io.BytesIO()
                make_award_pdf(
                    bg_pdf_path=bg_pdf,  # 修正: BytesIO対応
                    output_size=row["出力サイズ"],
                    name=row["名前"],
                    award_date="2025年10月10日",
                    title="代表取締役社長",
                    presenter="山田太郎",
                    body_text="あなたは業務において優秀な成果をおさめ…",
                    output_path=pdf_buffer,  # 修正: ファイルパスでなくBytesIO
                    show_guide=False
                )
                zipf.writestr(f"{row['名前']}_表彰状.pdf", pdf_buffer.getvalue())

        st.download_button(
            "📦 ZIPをダウンロード",
            data=zip_buffer.getvalue(),
            file_name="awards.zip",
            mime="application/zip"
        )
