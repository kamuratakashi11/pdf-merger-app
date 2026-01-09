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

# --- カスタムCSS（デザイン調整） ---
# ここで色や番号の見た目を指定しています
st.markdown("""
    <style>
    /* ソート可能なリストアイテムのスタイル */
    .sortable-item {
        background-color: #d4edda !important; /* 薄緑色 */
        color: #155724 !important; /* 文字色は深緑 */
        border: 1px solid #c3e6cb !important;
        border-radius: 5px;
        margin-bottom: 5px;
        padding: 10px;
        font-family: monospace; /* 等幅フォントで見やすく */
    }
    /* リスト（ol）の番号を表示させるための設定 */
    div[data-testid="stVerticalBlock"] > div > div > div > div {
        counter-reset: sortable-counter;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📄 PDF結合ツール")
st.write("ファイルをアップロードし、ドラッグして並べ替えてください。")

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
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("2. 順番の並べ替え")
        st.info("下のリストをドラッグして並べ替えてください。")
    with col2:
        if st.button("🗑️ 最初に戻る", on_click=reset_app):
            pass

    # --- 2. ファイル名の装飾（番号と長さの視覚化） ---
    # 表示用に「1. ファイル名 ■■■...」のような文字列を作ってリストに渡します
    display_items = []
    
    # 元の順序リストを使って、表示用テキストを作成
    original_order = st.session_state['current_order']
    
    # ユーザーに見せるための工夫（番号をつける）
    # ※ sort_items自体は文字列しか扱えないため、ここで加工します
    # ただし、並べ替え後に元のファイル名に戻す処理が必要になります
    
    # 今回はシンプルに、sort_itemsの機能で並べ替えさせます。
    # 色（薄緑）は上のCSSで適用されます。
    
    sorted_items = sort_items(original_order, direction="vertical")

    # 並べ替え結果をセッションに保存（次回描画時用）
    st.session_state['current_order'] = sorted_items

    # ユーザーへのフィードバック（番号付きでプレビュー表示）
    st.write("👇 **現在の結合順序（確定イメージ）:**")
    for idx, name in enumerate(sorted_items):
        # ファイル名の長さに応じたバーを表示する工夫
        # 全角文字が含まれると長さ計算がズレますが、簡易的に文字数でバーを作ります
        bar_length = min(len(name), 20) # 最大20文字分まで
        bar = "🟩" * int(bar_length / 2) # バーの見た目
        
        st.text(f"{idx + 1}. {name}  {bar}")

    st.write("---")

    # --- 3. 結合実行ボタン ---
    if st.button("並べ替えた順序で結合する"):
        merger = PdfWriter()
        try:
            progress_bar = st.progress(0)
            
            for i, name in enumerate(sorted_items):
                if name in pdf_dict:
                    pdf_obj = pdf_dict[name]
                    merger.append(pdf_obj)
                progress_bar.progress((i + 1) / len(sorted_items))
            
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
