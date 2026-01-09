import streamlit as st
from pypdf import PdfWriter
import io

# --- ページ設定 ---
st.set_page_config(page_title="PDF結合ツール (順序指定可)", layout="centered")

st.title("📄 PDF結合ツール")
st.write("複数のPDFをアップロードし、**好きな順番で**結合できます。")

# --- 1. ファイルアップロード ---
uploaded_pdfs = st.file_uploader(
    "結合したいPDFをすべて選んでください", 
    type=['pdf'], 
    accept_multiple_files=True
)

if uploaded_pdfs:
    # ファイル名とファイル実体（データ）を紐付ける辞書を作る
    pdf_dict = {file.name: file for file in uploaded_pdfs}
    
    # 選択されたファイル名のリストを作成
    file_names = list(pdf_dict.keys())

    st.write("---")
    st.subheader("2. 結合順序の指定")
    st.info("下のボックスで、結合したい順番にファイルを選び直したり、並べ替えたりできます（×で消して選び直せます）。")

    # --- 2. 順番指定用のセレクトボックス ---
    # デフォルトではアップロードされた順にすべて入っています
    selected_files = st.multiselect(
        "結合する順番にファイルを並べてください",
        options=file_names,
        default=file_names
    )

    st.write(f"👉 **現在の結合順序:**")
    if not selected_files:
        st.warning("結合するファイルが選択されていません。")
    else:
        for i, name in enumerate(selected_files):
            st.text(f"{i+1}. {name}")

        # --- 3. 結合実行ボタン ---
        st.write("---")
        if st.button("この順序で結合を実行する"):
            merger = PdfWriter()
            try:
                progress_bar = st.progress(0)
                
                # 指定された順序（selected_files）に従ってループする
                for i, name in enumerate(selected_files):
                    # 辞書からファイルの実体を取り出す
                    pdf_obj = pdf_dict[name]
                    merger.append(pdf_obj)
                    
                    # 進捗バー更新
                    progress_bar.progress((i + 1) / len(selected_files))
                
                # 保存
                output_buffer = io.BytesIO()
                merger.write(output_buffer)
                merger.close()
                
                st.success("✅ 結合が完了しました！")
                
                # ダウンロード
                st.download_button(
                    label="📥 結合PDFをダウンロード",
                    data=output_buffer.getvalue(),
                    file_name="ordered_merge_result.pdf",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
