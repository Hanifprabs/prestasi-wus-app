import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import datetime
import streamlit as st

# --- KONFIGURASI KONEKSI DATABASE (LOCAL FALLBACK) ---
# Digunakan saat menjalankan aplikasi di laptop secara lokal.
# Saat di-deploy ke Streamlit Cloud, koneksi otomatis menggunakan st.secrets.
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "db_stunting_wus"
DB_USER     = "postgres"
DB_PASSWORD = "postgres"

def get_db_connection():
    """
    Membuka koneksi ke database PostgreSQL.
    - Jika berjalan di Streamlit Cloud: membaca dari st.secrets [postgres]
    - Jika berjalan lokal: menggunakan konfigurasi hardcoded di atas
    """
    try:
        # pyrefly: ignore [missing-import]
        import streamlit as st
        cfg = st.secrets["postgres"]
        conn = psycopg2.connect(
            host=cfg["host"],
            port=cfg["port"],
            database=cfg["database"],
            user=cfg["user"],
            password=cfg["password"],
            sslmode="require"          # Neon & sebagian besar cloud PG butuh SSL
        )
    except (KeyError, FileNotFoundError, Exception):
        # Fallback ke koneksi lokal jika st.secrets tidak tersedia
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
    return conn


def init_db():
    """Membuat tabel database jika belum ada dan memperbarui (ALTER) jika ada kolom baru"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Membuat tabel dasar dengan sintaks PostgreSQL
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pasien_tb (
        id_rekam SERIAL PRIMARY KEY,
        id_pasien VARCHAR(50) NOT NULL,
        nik VARCHAR(50), 
        nama VARCHAR(100) NOT NULL,
        email VARCHAR(100),
        no_hp VARCHAR(20),
        usia INTEGER,
        alamat_kecamatan VARCHAR(100),
        lokasi_faskes VARCHAR(100),         
        jadwal_kunjungan VARCHAR(200),      
        no_antrean VARCHAR(50),     
        tanggal_pengisian VARCHAR(100),       
        pendidikan_terakhir INTEGER,
        pendapatan_bulanan INTEGER,
        akses_air_bersih INTEGER,
        akses_layanan_kesehatan INTEGER,
        skor_pengetahuan_gizi INTEGER,
        status_pemeriksaan VARCHAR(100),
        berat_badan NUMERIC(5,2),
        tinggi_badan NUMERIC(5,2),
        hb_darah NUMERIC(4,2),
        imt NUMERIC(4,2),
        lila NUMERIC(4,2),
        hasil_risiko VARCHAR(100),
        rekomendasi TEXT
    )
    """)

    # 2. Membuat tabel users_tb untuk akun Nakes & Admin
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users_tb (
        id         SERIAL PRIMARY KEY,
        username   VARCHAR(100) NOT NULL UNIQUE,
        email      VARCHAR(100) NOT NULL,
        no_hp      VARCHAR(20),
        role       VARCHAR(50)  NOT NULL,
        created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 3. FITUR ANTI-ERROR: Update skema otomatis menggunakan information_schema PostgreSQL
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'pasien_tb'
    """)
    existing_columns = [row[0] for row in cursor.fetchall()]
    
    if 'email' not in existing_columns:
        cursor.execute("ALTER TABLE pasien_tb ADD COLUMN email VARCHAR(100)")
    if 'no_hp' not in existing_columns:
        cursor.execute("ALTER TABLE pasien_tb ADD COLUMN no_hp VARCHAR(20)")
    if 'nik' not in existing_columns:
        cursor.execute("ALTER TABLE pasien_tb ADD COLUMN nik VARCHAR(50)")
        
    conn.commit()
    cursor.close()
    conn.close()


def register_new_patient(nama, email, no_hp, kecamatan, nik=""):
    """
    Fungsi khusus untuk mengeksekusi pendaftaran dari UI Pendaftaran Pasien Baru.
    Menggunakan NIK sebagai ID Pasien Utama.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    id_baru = nik 
    tgl_daftar = datetime.datetime.now().strftime("%d %B %Y - %H:%M WIB")
    
    # Mengubah placeholder ? menjadi %s untuk PostgreSQL
    cursor.execute("""
    INSERT INTO pasien_tb (
        id_pasien, nama, email, no_hp, alamat_kecamatan, nik, 
        status_pemeriksaan, tanggal_pengisian
    ) VALUES (%s, %s, %s, %s, %s, %s, 'Menunggu Pemeriksaan Fisik', %s)
    """, (id_baru, nama, email, no_hp, kecamatan, nik, tgl_daftar))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    try:
        st.cache_data.clear()
    except Exception:
        pass
        
    return id_baru

# --- FUNGSI UNTUK PASIEN LAMA ---
def insert_patient_kuesioner(data_dict):
    """Menyimpan data pendaftaran awal pasien (Legacy function)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO pasien_tb (
        id_pasien, nama, usia, alamat_kecamatan, pendidikan_terakhir, 
        pendapatan_bulanan, akses_air_bersih, akses_layanan_kesehatan, 
        skor_pengetahuan_gizi, status_pemeriksaan, hasil_risiko, rekomendasi
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data_dict['ID_Pasien'], data_dict['Nama'], data_dict['Usia'], data_dict['Alamat_Kecamatan'],
        data_dict['Pendidikan_Terakhir'], data_dict['Pendapatan_Bulanan'], data_dict['Akses_Air_Bersih'],
        data_dict['Akses_Layanan_Kesehatan'], data_dict['Skor_Pengetahuan_Gizi'], data_dict['Status_Pemeriksaan'],
        data_dict['Hasil_Risiko'], data_dict['Rekomendasi']
    ))
    conn.commit()
    cursor.close()
    conn.close()
    
    try:
        st.cache_data.clear()
    except Exception:
        pass

def get_patient_by_name(nama_pasien):
    """Mengambil riwayat medis pasien berdasarkan nama (untuk login pasien)"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("SELECT * FROM pasien_tb WHERE nama = %s", (nama_pasien,))
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return pd.DataFrame(rows) if rows else pd.DataFrame()

# --- FUNGSI UNTUK NAKES & ADMIN ---
@st.cache_data(ttl=30)
def get_all_patients():
    """Mengambil seluruh data pasien untuk ditampilkan di Dashboard Nakes/Admin (Di-cache selama 30 detik)"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("SELECT * FROM pasien_tb")
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return pd.DataFrame(rows) if rows else pd.DataFrame()

def update_patient_medical(id_pasien, medical_dict):
    """Mengupdate hasil pemeriksaan klinis nakes dan prediksi AI"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE pasien_tb SET 
        berat_badan = %s, tinggi_badan = %s, hb_darah = %s, imt = %s, lila = %s,
        status_pemeriksaan = %s, hasil_risiko = %s, rekomendasi = %s
    WHERE id_pasien = %s
    """, (
        medical_dict['Berat_Badan'], medical_dict['Tinggi_Badan'], medical_dict['Hb_Darah'],
        medical_dict['IMT'], medical_dict['LILA'], medical_dict['Status_Pemeriksaan'],
        medical_dict['Hasil_Risiko'], medical_dict['Rekomendasi'], id_pasien
    ))
    conn.commit()  
    cursor.close()
    conn.close()   
    
    try:
        st.cache_data.clear()
    except Exception:
        pass

def is_id_pasien_exists(id_pasien):
    """Mengecek apakah ID Pasien sudah terdaftar di database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM pasien_tb WHERE id_pasien = %s", (id_pasien,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()  
    return result is not None  

def generate_new_patient_id():
    """
    Menghasilkan ID Pasien unik otomatis (Fungsi Cadangan / Legacy).
    Sistem saat ini sudah menggunakan NIK, namun fungsi ini tetap dipertahankan
    jika sewaktu-waktu dibutuhkan format ID internal faskes.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    tahun_sekarang = datetime.datetime.now().year
    prefix = f"WUS-{tahun_sekarang}-"
    
    cursor.execute("SELECT id_pasien FROM pasien_tb WHERE id_pasien LIKE %s ORDER BY id_pasien DESC LIMIT 1", (prefix + '%',))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if row:
        id_terakhir = row[0]
        nomor_urut_baru = int(id_terakhir.split('-')[-1]) + 1
    else:
        nomor_urut_baru = 1
        
    id_baru = f"{prefix}{nomor_urut_baru:04d}"
    return id_baru


# --- FUNGSI UNTUK REGISTRASI & LOGIN NAKES / ADMIN ---

def register_staff(username, email, no_hp, role):
    """
    Mendaftarkan akun baru Tenaga Kesehatan atau Admin ke tabel users_tb.
    Mengembalikan True jika berhasil, False jika username sudah ada.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users_tb (username, email, no_hp, role) VALUES (%s, %s, %s, %s)",
            (username, email, no_hp, role)
        )
        conn.commit()
        try:
            st.cache_data.clear()
        except Exception:
            pass
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def get_staff_by_username(username, role):
    """
    Mengambil data staf berdasarkan username dan role dari users_tb.
    Digunakan untuk validasi login dan pengiriman OTP.
    Mengembalikan dict {username, email, no_hp, role} atau None.
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT username, email, no_hp, role FROM users_tb WHERE username = %s AND role = %s",
        (username, role)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(row) if row else None


def is_username_exists(username):
    """Mengecek apakah username sudah terdaftar di users_tb."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users_tb WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None
