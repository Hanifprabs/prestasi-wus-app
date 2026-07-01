# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
import random  

# ==========================================
# 1. KONFIGURASI UTAMA STREAMLIT (WAJIB BARIS PERTAMA)
# ==========================================
st.set_page_config(
    page_title="PRESTASI-WUS",
    page_icon="🩺",
    layout="wide",  # Mengunci mode desktop layar lebar agar layout tidak terlipat vertikal
    initial_sidebar_state="expanded"
)

import urllib.parse
from modules.database import init_db, generate_new_patient_id, register_new_patient, get_db_connection, register_staff, get_staff_by_username, is_username_exists

# Jalankan inisialisasi database PostgreSQL hanya sekali saat aplikasi pertama kali dinyalakan
if 'db_initialized' not in st.session_state:
    init_db()
    st.session_state['db_initialized'] = True

# PERHATIAN: Pastikan mengimpor dashboard edukasi dari file yang baru kita buat
from modules.ui_components import inject_modern_css
from modules.dashboard_edukasi import show_education_dashboard

from modules.model_ai import init_ai_and_database, train_model
from modules.auth import init_auth_session, check_credentials, login_user, logout_user, send_id_to_email, send_otp_staff_email, KODE_REGISTRASI_NAKES, KODE_REGISTRASI_ADMIN

from roles.pasien import show_patient_main_menu, show_patient_history
from roles.nakes import show_nakes_main_menu, show_nakes_history_dashboard
from roles.admin import show_admin_model_menu, show_admin_database_menu, show_admin_evaluation_menu

# Jalankan Inisialisasi Gaya Visual & Struktur Data Global
inject_modern_css()
init_auth_session()
init_ai_and_database()

# Pastikan Model Inteligensi Buatan Sudah Terlatih Saat Start-up
if 'ai_model' not in st.session_state:
    train_model()

# ==========================================
# 🌟 FITUR BARU: ANTI-LOGOUT SAAT BROWSER DI-REFRESH (F5)
# ==========================================
# Sistem akan mengecek URL browser. Jika ada token sesi, pulihkan status login!
if "session_role" in st.query_params:
    st.session_state['logged_in'] = True
    st.session_state['role'] = st.query_params["session_role"]
    st.session_state['username'] = st.query_params.get("session_user", "User")
    if "session_pid" in st.query_params:
        st.session_state['patient_id'] = st.query_params["session_pid"]

# ==========================================
# 2. SISTEM ROUTER KONDISI STATE & URL PARAMETER
# ==========================================
# Inisialisasi state halaman login jika belum ada
if 'tampilkan_login' not in st.session_state:
    st.session_state['tampilkan_login'] = False

# Cek apakah ada parameter "?action=login" di URL browser dari tombol HTML
if "action" in st.query_params:
    if st.query_params["action"] == "login":
        st.session_state['tampilkan_login'] = True
        del st.query_params["action"]  # Bersihkan parameter action saja, jangan .clear() semua agar token tidak hilang
        st.rerun()  # Paksa muat ulang halaman


# ==========================================
# 3. FUNGSI MENU EDIT PROFIL PASIEN 
# ==========================================
def show_patient_profile_menu():
    st.markdown("""
<div style="margin-bottom: 1.5rem;">
<h2 style='color:#0f172a; font-weight: 800; margin-bottom: 0.2rem; margin-top: 0;'>👤 Profil & Pengaturan</h2>
<p style='color:#64748b; font-size: 0.95rem; margin-top: 0;'>Perbarui data kontak dan domisili Anda agar sistem tetap terhubung.</p>
</div>
    """, unsafe_allow_html=True)

    id_pasien = st.session_state.get('patient_id')
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nama, email, no_hp, alamat_kecamatan FROM pasien_tb WHERE id_pasien = %s", (id_pasien,))
        row = cursor.fetchone()
        df_user = pd.DataFrame([row], columns=['nama', 'email', 'no_hp', 'alamat_kecamatan']) if row else pd.DataFrame()
        
        if not df_user.empty:
            curr_nama = df_user['nama'].iloc[0] or ""
            curr_email = df_user['email'].iloc[0] or ""
            curr_hp = df_user['no_hp'].iloc[0] or ""
            curr_kec = df_user['alamat_kecamatan'].iloc[0] or ""
        else:
            curr_nama, curr_email, curr_hp, curr_kec = "", "", "", ""
            
        with st.container(border=True):
            with st.form("form_edit_profil"):
                st.text_input("Nama Lengkap (Sesuai KTP)", value=curr_nama, disabled=True, help="Nama terikat dengan rekam medis. Hubungi petugas faskes jika ada kesalahan nama.")
                
                col1, col2 = st.columns(2)
                with col1:
                    email_baru = st.text_input("Alamat Email Aktif", value=curr_email)
                with col2:
                    hp_baru = st.text_input("Nomor WhatsApp Aktif", value=curr_hp)
                    
                list_kec = ["Banjarsari", "Jebres", "Laweyan", "Pasar Kliwon", "Serengan"]
                idx_kec = list_kec.index(curr_kec) if curr_kec in list_kec else 0
                kec_baru = st.selectbox("Kecamatan Tinggal", list_kec, index=idx_kec)
                
                st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                submit_edit = st.form_submit_button("💾 Simpan Perubahan Profil", type="primary", use_container_width=True)
                
                if submit_edit:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE pasien_tb SET email = %s, no_hp = %s, alamat_kecamatan = %s WHERE id_pasien = %s", (email_baru, hp_baru, kec_baru, id_pasien))
                    conn.commit()
                    st.success("Data profil berhasil diperbarui! Silakan lihat perubahan di Menu Sidebar.")
                    st.rerun()
        conn.close()
    except Exception as e:
        st.error(f"Gagal memuat data profil: {e}")


