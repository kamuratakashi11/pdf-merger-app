import streamlit as st
from pypdf import PdfWriter
import io

# --- ページ設定 ---
st.set_page_config(page_title="PDF結合ツール", layout="centered")

st.title("📄 PDF結合ツール")
st.write("複数のPDFファイルをアップロードして、1つのファイルにまとめます。")

# --- ファイルアップロード ---
uploaded_pdfs = st.file_uploader(
    "結合したいPDFをすべて選んでください（ドラッグ&ドロップ可）", 
    type=['pdf'], 
    accept_multiple_files=True
)

if uploaded_pdfs:
    st.write(f"**{len(uploaded_pdfs)} 個のファイルが選択されています**")
    
    # 結合処理
    if st.button("結合を実行する"):
        merger = PdfWriter()
        try:
            # プログレスバー（進行状況）の表示
            progress_bar = st.progress(0)
            
            for i, pdf in enumerate(uploaded_pdfs):
                merger.append(pdf)
                # 進捗を更新
                progress_bar.progress((i + 1) / len(uploaded_pdfs))
            
            # メモリ上に保存するための準備
            output_buffer = io.BytesIO()
            merger.write(output_buffer)
            merger.close()
            
            st.success("✅ 結合が完了しました！")
            
            # ダウンロードボタン
            st.download_button(
                label="📥 結合されたPDFをダウンロード",
                data=output_buffer.getvalue(),
                file_name="merged_result.pdf",
                mime="application/pdf"
            )
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")