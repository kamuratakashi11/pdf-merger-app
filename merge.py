import streamlit as st
from pypdf import PdfWriter
import io

# 外部ライブラリ（ドラッグ＆ドロップ機能）の読み込み
try:
    from streamlit_sortables import sort_items
except ImportError:
    st.error("⚠️ 'streamlit-sortables' がインストールされていません。requirements.txt に追記してください。")
    st.stop()

# --- ページ設定 ---
st.set_page_config(page_title="PDF結合ツール", layout="centered")

st.title("📄 PDF結合ツール")
st.write("複数のPDFをアップロードし、**ドラッグ操作で直感的に**並べ替えて結合できます。")

# --- 1. ファイルアップロード ---
uploaded_pdfs = st.file_uploader(
    "結合したいPDFをすべて選んでください", 
    type=['pdf'], 
    accept_multiple_files=True
)

if uploaded_pdfs:
    # ファイル名とデータの紐付け
    pdf_dict = {file.name: file for file in uploaded_pdfs}
    original_names = list(pdf_dict.keys())

    st.write("---")
    st.subheader("2. 順番の並べ替え")
    st.info("下のリストの項目をマウスで掴んで、好きな順番に並べ替えてください。")

    # --- 2. ドラッグ＆ドロップ可能なリストを表示 ---
    # sort_items(リスト) で、並べ替え可能なリストを表示し、並べ替え後のリストを受け取る
    sorted_names = sort_items(original_names)

    st.write("---")

    # --- 3. 結合実行ボタン ---
    if st.button("並べ替えた順序で結合する"):
        merger = PdfWriter()
        try:
            progress_bar = st.progress(0)
            
            # 並べ替えられた名前(sorted_names)の順にループ処理
            for i, name in enumerate(sorted_names):
                pdf_obj = pdf_dict[name]
                merger.append(pdf_obj)
                progress_bar.progress((i + 1) / len(sorted_names))
            
            # 保存
            output_buffer = io.BytesIO()
            merger.write(output_buffer)
            merger.close()
            
            st.success("✅ 結合が完了しました！")
            
            # ダウンロード
            st.download_button(
                label="📥 結合PDFをダウンロード",
                data=output_buffer.getvalue(),
                file_name="merged_result.pdf",
                mime="application/pdf"
            )
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
