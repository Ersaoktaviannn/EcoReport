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

## ▶️ Cara Menjalankan Aplikasi
1. Clone repository
```plaintext
git clone https://github.com/username/EcoReport.git
cd EcoReport
```

2. Buat dan aktifkan virtual environment
```plaintext
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install dependensi
```plaintext
pip install -r requirements.txt
```

4. Testing
```plaintext
pytest
python run_tests.py 
```

5. Jalankan aplikasi
```plaintext
python app.py
```
Aplikasi akan berjalan di: http://localhost:5000

----

📌 Catatan
Pastikan file .env tersedia jika kamu menggunakan variabel environment.

File .db (SQLite) tidak disertakan — buatlah database saat pertama kali aplikasi dijalankan.
