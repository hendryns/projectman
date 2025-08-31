import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

# Fungsi ini akan mengurus proses loading, chunking, embedding, dan storing
@st.cache_resource
def setup_rag_pipeline(api_key, pdf_file_path):
    """
    Mempersiapkan pipeline RAG dari file PDF.
    1. Muat dokumen PDF.
    2. Pecah dokumen menjadi potongan-potongan (chunking).
    3. Buat embeddings untuk setiap potongan.
    4. Simpan embeddings di dalam FAISS Vector Store.
    """
    # 1. Muat Dokumen
    loader = PyPDFLoader(pdf_file_path)
    docs = loader.load()

    # 2. Lakukan Chunking
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    text_chunks = text_splitter.split_documents(docs)

    # 3. Buat Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)

    # 4. Buat Vector Store
    vector_store = FAISS.from_documents(text_chunks, embeddings)
    
    return vector_store

def main():
    """Fungsi utama untuk menjalankan aplikasi Streamlit."""
    st.set_page_config(page_title="Chatbot Cerdas PM", page_icon="🧠")

    st.title("🧠 Chatbot Cerdas Manajemen Proyek")
    st.markdown("Tanya apa saja dari dokumen panduan manajemen proyek!")

    # Pastikan GOOGLE_API_KEY tersedia
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("GEMINI_API_KEY tidak ditemukan. Harap atur di Streamlit Secrets Anda.")
        st.stop()
    
    api_key = st.secrets["GEMINI_API_KEY"]
    
    # Ganti dengan path ke file PDF Anda. 
    # Untuk contoh ini, anggap ada file 'Panduan_Manajemen_Proyek.pdf' di direktori yang sama.
    pdf_file = "Panduan_Manajemen_Proyek.pdf" 

    if not os.path.exists(pdf_file):
        st.error(f"File '{pdf_file}' tidak ditemukan. Harap unggah file tersebut.")
        st.stop()

    # Siapkan pipeline RAG. Ini hanya akan berjalan sekali berkat @st.cache_resource
    vector_store = setup_rag_pipeline(api_key, pdf_file)

    # Siapkan LLM dan RAG Chain
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7, google_api_key=api_key)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever()
    )

    # Inisialisasi riwayat chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Tampilkan riwayat chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input dari pengguna
    if prompt := st.chat_input("Tanya dari dokumen panduan..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Mencari jawaban di dokumen..."):
                response = qa_chain.invoke(prompt)
                st.markdown(response['result'])
        
        st.session_state.messages.append({"role": "assistant", "content": response['result']})

if __name__ == "__main__":
    main()
