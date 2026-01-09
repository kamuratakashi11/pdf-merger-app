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

# --- カスタムCSS（全体の色調整） ---
st.markdown("""
    <style>
    /* 1. 「結合する」ボタンなどのボタン色を緑系にする */
    div.stButton > button {
        background-color: #e8f5e9 !important; /* 背景：かなり薄い緑 */
        color: #2e7d32 !important;           /* 文字：深緑 */
        border: 1px solid #a5d6a7 !important; /* 枠線：薄い緑 */
        border-radius: 8px;
    }
    /* ボタンにマウスを乗せたときの色 */
    div.stButton > button:hover {
        background-color: #c8e6c9 !important; /* 少し濃い薄緑 */
        color: #1b5e20 !important;
        border-color: #81c784 !important;
    }

    /* 2. 左側の番号ボックスのデザイン */
    .number-box {
        background-color: #e8f5e9; /* ボタンと同じ薄緑 */
        color: #2e7d32;            /* 深緑 */
        border: 1px solid #a5d6a7;
        width: 30px;
        height: 46px; /* 右側のリストアイテムの高さに合わせる */
        display: flex;
        align-items: center;
        justify_content: center;
        border-radius: 5px;
        margin-bottom: 6px;
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
    pdf_dict = {file.name: file for file in uploaded_pdfs}
    
    if 'current_order' not in st.session_state or len(st.session_state['current_order']) != len(uploaded_pdfs):
        st.session_state['current_order'] = list(pdf_dict.keys())

    st.write("---")
    
    col_header_1, col_header_2 = st.columns([3, 1])
    with col_header_1:
        st.subheader("2. 順番の並べ替え")
        st.info("左の番号に合わせて、右の箱を並べ替えてください。")
    with col_header_2:
        # このボタンもCSSで緑色になります
        if st.button("🗑️ 最初に戻る", on_click=reset_app):
            pass

    # --- 2. ドラッグ＆ドロップ画面 ---
    col_nums, col_sort = st.columns([1, 10])
    
    with col_nums:
        # CSSで緑色にした番号ボックスを表示
        for i in range(len(st.session_state['current_order'])):
            st.markdown(f'<div class="number-box">{i+1}</div>', unsafe_allow_html=True)

    with col_sort:
        # ※注意: 右側のドラッグボックス自体の色はライブラリの制限で変更できない場合がありますが
        # 周囲のボタンや番号の色を緑に統一することで、全体の印象を和らげています。
        sorted_names = sort_items(st.session_state['current_order'], direction="vertical")

    st.session_state['current_order'] = sorted_names

    st.write("---")

    # --- 3. 結合実行ボタン ---
    # CSSで緑色になります
    if st.button("この順序で結合する"):
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
