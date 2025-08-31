import streamlit as st
import os
import tempfile
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

# Menggunakan cache untuk menyimpan resource dan mencegah re-run yang mahal
@st.cache_resource
def setup_rag_pipeline(api_key, pdf_bytes):
    """
    Mempersiapkan pipeline RAG dari bytes file PDF yang diunggah.
    Proses ini (membuat vector store) mahal, jadi kita cache hasilnya.
    Kunci cache didasarkan pada file_bytes, jadi jika file yang sama diunggah lagi,
    proses ini akan dilewati dan hasil cache akan digunakan.
    """
    try:
        # Membuat file sementara dari bytes yang diunggah untuk dibaca oleh PyPDFLoader
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_file_path = tmp_file.name

        # 1. Muat Dokumen dari path file sementara
        loader = PyPDFLoader(tmp_file_path)
        docs = loader.load()

    finally:
        # Pastikan file sementara selalu dihapus
        if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
    
    # 2. Lakukan Chunking (memecah teks)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    text_chunks = text_splitter.split_documents(docs)

    # 3. Buat Embeddings (mengubah teks menjadi vektor angka)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)

    # 4. Buat Vector Store dari chunk dan embeddings
    vector_store = FAISS.from_documents(text_chunks, embeddings)
    
    return vector_store

def main():
    """Fungsi utama untuk menjalankan aplikasi Streamlit."""
    st.set_page_config(page_title="Asisten Dokumen PDF", page_icon="📄")

    st.title("📄 Asisten Dokumen PDF")
    st.markdown("Unggah dokumen PDF Anda dan tanyakan apa saja tentang isinya.")

    # Pastikan GOOGLE_API_KEY tersedia
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("GEMINI_API_KEY tidak ditemukan. Harap atur di Streamlit Secrets Anda.")
        st.stop()
    
    api_key = st.secrets["GEMINI_API_KEY"]
    
    # 1. Widget untuk mengunggah file
    uploaded_file = st.file_uploader("Pilih file PDF Anda", type="pdf")

    # Kode di bawah ini hanya akan berjalan SETELAH pengguna mengunggah file
    if uploaded_file is not None:
        # Dapatkan bytes dari file yang diunggah
        pdf_bytes = uploaded_file.getvalue()

        # Siapkan pipeline RAG. Ini akan menggunakan cache jika file yang sama diunggah lagi.
        vector_store = setup_rag_pipeline(api_key, pdf_bytes)

        # Siapkan LLM dan RAG Chain
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7, google_api_key=api_key)
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever()
        )

        # Inisialisasi riwayat chat jika belum ada
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Tampilkan riwayat chat
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Input dari pengguna
        if prompt := st.chat_input(f"Tanya tentang {uploaded_file.name}..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Menganalisis dokumen dan mencari jawaban..."):
                    response = qa_chain.invoke(prompt)
                    st.markdown(response['result'])
            
            st.session_state.messages.append({"role": "assistant", "content": response['result']})

if __name__ == "__main__":
    main()
