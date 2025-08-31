# 🤖 Bot Manajemen Proyek dengan Gemini & Streamlit

Aplikasi ini adalah bot manajemen proyek interaktif yang dibuat dengan **Streamlit** dan didukung oleh **Google Gemini** melalui **Langchain**. Bot ini dapat memahami perintah bahasa alami untuk membuat proyek, menambahkan tugas, dan melihat status proyek.

## Persiapan & Deployment

### 1. Dapatkan Kunci API Gemini

Daftarkan diri di Google AI Studio dan dapatkan kunci API Gemini Pro.

### 2. Atur Kunci API

Kunci API harus disimpan dengan aman. Jangan pernah meletakkannya langsung di dalam kode.

#### Untuk Uji Coba Lokal:
Buat file bernama `.streamlit/secrets.toml` di dalam direktori proyekmu. Isi file tersebut dengan baris ini:
```toml
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"