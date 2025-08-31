import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Memuat variabel lingkungan dari file .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("GOOGLE_API_KEY tidak ditemukan. Harap buat file .env dan tambahkan kunci API Anda.")

def get_pdf_text(pdf_docs):
    """
    Mengekstrak teks dari daftar file PDF yang diunggah.
    """
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    """
    Memecah teks mentah menjadi potongan-potongan (chunks) yang lebih kecil.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    """
    Membuat vector store dari potongan teks menggunakan embeddings Google GenAI.
    Menyimpan vector store secara lokal jika belum ada.
    """
    if not text_chunks:
        st.warning("Tidak ada teks untuk diproses. Silakan unggah PDF.")
        return None
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Membuat vector store baru dari dokumen
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    
    # Menyimpan vector store secara lokal
    vector_store.save_local("faiss_index")
    st.success("Vector store berhasil dibuat dan disimpan!")
    return vector_store


def get_conversational_chain():
    """
    Membuat dan mengembalikan conversational chain untuk tanya jawab.
    """
    prompt_template = """
    Jawab pertanyaan sedetail mungkin dari konteks yang diberikan. Pastikan untuk memberikan semua detailnya. Jika jawabannya tidak ada dalam konteks yang diberikan, katakan saja, "jawaban tidak tersedia dalam konteks", jangan memberikan jawaban yang salah.

    Konteks:
    {context}

    Pertanyaan:
    {question}

    Jawaban:
    """
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def user_input(user_question):
    """
    Menangani input pengguna, melakukan pencarian di vector store, dan mendapatkan respons.
    """
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        
        # Memuat vector store dari lokal
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)
        
        chain = get_conversational_chain()
        
        response = chain(
            {"input_documents": docs, "question": user_question},
            return_only_outputs=True
        )
        
        st.write("Balasan: ", response["output_text"])

    except FileNotFoundError:
        st.error("File index FAISS tidak ditemukan. Silakan unggah dan proses PDF terlebih dahulu.")
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")


def main():
    st.set_page_config(page_title="Chatbot Project Management", page_icon="🤖")
    
    st.header("Chatbot Cerdas untuk Manajemen Proyek 🤖")
    
    user_question = st.text_input("Ajukan Pertanyaan tentang Dokumen Proyek Anda")

    if user_question:
        user_input(user_question)

    with st.sidebar:
        st.title("Menu")
        st.write("Unggah dokumen PDF proyek Anda di sini dan klik tombol 'Proses' untuk memulai.")
        pdf_docs = st.file_uploader("Unggah File PDF", accept_multiple_files=True, type="pdf")
        
        if st.button("Proses"):
            if pdf_docs:
                with st.spinner("Memproses dokumen... Ini mungkin memakan waktu beberapa saat."):
                    # 1. Ekstrak teks dari PDF
                    raw_text = get_pdf_text(pdf_docs)
                    
                    # 2. Pecah teks menjadi chunks
                    text_chunks = get_text_chunks(raw_text)
                    
                    # 3. Buat dan simpan vector store
                    get_vector_store(text_chunks)
            else:
                st.warning("Harap unggah setidaknya satu file PDF.")

if __name__ == "__main__":
    main()
