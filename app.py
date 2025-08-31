import streamlit as st
import json
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# --- 1. Konfigurasi API Gemini ---
# Mengambil kunci API dari secrets Streamlit.
# Ini adalah cara paling aman untuk menyimpan kunci API saat deployment.
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Error: Kunci API 'GEMINI_API_KEY' tidak ditemukan di secrets Streamlit.")
    st.stop()

# Inisialisasi model Gemini dengan kunci API
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)

# --- 2. Prompt Engineering dengan Langchain ---
# Memberikan instruksi spesifik kepada Gemini agar hasilnya konsisten dalam format JSON.
prompt_template = """
Kamu adalah bot manajemen proyek. Identifikasi niat pengguna dari teks berikut dan ekstrak informasi penting seperti nama proyek dan nama tugas. Berikan hasilnya dalam format JSON.

Aturan output:
- Jika niatnya adalah "membuat proyek", niatnya adalah "create_project".
- Jika niatnya adalah "menambahkan tugas", niatnya adalah "add_task".
- Jika niatnya adalah "menampilkan proyek", niatnya adalah "show_projects".
- Jika tidak ada niat yang jelas, niatnya adalah "unknown".

Output harus berupa JSON valid dengan kunci "intent" dan kunci data lainnya sesuai kebutuhan.

Contoh 1:
Teks: "Buat proyek baru namanya 'Website Perusahaan'"
Hasil: {{"intent": "create_project", "project_name": "Website Perusahaan"}}

Contoh 2:
Teks: "Tambah tugas 'Desain UI' ke proyek 'Website Perusahaan'"
Hasil: {{"intent": "add_task", "task_name": "Desain UI", "project_name": "Website Perusahaan"}}

Teks: "{query}"
Hasil: 
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["query"])
llm_chain = LLMChain(prompt=prompt, llm=llm)

# --- 3. Logika Utama Aplikasi Streamlit ---
def main():
    st.title("🤖 Bot Manajemen Proyek dengan Gemini")
    st.write("Silakan ketikkan perintah kamu. Contoh: 'Buat proyek Marketing' atau 'Tambah tugas buat laporan ke proyek Marketing'.")

    # Inisialisasi data proyek
    if 'projects' not in st.session_state:
        st.session_state.projects = {}

    user_query = st.text_input("Ketikkan perintah di sini:", key="user_input")

    if st.button("Kirim"):
        if user_query:
            
try:
    # Memanggil Langchain untuk memproses query dengan Gemini
    st.info("Memproses perintah...")
    raw_response = llm_chain.run(query=user_query)
    
    # --- Solusi: Mencari dan membersihkan JSON dari respons ---
    start_index = raw_response.find('{')
    end_index = raw_response.rfind('}')
    
    if start_index != -1 and end_index != -1:
        # Ekstrak string JSON yang valid
        json_string = raw_response[start_index : end_index + 1]
        
        # Mengurai JSON dari respons Gemini
        parsed_data = json.loads(json_string)
        
        # ... (Logika pemrosesan intent yang sudah ada) ...
        intent = parsed_data.get("intent")
        
        if intent == "create_project":
            project_name = parsed_data.get("project_name")
            if project_name and project_name not in st.session_state.projects:
                st.session_state.projects[project_name] = []
                st.success(f"✅ Proyek **'{project_name}'** berhasil dibuat!")
            elif project_name:
                st.warning(f"⚠️ Proyek **'{project_name}'** sudah ada.")
            else:
                st.error("❌ Nama proyek tidak ditemukan.")

        elif intent == "add_task":
            task_name = parsed_data.get("task_name")
            project_name = parsed_data.get("project_name")
            if project_name and task_name and project_name in st.session_state.projects:
                st.session_state.projects[project_name].append(task_name)
                st.success(f"✅ Tugas **'{task_name}'** berhasil ditambahkan ke proyek **'{project_name}'**.")
            elif project_name:
                st.error(f"❌ Proyek **'{project_name}'** tidak ditemukan.")
            else:
                st.error("❌ Nama tugas atau proyek tidak ditemukan.")

        elif intent == "show_projects":
            st.success("Berikut daftar proyek kamu:")
            if st.session_state.projects:
                for project, tasks in st.session_state.projects.items():
                    st.subheader(f"📂 {project}")
                    if tasks:
                        for i, task in enumerate(tasks):
                            st.write(f"   - {i+1}. {task}")
                    else:
                        st.write("   _(Tidak ada tugas)_")
            else:
                st.write("Belum ada proyek yang dibuat.")

        else:
            st.warning("Maaf, saya tidak mengerti perintah itu.")

    else:
        st.error("❌ Respons AI tidak mengandung format JSON yang valid. Coba lagi atau periksa respons model.")
        st.write("Respons mentah (raw response) dari model:", raw_response)
        
except json.JSONDecodeError:
    st.error("❌ Terjadi kesalahan dalam mengurai respons AI. Mohon coba lagi.")
except Exception as e:
    st.error(f"❌ Terjadi kesalahan tak terduga: {e}")

    # Menampilkan status proyek saat ini untuk debugging (opsional)
    st.subheader("Status Proyek (Debugging)")
    st.json(st.session_state.projects)

if __name__ == "__main__":
    main()