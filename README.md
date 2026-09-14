# ⛰️ Pendakian Lawu — Sistem Tabungan Pendakian

Website untuk **mencatat dan memantau tabungan peserta pendakian**.  
Bukan untuk menerima pembayaran langsung — semua catatan tabungan diverifikasi secara manual oleh Admin.

---

## 🗂️ Fitur

| Fitur | Admin | User |
|---|:---:|:---:|
| Login dengan username & password | ✅ | ✅ |
| Dashboard ringkasan tabungan | ✅ (semua peserta) | ✅ (milik sendiri) |
| Tambah / edit / nonaktifkan akun peserta | ✅ | ❌ |
| Set target tabungan per peserta | ✅ | ❌ |
| Catat tabungan baru | ❌ | ✅ |
| Verifikasi (setuju / tolak) tabungan peserta | ✅ | ❌ |
| Riwayat tabungan | ✅ (semua) | ✅ (milik sendiri) |
| Kelola informasi pendakian | ✅ | ❌ |
| Kelola rute / itinerary | ✅ | ❌ |
| Lihat info & rute pendakian | ❌ | ✅ |

---

## 🏗️ Struktur Proyek

```
Pendakian-Lawu/
├── run.py                    # Entry point
├── requirements.txt
├── instance/
│   └── pendakian.db          # SQLite database (dibuat otomatis)
└── app/
    ├── __init__.py           # App factory + security middleware
    ├── database.py           # SQLAlchemy instance + seed
    ├── models.py             # User, Savings, ClimbingInfo, RouteItem
    ├── decorators.py         # login_required, admin_required, user_required
    ├── routes/
    │   ├── auth.py           # /login, /logout
    │   ├── admin.py          # /admin/...
    │   └── user.py           # /user/...
    ├── static/
    │   ├── css/style.css     # Design system lengkap
    │   └── js/main.js        # Interaktivitas global
    └── templates/
        ├── base.html         # Layout utama (sidebar + topbar)
        ├── login.html
        ├── 403.html / 404.html / 500.html
        ├── admin/            # Semua halaman Admin
        └── user/             # Semua halaman User
```

---

## 🚀 Cara Menjalankan

### 1. Prasyarat
Pastikan **Python 3.10+** sudah terinstall.

### 2. Clone / buka folder proyek
```bash
cd Pendakian-Lawu
```

### 3. Buat virtual environment (disarankan)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependensi
```bash
pip install -r requirements.txt
```

### 5. Jalankan server
```bash
python run.py
```

Buka browser → **http://localhost:5000**

---

## 🔐 Akun Default

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |

> ⚠️ **Ganti password admin** segera setelah pertama kali login melalui fitur edit peserta, atau ubah langsung di `app/database.py` sebelum deploy.

---

## 📖 Alur Penggunaan

### Admin
1. Login dengan akun admin
2. Tambah peserta baru di menu **Peserta** → set username, password, dan target tabungan
3. Bagikan username & password kepada masing-masing peserta
4. Tambah informasi pendakian di menu **Info Pendakian**
5. Setiap ada tabungan masuk → verifikasi di menu **Verifikasi Tabungan**

### User (Peserta)
1. Login dengan username & password dari Admin
2. Lihat progress tabungan di **Dashboard**
3. Catat tabungan baru di menu **Catat Tabungan**
4. Pantau status (menunggu / disetujui / ditolak) di **Riwayat Tabungan**
5. Lihat informasi dan rute pendakian di menu **Pendakian**

---

## 🛠️ Tech Stack

| Layer | Teknologi |
|-------|-----------|
| Frontend | HTML5 · CSS3 · Vanilla JavaScript |
| Template engine | Jinja2 (via Flask) |
| Backend | Python 3 · Flask 3 |
| ORM | SQLAlchemy (Flask-SQLAlchemy) |
| Database | SQLite |
| Auth | Session-based (Werkzeug password hashing) |

---

## 🔒 Keamanan

- Password di-hash menggunakan `werkzeug.security.generate_password_hash` (PBKDF2/SHA-256)
- Session cookie: `HttpOnly`, `SameSite=Lax`, expired 8 jam
- Security headers: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, dll.
- Decorator `@admin_required` / `@user_required` di setiap route
- `before_request` memvalidasi sesi masih valid setiap request
- User tidak bisa mengakses data peserta lain — query selalu difilter dengan `user_id = session['user_id']`

---

## 📝 Catatan Pengembangan

- Database SQLite tersimpan di `instance/pendakian.db` (dibuat otomatis saat pertama kali jalan)
- Untuk reset database, hapus file `instance/pendakian.db` lalu restart server
- Untuk production, ganti `SECRET_KEY` via environment variable:
  ```bash
  export SECRET_KEY="kunci-rahasia-panjang-anda"
  ```
- Untuk production juga disarankan migrasi ke PostgreSQL dengan mengubah `SQLALCHEMY_DATABASE_URI`
