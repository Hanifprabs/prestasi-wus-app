import streamlit as st
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- KODE REGISTRASI RAHASIA (ganti sesuai kebutuhan) ---
KODE_REGISTRASI_NAKES = "NAKES2026"
KODE_REGISTRASI_ADMIN = "ADMIN2026"

def init_auth_session():
    """
    Inisialisasi variabel session state untuk sistem autentikasi
    jika aplikasi baru pertama kali dijalankan.
    """
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = ""
    if 'role' not in st.session_state:
        st.session_state['role'] = None
    if 'patient_id' not in st.session_state:
        st.session_state['patient_id'] = ""
    # Session state untuk OTP Nakes
    if 'nakes_otp_step' not in st.session_state:
        st.session_state['nakes_otp_step'] = "input_credentials"
    if 'temp_nakes_otp' not in st.session_state:
        st.session_state['temp_nakes_otp'] = None
    if 'temp_nakes_user' not in st.session_state:
        st.session_state['temp_nakes_user'] = None
    # Session state untuk OTP Admin
    if 'admin_otp_step' not in st.session_state:
        st.session_state['admin_otp_step'] = "input_credentials"
    if 'temp_admin_otp' not in st.session_state:
        st.session_state['temp_admin_otp'] = None
    if 'temp_admin_user' not in st.session_state:
        st.session_state['temp_admin_user'] = None


def login_user(username, role, patient_id=""):
    """
    Menyimpan data pengguna yang berhasil login ke dalam session state
    """
    st.session_state['logged_in'] = True
    st.session_state['role'] = role
    st.session_state['username'] = username

    # KUNCI UTAMA: Simpan ID Pasien ke session state jika masuk sebagai role Pasien
    if role == "Pasien" and patient_id != "":
        st.session_state['patient_id'] = patient_id

    st.rerun()


def logout_user():
    """
    Menghapus status login pengguna dari session state (clearing session)
    dan mengarahkan kembali ke halaman login.
    """
    st.session_state['logged_in'] = False
    st.session_state['role'] = None
    st.session_state['username'] = ""
    st.session_state['patient_id'] = ""
    # Reset OTP steps
    st.session_state['nakes_otp_step'] = "input_credentials"
    st.session_state['temp_nakes_otp'] = None
    st.session_state['temp_nakes_user'] = None
    st.session_state['admin_otp_step'] = "input_credentials"
    st.session_state['temp_admin_otp'] = None
    st.session_state['temp_admin_user'] = None
    st.rerun()


def check_credentials(username, password_or_id, role):
    """
    Dipertahankan untuk kompatibilitas mundur (legacy).
    Pasien: divalidasi via DB.
    Nakes/Admin: kini menggunakan flow OTP, fungsi ini tidak dipanggil untuk mereka.
    """
    if role == "Pasien":
        from modules.database import get_db_connection
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM pasien_tb WHERE nama = %s AND id_pasien = %s",
                (username, password_or_id)
            )
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            st.error(f"Gagal menghubungkan ke database: {str(e)}")
            return False
    return False


