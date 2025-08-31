import streamlit as st
import os
import tempfile
import nest_asyncio

# Patch untuk mengizinkan event loop asyncio yang nested
nest_asyncio.apply()

# Import pustaka yang dibutuhkan untuk Google Gemini
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

# Menggunakan cache untuk menyimpan resource dan mencegah re-run yang mahal
@st.cache_resource
def setup_rag_pipeline(api_key, pdf_bytes):
    """
    Mempersiapkan pipeline RAG dari bytes file PDF yang diunggah menggunakan Google Gemini.
    """
    try:
        # Membuat file sementara untuk dibaca oleh PyPDFLoader
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_file_path = tmp_file.name
        
        loader = PyPDFLoader(tmp_file_path)
        docs = loader.load()
    finally:
        # Membersihkan file sementara setelah selesai dibaca
        if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
    
    # Memecah dokumen menjadi potongan-potongan teks yang lebih kecil (chunks)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    text_chunks = text_splitter.split_documents(docs)
    
    # Membuat embeddings (representasi numerik) dari teks menggunakan model Google
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
    
    # Membuat vector store menggunakan FAISS untuk pencarian cepat
    vector_store = FAISS.from_documents(text_chunks, embeddings)
    return vector_store

def main():
    """Fungsi utama untuk menjalankan aplikasi Streamlit."""
    st.set_page_config(page_title="Asisten Dokumen PDF", page_icon="📄")

    st.title("📄 Asisten Dokumen PDF")
    st.markdown("Unggah dokumen PDF Anda dan tanyakan apa saja tentang isinya.")

    # Memeriksa keberadaan GOOGLE_API_KEY di Streamlit Secrets
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("GOOGLE_API_KEY tidak ditemukan. Harap atur di Streamlit Secrets Anda.")
        st.stop()
    
    api_key = st.secrets["GOOGLE_API_KEY"]
    
    # Widget untuk mengunggah file
    uploaded_file = st.file_uploader("Pilih file PDF Anda", type="pdf")

    # Logika utama hanya berjalan jika file sudah diunggah
    if uploaded_file is not in None:
        pdf_bytes = uploaded_file.getvalue()
        vector_store = setup_rag_pipeline(api_key, pdf_bytes)

        # Menginisialisasi model bahasa (LLM) dari Google Gemini
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.7, google_api_key=api_key)

        # Membuat RAG chain dengan tipe "refine" untuk menghindari error rate limit
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="refine",
            retriever=vector_store.as_ retriever(search_kwargs={"k": 8})
        )

        # Inisialisasi riwayat chat jika belum ada
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Menampilkan riwayat chat
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Menerima input dari pengguna
        if prompt := st.chat_input(f"Tanya tentang {uploaded_file.name}..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Menampilkan respons dari asisten
            with st.chat_message("assistant"):
                with st.spinner("Menganalisis dokumen secara mendalam..."):
                    response = qa_chain.invoke(prompt)
                    st.markdown(response['result'])
            
            # Menyimpan respons asisten ke riwayat chat
            st.session_state.messages.append({"role": "assistant", "content": response['result']})

if __name__ == "__main__":
    main()

