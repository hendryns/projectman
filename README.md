Chatbot Asisten Manajemen Proyek
Ini adalah aplikasi chatbot sederhana yang dibangun dengan Python, Streamlit, Langchain, dan Google Gemini API. Chatbot ini dirancang untuk bertindak sebagai asisten manajemen proyek, menjawab pertanyaan, dan memberikan wawasan tentang berbagai topik manajemen proyek.

Fitur
Antarmuka chat yang interaktif dan mudah digunakan.

Didukung oleh model bahasa canggih dari Google (Gemini-Pro).

Memiliki pengetahuan dasar tentang metodologi proyek (Agile, Scrum, Waterfall), manajemen risiko, penjadwalan, dan alat-alat PM.

Menyimpan riwayat percakapan untuk konteks yang lebih baik.

Prasyarat
Python 3.8 atau lebih tinggi

Akun Google dan API Key untuk Gemini (Anda bisa mendapatkannya dari Google AI Studio)

Instalasi dan Cara Menjalankan
Clone Repositori (atau unduh file-filenya)

# Jika menggunakan git
git clone <url-repositori-anda>
cd <nama-folder-proyek>

Buat dan Aktifkan Lingkungan Virtual (Virtual Environment)
Ini adalah praktik terbaik untuk menjaga dependensi proyek tetap terisolasi.

# Membuat environment
python -m venv venv

# Mengaktifkan di Windows
.\venv\Scripts\activate

# Mengaktifkan di macOS/Linux
source venv/bin/activate

Install Dependensi
Pastikan Anda berada di direktori proyek yang berisi file requirements.txt.

pip install -r requirements.txt

Atur API Key Anda

Buat file baru bernama .env di direktori utama proyek.

Buka file .env dan tambahkan API Key Google Anda seperti berikut:

GOOGLE_API_KEY="MASUKKAN_API_KEY_ANDA_DISINI"

Ganti MASUKKAN_API_KEY_ANDA_DISINI dengan kunci API yang Anda dapatkan dari Google.

Jalankan Aplikasi Streamlit
Buka terminal Anda, pastikan Anda berada di direktori proyek, dan jalankan perintah berikut:

streamlit run app.py

Buka di Browser
Aplikasi akan secara otomatis terbuka di browser web default Anda. Jika tidak, buka URL yang ditampilkan di terminal (biasanya http://localhost:8501).

Selamat! Sekarang Anda dapat mulai berinteraksi dengan asisten manajemen proyek Anda.