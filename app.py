import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# Template prompt untuk memberikan konteks pada AI
template = """
Anda adalah seorang asisten AI yang sangat ahli dalam manajemen proyek.
Tugas Anda adalah membantu pengguna dengan pertanyaan, saran, dan wawasan terkait manajemen proyek.
Jawablah pertanyaan dengan jelas, informatif, dan profesional. Anda dapat membantu dalam hal:
1.  Menjelaskan metodologi (seperti Agile, Scrum, Waterfall).
2.  Memberikan saran tentang cara mengelola risiko proyek.
3.  Memberi contoh cara membuat jadwal proyek.
4.  Menjawab pertanyaan umum tentang alat-alat manajemen proyek.

Riwayat percakapan saat ini:
{history}
Pengguna: {input}
Asisten AI:
"""

PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)

def main():
    """Fungsi utama untuk menjalankan aplikasi Streamlit."""
    st.set_page_config(page_title="Chatbot Manajemen Proyek", page_icon="🤖")

    st.title("🤖 Chatbot Asisten Manajemen Proyek")
    st.markdown("Ajukan pertanyaan apa pun tentang manajemen proyek!")

    # Inisialisasi session state jika belum ada
    if "conversation" not in st.session_state:
        # Pastikan GOOGLE_API_KEY tersedia di st.secrets
        if "GOOGLE_API_KEY" in st.secrets:
            api_key = st.secrets["GOOGLE_API_KEY"]
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7, google_api_key=api_key)
            st.session_state.conversation = ConversationChain(
                prompt=PROMPT,
                llm=llm,
                memory=ConversationBufferMemory(memory_key="history")
            )
        else:
            st.error("GOOGLE_API_KEY tidak ditemukan. Harap atur di Streamlit Secrets Anda.")
            st.info("Untuk pengembangan lokal, buat file .streamlit/secrets.toml.")
            st.stop()
            
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Tampilkan riwayat chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input dari pengguna
    if prompt := st.chat_input("Tanya sesuatu tentang manajemen proyek..."):
        # Tambahkan pesan pengguna ke riwayat dan tampilkan
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Dapatkan dan tampilkan respons dari bot
        with st.chat_message("assistant"):
            with st.spinner("Memikirkan jawaban..."):
                response = st.session_state.conversation.predict(input=prompt)
                st.markdown(response)
        
        # Tambahkan respons bot ke riwayat
        st.session_state.messages.append({"role": "assistant", "content": response})

# Blok ini memulai eksekusi program
if __name__ == "__main__":
    # PERBAIKAN: Baris 'main()' sekarang diindentasi dengan benar di dalam blok 'if'.
    # Ini menyelesaikan IndentationError.
    main()

