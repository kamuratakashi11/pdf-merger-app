import streamlit as st
from pypdf import PdfWriter
import io

# 外部ライブラリ
try:
    from streamlit_sortables import sort_items
except ImportError:
    st.error("⚠️ 'streamlit-sortables' がインストールされていません。requirements.txt に追記してください。")
    st.stop()

# --- ページ設定 ---
st.set_page_config(page_title="PDF結合ツール", layout="centered")

# --- カスタムCSS（番号エリアのデザイン） ---
st.markdown("""
    <style>
    /* 番号を表示する丸い枠のデザイン */
    .number-box {
        background-color: #d4edda; /* 薄緑色 */
        color: #155724; /* 深緑色の文字 */
        width: 30px;
        height: 46px; /* 右側のボックスの高さに合わせて調整 */
        display: flex;
        align-items: center;
        justify_content: center;
        border-radius: 5px;
        margin-bottom: 6px; /* ボックス間の隙間に合わせる */
        font-weight: bold;
        font-family: sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📄 PDF結合ツール")
st.write("ファイルをアップロードし、右側のボックスをドラッグして並べ替えてください。")

# --- リセット機能 ---
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
    
    col_header_1, col_header_2 = st.columns([3, 1])
    with col_header_1:
        st.subheader("2. 順番の並べ替え")
        st.info("左の番号に合わせて、右の箱を並べ替えてください。")
    with col_header_2:
        if st.button("🗑️ 最初に戻る", on_click=reset_app):
            pass

    # --- 2. ドラッグ＆ドロップ画面 ---
    # レイアウト：左の列に番号、右の列にドラッグエリア
    col_nums, col_sort = st.columns([1, 10])
    
    with col_nums:
        # ファイルの数だけ番号を表示
        # 右側のボックスと高さを合わせるため、CSSでheightを指定したdivを作ります
        for i in range(len(st.session_state['current_order'])):
            st.markdown(f'<div class="number-box">{i+1}</div>', unsafe_allow_html=True)

    with col_sort:
        # ドラッグ可能なリスト（色は変えられませんが、機能はそのままです）
        sorted_names = sort_items(st.session_state['current_order'], direction="vertical")

    # 並べ替え結果を保存
    st.session_state['current_order'] = sorted_names

    st.write("---")

    # --- 3. 結合実行ボタン ---
    if st.button("この順序で結合する", type="primary"):
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