# ==========================================
# 4. INTERFACE PANEL FORM LOGIN & DAFTAR
# ==========================================
def render_login():
    if 'login_role_active' not in st.session_state:
        st.session_state['login_role_active'] = "Pasien"
        
    if 'login_otp_step' not in st.session_state:
        st.session_state['login_otp_step'] = "input_credentials"
    if 'temp_otp' not in st.session_state:
        st.session_state['temp_otp'] = None
    if 'temp_user' not in st.session_state:
        st.session_state['temp_user'] = None

    _, center_column, _ = st.columns([1, 1.6, 1])
    
    with center_column:
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        
        # --- LOGO & HEADER ---
        st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
<div style="background-color: #006c49; width: 56px; height: 56px; border-radius: 16px; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; box-shadow: 0 10px 15px -3px rgba(0, 108, 73, 0.2);">
<span class="material-symbols-outlined" style="color: white; font-size: 2rem; font-variation-settings: 'FILL' 1;">psychology</span>
</div>
<h1 style="font-size: 2.2rem; font-weight: 800; color: #006c49; margin: 0 0 0.25rem 0; letter-spacing: -0.025em;">PRESTASI-WUS</h1>
<p style="font-size: 1rem; color: #475569; margin: 0; font-weight: 500;">Prediksi Risiko Stunting asistensi Wanita Usia Subur</p>
</div>
        """, unsafe_allow_html=True)
        
        st.markdown("<p style='text-align:center; font-size:0.9rem; font-weight:600; color:#475569; margin-bottom:1rem;'>Pilih Peran Anda</p>", unsafe_allow_html=True)
        
        role_sekarang = st.session_state['login_role_active']
        col_p1, col_p2, col_p3 = st.columns(3)
        
        with col_p1:
            if st.button("🙋‍♀️ Pasien WUS", key="btn_pill_pasien", use_container_width=True, type="primary" if role_sekarang == "Pasien" else "secondary"):
                st.session_state['login_role_active'] = "Pasien"
                st.rerun()
                
        with col_p2:
            if st.button("🩺 Nakes", key="btn_pill_nakes", use_container_width=True, type="primary" if role_sekarang == "Tenaga Kesehatan" else "secondary"):
                st.session_state['login_role_active'] = "Tenaga Kesehatan"
                st.rerun()
                
        with col_p3:
            if st.button("🛡️ Admin", key="btn_pill_admin", use_container_width=True, type="primary" if role_sekarang == "Admin" else "secondary"):
                st.session_state['login_role_active'] = "Admin"
                st.rerun()
        
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

        if role_sekarang == "Pasien":
            if 'radio_index' not in st.session_state:
                st.session_state['radio_index'] = 0

            status_akun = st.radio(
                "Pilih Status Anda:",
                ["Sudah Punya Akun", "Belum Punya Akun (Daftar Baru)"],
                horizontal=True,
                index=st.session_state['radio_index'],
                key="radio_status_pasien",
                label_visibility="collapsed"
            )
            
            if status_akun == "Sudah Punya Akun":
                st.session_state['radio_index'] = 0
                
                if st.session_state['login_otp_step'] == "input_credentials":
                    with st.form("form_login_pasien"):
                        st.markdown("<p class='form-label-text'>Nama Lengkap Anda (Sesuai KTP)</p>", unsafe_allow_html=True)
                        nama_login = st.text_input("Nama KTP", placeholder="Masukkan nama lengkap Anda", label_visibility="collapsed")
                        
                        st.markdown("<p class='form-label-text'>Nomor Induk Kependudukan (NIK KTP)</p>", unsafe_allow_html=True)
                        nik_login = st.text_input("NIK KTP", placeholder="Masukkan 16 digit NIK Anda", max_chars=16, label_visibility="collapsed")
                        
                        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                        submit_otp = st.form_submit_button("Minta Kode OTP via Email 📩", use_container_width=True)
                        
                        if submit_otp:
                            nama_bersih = nama_login.strip() if nama_login else ""
                            nik_bersih = nik_login.strip() if nik_login else ""
                            
                            if nama_bersih and len(nik_bersih) == 16:
                                try:
                                    conn = get_db_connection()
                                    cursor = conn.cursor()
                                    cursor.execute("SELECT id_pasien, email, nama FROM pasien_tb WHERE LOWER(nama) = LOWER(%s) AND nik = %s", (nama_bersih, nik_bersih))
                                    row_user = cursor.fetchone()
                                    conn.close()
                                    
                                    if row_user:
                                        id_p_db, email_db, nama_db = row_user[0], row_user[1], row_user[2]
                                        
                                        otp_acak = str(random.randint(1000, 9999))
                                        
                                        with st.spinner("Menghubungkan ke secure mail server & mengirim OTP..."):
                                            send_id_to_email(email_db, nama_db, f"KODE OTP LOGIN DIGIMIND ANDA: {otp_acak}")
                                        
                                        st.session_state['temp_otp'] = otp_acak
                                        st.session_state['temp_user'] = {
                                            'id_pasien': id_p_db,
                                            'nama': nama_db,
                                            'email': email_db
                                        }
                                        st.session_state['login_otp_step'] = "verify_otp"
                                        st.rerun()
                                    else:
                                        st.error("Kombinasi Nama Lengkap atau NIK salah / tidak ditemukan. Silakan registrasi terlebih dahulu.")
                                except Exception as e:
                                    st.error(f"Gagal memvalidasi database: {e}. Pastikan Anda telah menyimpan pembaruan di file database.py.")
                            else:
                                st.warning("Nama Lengkap wajib diisi dan NIK harus berjumlah tepat 16 digit!")
                                
                elif st.session_state['login_otp_step'] == "verify_otp":
                    user_data = st.session_state['temp_user']
                    email_raw = user_data['email']
                    email_masked = email_raw[:3] + "***" + email_raw[email_raw.find("@"):] if "@" in email_raw else email_raw
                    
                    st.success(f"📧 Kode OTP keamanan telah berhasil dikirimkan ke email `{email_masked}`. Silakan periksa kotak masuk atau folder spam email Anda.")
                    
                    with st.form("form_verifikasi_otp"):
                        st.markdown("<p class='form-label-text'>Masukkan 4-Digit Kode OTP</p>", unsafe_allow_html=True)
                        otp_input = st.text_input("Kode OTP", placeholder="Masukkan 4 angka sandi", max_chars=4, label_visibility="collapsed")
                        
                        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                        submit_verify = st.form_submit_button("Verifikasi & Masuk Ke Sistem ➔", use_container_width=True)
                        
                        if submit_verify:
                            if otp_input.strip() == st.session_state['temp_otp']:
                                p_id = user_data['id_pasien']
                                p_nama = user_data['nama']
                                
                                st.session_state['login_otp_step'] = "input_credentials"
                                st.session_state['temp_otp'] = None
                                st.session_state['temp_user'] = None
                                
                                st.session_state['patient_id'] = p_id
                                login_user(p_nama, "Pasien")
                                
                                # --- PENYIMPANAN TOKEN DI URL AGAR ANTI LOGOUT SAAT REFRESH ---
                                st.query_params["session_role"] = "Pasien"
                                st.query_params["session_user"] = p_nama
                                st.query_params["session_pid"] = p_id
                                # --------------------------------------------------------------
                                
                                st.rerun()
                            else:
                                st.error("Kode OTP salah. Silakan periksa kembali email Anda.")
                                
                    if st.button("⬅️ Batalkan & Ganti Akun Nama/NIK", use_container_width=True):
                        st.session_state['login_otp_step'] = "input_credentials"
                        st.session_state['temp_otp'] = None
                        st.session_state['temp_user'] = None
                        st.rerun()
            else:
                # --- FORM REGISTRASI AKUN BARU ---
                with st.form("form_registrasi_pasien"):
                    st.markdown("<p class='form-label-text'>Nama Lengkap (Sesuai KTP)</p>", unsafe_allow_html=True)
                    nama_daftar = st.text_input("RegNama", placeholder="Contoh: Siti Aminah", label_visibility="collapsed")
                    
                    st.markdown("<p class='form-label-text'>Nomor Induk Kependudukan (NIK KTP 16 Digit)</p>", unsafe_allow_html=True)
                    nik_daftar = st.text_input("RegNIK", placeholder="Contoh: 337201XXXXXXXXXX", max_chars=16, label_visibility="collapsed")
                    
                    st.markdown("<p class='form-label-text'>Alamat Email Aktif</p>", unsafe_allow_html=True)
                    email_daftar = st.text_input("RegEmail", placeholder="Contoh: sitiaminah@gmail.com", label_visibility="collapsed")
                    
                    st.markdown("<p class='form-label-text'>Nomor WhatsApp Aktif</p>", unsafe_allow_html=True)
                    no_hp_daftar = st.text_input("RegWA", placeholder="Contoh: 08123456789", label_visibility="collapsed")
                    
                    st.markdown("<p class='form-label-text'>Wilayah Kecamatan Tinggal (Kota Surakarta)</p>", unsafe_allow_html=True)
                    kecamatan_daftar = st.selectbox(
                        "RegKec",
                        ["Banjarsari", "Jebres", "Laweyan", "Pasar Kliwon", "Serengan"],
                        index=None,
                        placeholder="Pilih Kecamatan Tempat Tinggal...",
                        label_visibility="collapsed"
                    )
                    
                    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                    submit_daftar = st.form_submit_button("DAFTAR SEKARANG", use_container_width=True)
                    
                    if submit_daftar:
                        nama_d = nama_daftar.strip() if nama_daftar else ""
                        nik_d = nik_daftar.strip() if nik_daftar else ""
                        email_d = email_daftar.strip() if email_daftar else ""
                        hp_d = no_hp_daftar.strip() if no_hp_daftar else ""
                        
                        if nama_d and len(nik_d) == 16 and email_d and hp_d and kecamatan_daftar:
                            
                            # ========================================================
                            # 🌟 TAMBAHAN: VALIDASI ANTI DUPLIKASI NIK 
                            # ========================================================
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("SELECT COUNT(*) FROM pasien_tb WHERE nik = %s", (nik_d,))
                            nik_sudah_ada = cursor.fetchone()[0] > 0
                            conn.close()
                            
                            if nik_sudah_ada:
                                st.error("⚠️ Pendaftaran Gagal: NIK yang Anda masukkan sudah terdaftar di dalam sistem! Silakan gunakan akun yang sudah ada atau periksa kembali NIK Anda.")
                            else:
                                id_baru = register_new_patient(
                                    nama=nama_d,
                                    email=email_d,
                                    no_hp=hp_d,
                                    kecamatan=kecamatan_daftar,
                                    nik=nik_d  
                                )
                                
                                with st.spinner("Memproses kode akun dan mengirimkan ID ke email Anda..."):
                                    email_sent = send_id_to_email(email_d, nama_d, id_baru)
                                
                                if email_sent:
                                    st.session_state['notif_sukses'] = f"🎉 Pendaftaran Berhasil! ID Akun Anda: **{id_baru}**. Gunakan Nama & NIK Anda untuk meminta OTP saat masuk."
                                else:
                                    st.session_state['notif_sukses'] = f"🎉 Pendaftaran Berhasil! ID Akun Anda: **{id_baru}**."
                                
                                st.session_state['radio_index'] = 0
                                st.rerun()
                        else:
                            st.error("Semua data wajib diisi secara lengkap, dan pastikan NIK valid berjumlah 16 digit!")

        elif role_sekarang == "Tenaga Kesehatan":
            # ---- RADIO STATUS AKUN NAKES ----
            if 'nakes_radio_index' not in st.session_state:
                st.session_state['nakes_radio_index'] = 0

            status_nakes = st.radio(
                "Status Akun Nakes:",
                ["Sudah Punya Akun", "Belum Punya Akun (Daftar Baru)"],
                horizontal=True,
                index=st.session_state['nakes_radio_index'],
                key="radio_status_nakes",
                label_visibility="collapsed"
            )

            if status_nakes == "Sudah Punya Akun":
                st.session_state['nakes_radio_index'] = 0

                if st.session_state['nakes_otp_step'] == "input_credentials":
                    with st.form("form_login_nakes"):
                        st.markdown("<p class='form-label-text'>Username / NIP Petugas</p>", unsafe_allow_html=True)
                        username_nakes = st.text_input("NIP Nakes", placeholder="Masukkan username yang didaftarkan", label_visibility="collapsed")
                        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                        submit_nakes = st.form_submit_button("Minta Kode OTP via Email 📩", use_container_width=True)

                        if submit_nakes:
                            uname = username_nakes.strip()
                            if uname:
                                staf = get_staff_by_username(uname, "Tenaga Kesehatan")
                                if staf:
                                    otp = str(random.randint(1000, 9999))
                                    with st.spinner("Mengirim OTP ke email Anda..."):
                                        send_otp_staff_email(staf['email'], staf['username'], otp, "Tenaga Kesehatan")
                                    st.session_state['temp_nakes_otp'] = otp
                                    st.session_state['temp_nakes_user'] = staf
                                    st.session_state['nakes_otp_step'] = "verify_otp"
                                    st.rerun()
                                else:
                                    st.error("Username tidak ditemukan. Silakan daftar terlebih dahulu.")
                            else:
                                st.warning("Username wajib diisi!")

                elif st.session_state['nakes_otp_step'] == "verify_otp":
                    nakes_data = st.session_state['temp_nakes_user']
                    email_raw  = nakes_data['email']
                    email_mask = email_raw[:3] + "***" + email_raw[email_raw.find("@"):] if "@" in email_raw else email_raw
                    st.success(f"📧 Kode OTP dikirim ke `{email_mask}`. Periksa kotak masuk atau folder spam Anda.")

                    with st.form("form_verifikasi_otp_nakes"):
                        st.markdown("<p class='form-label-text'>Masukkan 4-Digit Kode OTP</p>", unsafe_allow_html=True)
                        otp_input = st.text_input("OTP Nakes", placeholder="Masukkan 4 angka kode OTP", max_chars=4, label_visibility="collapsed")
                        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                        submit_verify = st.form_submit_button("Verifikasi & Masuk Ke Sistem ➔", use_container_width=True)

                        if submit_verify:
                            if otp_input.strip() == st.session_state['temp_nakes_otp']:
                                uname = nakes_data['username']
                                st.session_state['nakes_otp_step'] = "input_credentials"
                                st.session_state['temp_nakes_otp'] = None
                                st.session_state['temp_nakes_user'] = None
                                login_user(uname, "Tenaga Kesehatan")
                                st.query_params["session_role"] = "Tenaga Kesehatan"
                                st.query_params["session_user"] = uname
                                st.rerun()
                            else:
                                st.error("Kode OTP salah. Silakan periksa kembali email Anda.")

                    if st.button("⬅️ Batalkan & Ganti Username", use_container_width=True):
                        st.session_state['nakes_otp_step'] = "input_credentials"
                        st.session_state['temp_nakes_otp'] = None
                        st.session_state['temp_nakes_user'] = None
                        st.rerun()

            else:
                # ---- FORM REGISTRASI NAKES ----
                with st.form("form_registrasi_nakes"):
                    st.markdown("<p class='form-label-text'>Username / NIP Petugas</p>", unsafe_allow_html=True)
                    reg_username = st.text_input("RegUserNakes", placeholder="Buat username unik Anda", label_visibility="collapsed")

                    st.markdown("<p class='form-label-text'>Alamat Email Aktif</p>", unsafe_allow_html=True)
                    reg_email = st.text_input("RegEmailNakes", placeholder="Contoh: petugas@puskesmas.go.id", label_visibility="collapsed")

                    st.markdown("<p class='form-label-text'>Nomor WhatsApp Aktif</p>", unsafe_allow_html=True)
                    reg_hp = st.text_input("RegHPNakes", placeholder="Contoh: 08123456789", label_visibility="collapsed")

                    st.markdown("<p class='form-label-text'>Kode Registrasi Khusus Nakes</p>", unsafe_allow_html=True)
                    reg_kode = st.text_input("RegKodeNakes", placeholder="Masukkan kode yang diberikan admin sistem", type="password", label_visibility="collapsed")

                    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                    submit_reg = st.form_submit_button("DAFTAR SEBAGAI NAKES", use_container_width=True)

                    if submit_reg:
                        u = reg_username.strip()
                        e = reg_email.strip()
                        h = reg_hp.strip()
                        k = reg_kode.strip()

                        if not (u and e and h and k):
                            st.error("Semua kolom wajib diisi!")
                        elif k != KODE_REGISTRASI_NAKES:
                            st.error("❌ Kode registrasi salah. Hubungi administrator sistem.")
                        elif is_username_exists(u):
                            st.error("⚠️ Username sudah terdaftar. Silakan gunakan username lain.")
                        else:
                            ok = register_staff(u, e, h, "Tenaga Kesehatan")
                            if ok:
                                st.session_state['nakes_radio_index'] = 0
                                st.success(f"🎉 Akun Nakes **{u}** berhasil didaftarkan! Silakan login menggunakan username Anda.")
                                st.rerun()
                            else:
                                st.error("Pendaftaran gagal. Coba lagi.")

        elif role_sekarang == "Admin":
            # ---- RADIO STATUS AKUN ADMIN ----
            if 'admin_radio_index' not in st.session_state:
                st.session_state['admin_radio_index'] = 0

            status_admin = st.radio(
                "Status Akun Admin:",
                ["Sudah Punya Akun", "Belum Punya Akun (Daftar Baru)"],
                horizontal=True,
                index=st.session_state['admin_radio_index'],
                key="radio_status_admin",
                label_visibility="collapsed"
            )

            if status_admin == "Sudah Punya Akun":
                st.session_state['admin_radio_index'] = 0

                if st.session_state['admin_otp_step'] == "input_credentials":
                    with st.form("form_login_admin"):
                        st.markdown("<p class='form-label-text'>Username Admin</p>", unsafe_allow_html=True)
                        username_admin = st.text_input("UserAdmin", placeholder="Masukkan username admin", label_visibility="collapsed")
                        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                        submit_admin = st.form_submit_button("Minta Kode OTP via Email 📩", use_container_width=True)

                        if submit_admin:
                            uname = username_admin.strip()
                            if uname:
                                staf = get_staff_by_username(uname, "Admin")
                                if staf:
                                    otp = str(random.randint(1000, 9999))
                                    with st.spinner("Mengirim OTP ke email Anda..."):
                                        send_otp_staff_email(staf['email'], staf['username'], otp, "Admin")
                                    st.session_state['temp_admin_otp'] = otp
                                    st.session_state['temp_admin_user'] = staf
                                    st.session_state['admin_otp_step'] = "verify_otp"
                                    st.rerun()
                                else:
                                    st.error("Username tidak ditemukan. Silakan daftar terlebih dahulu.")
                            else:
                                st.warning("Username wajib diisi!")

                elif st.session_state['admin_otp_step'] == "verify_otp":
                    admin_data = st.session_state['temp_admin_user']
                    email_raw  = admin_data['email']
                    email_mask = email_raw[:3] + "***" + email_raw[email_raw.find("@"):] if "@" in email_raw else email_raw
                    st.success(f"📧 Kode OTP dikirim ke `{email_mask}`. Periksa kotak masuk atau folder spam Anda.")

                    with st.form("form_verifikasi_otp_admin"):
                        st.markdown("<p class='form-label-text'>Masukkan 4-Digit Kode OTP</p>", unsafe_allow_html=True)
                        otp_input = st.text_input("OTP Admin", placeholder="Masukkan 4 angka kode OTP", max_chars=4, label_visibility="collapsed")
                        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                        submit_verify = st.form_submit_button("Verifikasi & Masuk Ke Sistem ➔", use_container_width=True)

                        if submit_verify:
                            if otp_input.strip() == st.session_state['temp_admin_otp']:
                                uname = admin_data['username']
                                st.session_state['admin_otp_step'] = "input_credentials"
                                st.session_state['temp_admin_otp'] = None
                                st.session_state['temp_admin_user'] = None
                                login_user(uname, "Admin")
                                st.query_params["session_role"] = "Admin"
                                st.query_params["session_user"] = uname
                                st.rerun()
                            else:
                                st.error("Kode OTP salah. Silakan periksa kembali email Anda.")

                    if st.button("⬅️ Batalkan & Ganti Username", use_container_width=True):
                        st.session_state['admin_otp_step'] = "input_credentials"
                        st.session_state['temp_admin_otp'] = None
                        st.session_state['temp_admin_user'] = None
                        st.rerun()

            else:
                # ---- FORM REGISTRASI ADMIN ----
                with st.form("form_registrasi_admin"):
                    st.markdown("<p class='form-label-text'>Username Admin</p>", unsafe_allow_html=True)
                    reg_username = st.text_input("RegUserAdmin", placeholder="Buat username admin", label_visibility="collapsed")

                    st.markdown("<p class='form-label-text'>Alamat Email Aktif</p>", unsafe_allow_html=True)
                    reg_email = st.text_input("RegEmailAdmin", placeholder="Contoh: admin@dinas.go.id", label_visibility="collapsed")

                    st.markdown("<p class='form-label-text'>Nomor WhatsApp Aktif</p>", unsafe_allow_html=True)
                    reg_hp = st.text_input("RegHPAdmin", placeholder="Contoh: 08123456789", label_visibility="collapsed")

                    st.markdown("<p class='form-label-text'>Kode Registrasi Khusus Admin</p>", unsafe_allow_html=True)
                    reg_kode = st.text_input("RegKodeAdmin", placeholder="Masukkan kode otoritas admin sistem", type="password", label_visibility="collapsed")

                    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                    submit_reg = st.form_submit_button("DAFTAR SEBAGAI ADMIN", use_container_width=True)

                    if submit_reg:
                        u = reg_username.strip()
                        e = reg_email.strip()
                        h = reg_hp.strip()
                        k = reg_kode.strip()

                        if not (u and e and h and k):
                            st.error("Semua kolom wajib diisi!")
                        elif k != KODE_REGISTRASI_ADMIN:
                            st.error("❌ Kode registrasi salah. Hubungi administrator sistem.")
                        elif is_username_exists(u):
                            st.error("⚠️ Username sudah terdaftar. Silakan gunakan username lain.")
                        else:
                            ok = register_staff(u, e, h, "Admin")
                            if ok:
                                st.session_state['admin_radio_index'] = 0
                                st.success(f"🎉 Akun Admin **{u}** berhasil didaftarkan! Silakan login menggunakan username Anda.")
                                st.rerun()
                            else:
                                st.error("Pendaftaran gagal. Coba lagi.")
        
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        if st.button("⬅️ Kembali ke Beranda Utama", use_container_width=True):
            st.session_state['tampilkan_login'] = False
            st.rerun()
            
        st.markdown("""
