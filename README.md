# 🌱 EcoReport

**EcoReport** adalah aplikasi web berbasis Flask yang digunakan untuk mencatat, melihat, dan mengelola laporan lingkungan secara digital. Proyek ini bertujuan untuk membantu pengguna dalam memantau data terkait pelaporan lingkungan dengan tampilan yang interaktif dan sistem autentikasi.

## 🔧 Teknologi yang Digunakan

- **Python 3.10**
- **Flask** – Web framework
- **SQLite** – Basis data lokal
- **Jinja2** – Template engine untuk HTML
- **HTML/CSS** – Tampilan antarmuka
- **Bootstrap** – Styling (jika digunakan)
- **Werkzeug** – Routing dan keamanan

## 📁 Struktur Proyek

```plaintext
EcoReport/
├── app.py                # Entry point aplikasi
├── api.py                # API endpoint (jika ada)
├── config.py             # Konfigurasi aplikasi
├── db_utils.py           # Utility untuk database
├── models.py             # Model ORM
├── templates/            # HTML templates (Jinja2)
├── static/               # File statis (CSS, JS, gambar)
├── requirements.txt      # Daftar dependensi
├── setup.py              # Setup project (opsional)
├── .gitignore
└── README.md
▶️ Cara Menjalankan Aplikasi
1. Clone repository
bash
Copy
Edit
git clone https://github.com/username/EcoReport.git
cd EcoReport
2. Buat dan aktifkan virtual environment
bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
3. Install dependensi
bash
Copy
Edit
pip install -r requirements.txt
4. Jalankan aplikasi
bash
Copy
Edit
python app.py
Aplikasi akan berjalan di: http://localhost:5000

✅ Fitur Aplikasi
 Login dan Register pengguna

 Dashboard laporan lingkungan

 Upload dan view data laporan

 API endpoint untuk laporan (opsional)

 Validasi data & autentikasi pengguna

📌 Catatan
Pastikan file .env tersedia jika kamu menggunakan variabel environment.

File .db (SQLite) tidak disertakan — buatlah database saat pertama kali aplikasi dijalankan.