def send_id_to_email(receiver_email, patient_name, patient_id):
    """
    Mengirimkan ID Pasien / Kode OTP ke email pasien secara otomatis
    menggunakan protokol SMTP TLS Google.
    """
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "muhammadhanifprabowo@gmail.com"
    SENDER_PASSWORD = "btag icmz lukc alxz"

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = f"🔑 ID Pasien DigiMind Anda: {patient_id}"

    html_body = f"""
    <html>
        <body style="font-family: 'Arial', sans-serif; color: #333333; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                <div style="background-color: #064e3b; padding: 24px; text-align: center;">
                    <h2 style="color: #ffffff; margin: 0; letter-spacing: 1px;">DigiMind System</h2>
                </div>
                <div style="padding: 30px; background-color: #ffffff;">
                    <p>Halo <strong>{patient_name}</strong>,</p>
                    <p>Terima kasih telah melakukan pendaftaran mandiri pada <strong>Sistem Prediksi Risiko Stunting WUS Kota Surakarta (DigiMind)</strong>.</p>
                    <div style="background-color: #ecfdf5; border-left: 4px solid #10b981; padding: 20px; border-radius: 8px; margin: 25px 0; text-align: center;">
                        <span style="font-size: 14px; color: #047857; display: block; margin-bottom: 5px; font-weight: bold;">ID PASIEN UNIK ANDA:</span>
                        <code style="font-size: 24px; font-weight: bold; color: #064e3b; letter-spacing: 2px; background: #ffffff; padding: 4px 12px; border-radius: 4px; border: 1px solid #bbf7d0;">{patient_id}</code>
                    </div>
                    <p style="color: #64748b; font-size: 14px;">⚠️ <em>Harap simpan ID ini baik-baik. Anda wajib memasukkan ID ini beserta Nama Lengkap Anda setiap kali masuk kembali ke sistem untuk melihat rekam medis atau grafik riwayat perkembangan kesehatan Anda.</em></p>
                </div>
                <div style="background-color: #f8fafc; padding: 15px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8;">
                    &copy; 2026 DigiMind Stunting Detection Project. All rights reserved.
                </div>
            </div>
        </body>
    </html>
    """
    msg.attach(MIMEText(html_body, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Gagal mengirim email: {str(e)}")
        return False


def send_otp_staff_email(receiver_email, username, otp_code, role):
    """
    Mengirimkan kode OTP login ke email Tenaga Kesehatan / Admin.
    """
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "muhammadhanifprabowo@gmail.com"
    SENDER_PASSWORD = "btag icmz lukc alxz"

    role_label = "Tenaga Kesehatan" if role == "Tenaga Kesehatan" else "Admin"
    role_color = "#0369a1" if role == "Tenaga Kesehatan" else "#7c3aed"
    role_bg    = "#e0f2fe"  if role == "Tenaga Kesehatan" else "#ede9fe"

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = f"🔐 Kode OTP Login DigiMind — {role_label}"

    html_body = f"""
    <html>
        <body style="font-family: 'Arial', sans-serif; color: #333333; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                <div style="background-color: #1e293b; padding: 24px; text-align: center;">
                    <h2 style="color: #ffffff; margin: 0; letter-spacing: 1px;">DigiMind System</h2>
                    <p style="color: #94a3b8; margin: 4px 0 0 0; font-size: 13px;">Portal {role_label}</p>
                </div>
                <div style="padding: 30px; background-color: #ffffff;">
                    <p>Halo <strong>{username}</strong>,</p>
                    <p>Berikut adalah <strong>Kode OTP</strong> untuk masuk ke Sistem DigiMind sebagai <strong>{role_label}</strong>. Kode ini berlaku untuk satu kali penggunaan.</p>
                    <div style="background-color: {role_bg}; border-left: 4px solid {role_color}; padding: 20px; border-radius: 8px; margin: 25px 0; text-align: center;">
                        <span style="font-size: 14px; color: {role_color}; display: block; margin-bottom: 8px; font-weight: bold;">KODE OTP LOGIN ANDA:</span>
                        <code style="font-size: 40px; font-weight: bold; color: #1e293b; letter-spacing: 8px; background: #ffffff; padding: 8px 20px; border-radius: 8px; border: 1px solid #cbd5e1;">{otp_code}</code>
                    </div>
                    <p style="color: #64748b; font-size: 14px;">⚠️ <em>Jangan bagikan kode ini kepada siapa pun. Jika Anda tidak merasa meminta kode ini, abaikan email ini.</em></p>
                </div>
                <div style="background-color: #f8fafc; padding: 15px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8;">
                    &copy; 2026 DigiMind Stunting Detection Project. All rights reserved.
                </div>
            </div>
        </body>
    </html>
    """
    msg.attach(MIMEText(html_body, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Gagal mengirim OTP staf: {str(e)}")
        return False