<p style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 2.5rem; line-height: 1.5;">
© 2026 DigiMind. Didukung oleh Tenaga Kesehatan Profesional untuk<br>pencegahan stunting berkelanjutan di Indonesia.
</p>
        """, unsafe_allow_html=True)
        
# ==========================================
# 5. CONTROLLER KONDISI UTAMA (LOGGED IN CHECK)
# ==========================================
if not st.session_state.get('logged_in', False):
    if st.session_state['tampilkan_login']:
        if 'notif_sukses' in st.session_state:
            st.success(st.session_state['notif_sukses'])
            del st.session_state['notif_sukses'] 
        render_login()
    else:
        show_education_dashboard()
else:
    username_display = st.session_state.get('username', 'USER').upper()
    role_user = st.session_state.get('role', 'Pasien')
    id_pasien = st.session_state.get('patient_id', 'Belum Terdaftar')

    from modules.ui_components import inject_modern_css
    inject_modern_css()

    st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 10px; padding: 0.5rem; margin-bottom: 1.5rem;">
<div style="background-color: #006c49; width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
<span class="material-symbols-outlined" style="color: white; font-size: 1.4rem; font-variation-settings: 'FILL' 1;">psychology</span>
</div>
<div>
<h3 style="color: white; margin: 0; font-size: 1.15rem; font-weight: 800; letter-spacing: -0.025em;">PRESTASI-WUS</h3>
<p style="color: #a7f3d0; margin: 0; font-size: 0.7rem; font-weight: 600; text-transform: uppercase;">Healthcare Portal</p>
</div>
</div>
""", unsafe_allow_html=True)

    # SIDEBAR PROFILE INFO CARD (EXPANDER DROPDOWN TAB)
    if role_user == "Pasien":
        alamat_pasien = "-"
        nohp_pasien = "-"
        email_pasien = "-"
        
        try:
            conn = get_db_connection()
            cursor_sb = conn.cursor()
            cursor_sb.execute("SELECT alamat_kecamatan, no_hp, email FROM pasien_tb WHERE id_pasien = %s", (id_pasien,))
            row_sb = cursor_sb.fetchone()
            df_user = pd.DataFrame([row_sb], columns=['alamat_kecamatan', 'no_hp', 'email']) if row_sb else pd.DataFrame()
            conn.close()
            
            if not df_user.empty:
                alamat_pasien = df_user['alamat_kecamatan'].iloc[0] or "-"
                nohp_pasien = df_user['no_hp'].iloc[0] or "-"
                email_pasien = df_user['email'].iloc[0] or "-"
        except Exception as e:
            pass 

        st.sidebar.markdown(f"""
<div style="background-color: rgba(255, 255, 255, 0.1); padding: 1.2rem; border-radius: 12px; margin-bottom: 1.5rem; border: 1px solid rgba(255, 255, 255, 0.15);">
<p style="font-size: 0.75rem; margin-bottom: 0.2rem; font-weight: 700; color: #cbd5e1; letter-spacing: 0.5px;">PENGGUNA AKTIF</p>
<h3 style="margin-top: 0px; margin-bottom: 0.2rem; color: #ffffff; font-size: 1.3rem; font-weight: 800; text-transform: uppercase;">{username_display}</h3>
<p style="margin: 0px; font-size: 0.9rem; color: #e2e8f0; font-weight: 500;">Role: Pasien</p>
<p style="margin: 5px 0px 0px 0px; font-size: 0.9rem; font-weight: 700; color: #ffffff;">ID / NIK: {id_pasien}</p>
<details style="margin-top: 15px; cursor: pointer;">
<summary style="font-size: 0.8rem; font-weight: 600; color: #a7f3d0; outline: none;">🔍 Lihat Detail Kontak</summary>
<div style="margin-top: 10px; display: flex; flex-direction: column; gap: 8px; padding-top: 10px; border-top: 1px dashed rgba(255, 255, 255, 0.2);">
<div style="display: flex; align-items: center; gap: 8px;">
<span style="font-size: 0.9rem;">📍</span>
<span style="font-size: 0.8rem; color: #e2e8f0; line-height: 1.2;">Kec. {alamat_pasien}</span>
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<span style="font-size: 0.9rem;">📞</span>
<span style="font-size: 0.8rem; color: #e2e8f0; line-height: 1.2;">{nohp_pasien}</span>
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<span style="font-size: 0.9rem;">✉️</span>
<span style="font-size: 0.8rem; color: #e2e8f0; line-height: 1.2; word-break: break-all;">{email_pasien}</span>
</div>
</div>
</details>
</div>
""", unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"""
<div style="background: rgba(255, 255, 255, 0.06); padding: 1rem; border-radius: 16px; margin-bottom: 1.5rem; border: 1px solid rgba(255,255,255,0.05);">
<p style="margin: 0; color: #94a3b8; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.05em;">PENGGUNA AKTIF</p>
<p style="margin: 3px 0 0 0; color: white; font-size: 0.95rem; font-weight: 700; line-height: 1.2;">{username_display}</p>
<p style="margin: 2px 0 0 0; color: #10b981; font-size: 0.8rem; font-weight: 600;">Role: {role_user}</p>
</div>
""", unsafe_allow_html=True)
    
    st.sidebar.markdown("<p style='font-size:0.8rem; font-weight:700; color:#94a3b8; margin-bottom:0.5rem; letter-spacing:0.05em;'>📂 NAVIGASI PANEL</p>", unsafe_allow_html=True)
    
    if 'menu_internal_active' not in st.session_state:
        st.session_state['menu_internal_active'] = "Dashboard"

    # 3. NAVIGASI TOMBOL KOTAK BERDASARKAN HIERARKI AKSES
    if role_user == "Pasien":
        b1 = st.sidebar.button("📊 Dashboard", type="primary" if st.session_state['menu_internal_active'] == 'Dashboard' else "secondary", use_container_width=True)
        if b1: st.session_state['menu_internal_active'] = "Dashboard"; st.rerun()
        
        b2 = st.sidebar.button("📋 Layanan Utama", type="primary" if st.session_state['menu_internal_active'] == 'Layanan Utama' else "secondary", use_container_width=True)
        if b2: st.session_state['menu_internal_active'] = "Layanan Utama"; st.rerun()
        
        b3 = st.sidebar.button("🩺 Riwayat Medis", type="primary" if st.session_state['menu_internal_active'] == 'Riwayat Medis' else "secondary", use_container_width=True)
        if b3: st.session_state['menu_internal_active'] = "Riwayat Medis"; st.rerun()

        b4 = st.sidebar.button("👤 Profil Saya", type="primary" if st.session_state['menu_internal_active'] == 'Profil Saya' else "secondary", use_container_width=True)
        if b4: st.session_state['menu_internal_active'] = "Profil Saya"; st.rerun()

    elif role_user == "Admin":
        b1 = st.sidebar.button("📊 Dashboard", type="primary" if st.session_state['menu_internal_active'] == 'Dashboard' else "secondary", use_container_width=True)
        if b1: st.session_state['menu_internal_active'] = "Dashboard"; st.rerun()

        b2 = st.sidebar.button("📈 Evaluasi Model AI", type="primary" if st.session_state['menu_internal_active'] == 'Evaluasi Model AI' else "secondary", use_container_width=True)
        if b2: st.session_state['menu_internal_active'] = "Evaluasi Model AI"; st.rerun()
        
        b3 = st.sidebar.button("⚙️ Retraining Model AI", type="primary" if st.session_state['menu_internal_active'] == 'Retraining Model AI' else "secondary", use_container_width=True)
        if b3: st.session_state['menu_internal_active'] = "Retraining Model AI"; st.rerun()
        
        b4 = st.sidebar.button("🗄️ Database Pasien", type="primary" if st.session_state['menu_internal_active'] == 'Database Pasien' else "secondary", use_container_width=True)
        if b4: st.session_state['menu_internal_active'] = "Database Pasien"; st.rerun()
        
    else:  # Nakes
        b1 = st.sidebar.button("📊 Dashboard", type="primary" if st.session_state['menu_internal_active'] == 'Dashboard' else "secondary", use_container_width=True)
        if b1: st.session_state['menu_internal_active'] = "Dashboard"; st.rerun()
        
        b2 = st.sidebar.button("🩺 Layanan Utama", type="primary" if st.session_state['menu_internal_active'] == 'Layanan Utama' else "secondary", use_container_width=True)
        if b2: st.session_state['menu_internal_active'] = "Layanan Utama"; st.rerun()
        
        b3 = st.sidebar.button("📈 Riwayat & Statistik", type="primary" if st.session_state['menu_internal_active'] == 'Riwayat & Statistik' else "secondary", use_container_width=True)
        if b3: st.session_state['menu_internal_active'] = "Riwayat & Statistik"; st.rerun()

    menu_pilihan = st.session_state['menu_internal_active']

    # 4. UTILITY DOWN SIDEBAR
    st.sidebar.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    if st.sidebar.button("❓ Bantuan", use_container_width=True):
        st.sidebar.info("Hubungi Pusat Layanan Khusus WA: 08123456789")

    if st.sidebar.button("🚪 Keluar", use_container_width=True):
        # 🌟 PERBAIKAN: Bersihkan URL Token agar benar-benar Logout (Lupa Ingatan) saat refresh
        st.query_params.clear()
        
        st.session_state['tampilkan_login'] = True 
        st.session_state['login_otp_step'] = "input_credentials" 
        st.session_state['temp_otp'] = None
        st.session_state['temp_user'] = None
        st.session_state['radio_index'] = 0
        st.session_state['login_role_active'] = "Pasien"
        st.session_state['menu_internal_active'] = "Dashboard"
        # Reset OTP state Nakes & Admin
        st.session_state['nakes_otp_step'] = "input_credentials"
        st.session_state['temp_nakes_otp'] = None
        st.session_state['temp_nakes_user'] = None
        st.session_state['admin_otp_step'] = "input_credentials"
        st.session_state['temp_admin_otp'] = None
        st.session_state['temp_admin_user'] = None
        
        logout_user()
        st.rerun()
        
    # ==========================================
    # 6. INTEGRASI ARSITEKTUR ROUTING PANEL TENGAH
    # ==========================================
    if menu_pilihan == "Dashboard":
        show_education_dashboard()
    elif menu_pilihan == "Riwayat Medis":
        show_patient_history()
    elif menu_pilihan == "Profil Saya":
        show_patient_profile_menu()
    elif menu_pilihan == "Evaluasi Model AI":
        show_admin_evaluation_menu()
    elif menu_pilihan == "Retraining Model AI":
        show_admin_model_menu()
    elif menu_pilihan == "Database Pasien":
        show_admin_database_menu()
    elif menu_pilihan == "Riwayat & Statistik":
        show_nakes_history_dashboard()
    else:
        if role_user == "Pasien":
            show_patient_main_menu()
        elif role_user == "Tenaga Kesehatan":
            show_nakes_main_menu()