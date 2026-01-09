import streamlit as st
from pypdf import PdfWriter
import io

# 外部ライブラリ（ドラッグ＆ドロップ機能）
try:
    from streamlit_sortables import sort_items
except ImportError:
    st.error("⚠️ 'streamlit-sortables' がインストールされていません。requirements.txt に追記してください。")
    st.stop()

# --- ページ設定 ---
st.set_page_config(page_title="PDF結合ツール", layout="centered")

st.title("📄 PDF結合ツール")
st.write("複数のPDFをアップロードし、ドラッグ操作で並べ替えて結合できます。")

# --- リセット機能のキモ ---
if 'reset_count' not in st.session_state:
    st.session_state['reset_count'] = 0

def reset_app():
    st.session_state['reset_count'] += 1
    if 'current_order' in st.session_state:
        del st.session_state['current_order']

# --- 1. ファイルアップロード ---
uploaded_pdfs = st.file_uploader(
    "結合したいPDFをすべて選んでください", 
    type=['pdf'], 
    accept_multiple_files=True,
    key=f"uploader_{st.session_state['reset_count']}" 
)

if uploaded_pdfs:
    # ファイル名とデータの紐付け
    pdf_dict = {file.name: file for file in uploaded_pdfs}
    
    if 'current_order' not in st.session_state or len(st.session_state['current_order']) != len(uploaded_pdfs):
        st.session_state['current_order'] = list(pdf_dict.keys())

    st.write("---")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("2. 順番の並べ替え")
        st.info("下のリストをドラッグして並べ替えてください（縦並び）。")
    with col2:
        # 完全リセットボタン
        if st.button("🗑️ 最初に戻る", on_click=reset_app):
            pass

    # --- 2. ドラッグ＆ドロップ可能なリストを表示（★ここを変更しました） ---
    # direction="vertical" を追加することで、縦に積まれるようになります
    sorted_names = sort_items(st.session_state['current_order'], direction="vertical")

    st.write("---")

    # --- 3. 結合実行ボタン ---
    if st.button("並べ替えた順序で結合する"):
        merger = PdfWriter()
        try:
            progress_bar = st.progress(0)
            
            for i, name in enumerate(sorted_names):
                if name in pdf_dict:
                    pdf_obj = pdf_dict[name]
                    merger.append(pdf_obj)
                progress_bar.progress((i + 1) / len(sorted_names))
            
            output_buffer = io.BytesIO()
            merger.write(output_buffer)
            merger.close()
            
            st.success("✅ 結合が完了しました！")
            
            st.download_button(
                label="📥 結合PDFをダウンロード",
                data=output_buffer.getvalue(),
                file_name="merged_result.pdf",
                mime="application/pdf"
            )
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
