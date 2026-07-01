import streamlit as st
import numpy as np
import pandas as pd
import datetime
import io
import textwrap 
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from modules.database import get_db_connection
from psycopg2.extras import RealDictCursor

# Konfigurasi wilayah Solo untuk input Alamat
KECAMATAN_SOLO = ["Banjarsari", "Jebres", "Laweyan", "Pasar Kliwon", "Serengan"]

# Mapping Kode Puskesmas untuk format Nomor Antrean
KODE_FASKES = {
    "Puskesmas Penumping": "PNP",
    "Puskesmas Jayengan": "JYG",
    "Puskesmas Sangkrah": "SKR",
    "Puskesmas Pucang Sawit": "PCS",
    "Puskesmas Nusukan": "NSK"
}

def show_patient_main_menu():
    """
    Menampilkan Layanan Utama Pasien berupa Form Kuesioner Mandiri dan Penjadwalan KIA.
    Dilengkapi dengan pengecekan kuota maksimal 4 pasien per sesi per hari per puskesmas.
    """
    nama_user = st.session_state.get('username', '')
    patient_id_session = st.session_state.get('patient_id', '')
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT id_rekam, usia, status_pemeriksaan, id_pasien 
        FROM pasien_tb 
        WHERE id_pasien = %s OR (nama = %s AND status_pemeriksaan = 'Menunggu Pemeriksaan Fisik')
        ORDER BY id_rekam DESC LIMIT 1
    """, (patient_id_session, nama_user))
    row_terakhir = cursor.fetchone()
    conn.close()
    
    pemeriksaan_aktif = False
    id_aktif = patient_id_session
    status_terakhir = None
    row_id_terakhir = None

    if row_terakhir:
        row_id_terakhir = row_terakhir['id_rekam']
        usia_tercatat = row_terakhir['usia']
        status_terakhir = row_terakhir['status_pemeriksaan']
        id_aktif = row_terakhir['id_pasien']
        
        # JIKA pasien sudah memiliki antrean aktif yang belum diperiksa Nakes
        if usia_tercatat is not None and status_terakhir == 'Menunggu Pemeriksaan Fisik':
            pemeriksaan_aktif = True
            
            # TAMPILKAN TIKET JIKA ADA
            if 'tiket_antrean' in st.session_state:
                t = st.session_state['tiket_antrean']
                
                st.markdown(f"""<div style='background: linear-gradient(135deg, #006c49, #064e3b); padding: 2.5rem; border-radius: 20px; color: white; margin-bottom: 1.5rem; text-align: center; box-shadow: 0 10px 30px rgba(0, 108, 73, 0.2); border: 1px solid #10b981;'>
<h4 style='color: #a7f3d0; margin-top:0; font-weight:700; letter-spacing: 1px; font-size: 1.1rem;'>KARTU ANTREAN BIRO KIA PUSKESMAS</h4>
<h1 style='font-size: 4.5rem; color: #ffffff; margin: 0.5rem 0; font-weight: 800; letter-spacing: 2px; text-shadow: 0 4px 10px rgba(0,0,0,0.2);'>{t['no']}</h1>
<div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 12px; display: inline-block; text-align: left; margin-top: 1rem;'>
<p style='font-size: 1.05rem; margin: 0 0 0.5rem 0;'>👤 <strong>ID Pasien:</strong> {id_aktif}</p>
<p style='font-size: 1.05rem; margin: 0 0 0.5rem 0;'>🏥 <strong>Lokasi:</strong> {t['faskes']}</p>
<p style='font-size: 1.05rem; margin: 0;'>📅 <strong>Jadwal Cek Fisik:</strong> {t['jadwal']}</p>
</div>
</div>""", unsafe_allow_html=True)
                
                # MEMBUAT GAMBAR FOTO TIKET UNTUK DIUNDUH
                buf = io.BytesIO()
                fig, ax = plt.subplots(figsize=(6, 4), facecolor='#006c49')
                ax.axis('off')
                
                # Ekstrak tanggal dan sesi untuk dipisah baris agar muat di gambar
                jadwal_split = t['jadwal'].split(" - ")
                tgl_str = jadwal_split[0] if len(jadwal_split) > 0 else t['jadwal']
                sesi_str = jadwal_split[1] if len(jadwal_split) > 1 else ""

                ax.text(0.5, 0.90, 'KARTU ANTREAN BIRO KIA', fontsize=15, color='#a7f3d0', ha='center', weight='bold')
                ax.text(0.5, 0.60, t['no'], fontsize=45, color='white', ha='center', weight='bold')
                info_text = f"ID Pasien: {id_aktif}\nLokasi: {t['faskes']}\nTanggal: {tgl_str}\nWaktu: {sesi_str}"
                ax.text(0.5, 0.20, info_text, fontsize=11, color='white', ha='center', linespacing=1.6)
                
                plt.savefig(buf, format='png', bbox_inches='tight', dpi=200, facecolor='#006c49')
                buf.seek(0)
                plt.close(fig)
                
                st.download_button("📥 Unduh Foto Kartu Antrean", data=buf, file_name=f"Antrean_{t['no']}.png", mime="image/png", type="primary", use_container_width=True)
                st.info("💡 **TIPS:** Unduh foto ini dan tunjukkan kepada petugas pendaftaran di Puskesmas pada hari kunjungan Anda.")
                
            else:
                # Fallback jika pasien me-refresh halaman tapi statusnya masih menunggu
                st.markdown("<h3 style='color:#b45309; margin-top:0;'>⏳ Pendaftaran Aktif Ditemukan</h3>", unsafe_allow_html=True)
                st.warning(
                    f"Anda sedang berada dalam antrean pemeriksaan dengan ID: **{id_aktif}**. "
                    "Silakan selesaikan pemeriksaan fisik (LILA, Hb, BB, TB) di Puskesmas terlebih dahulu sebelum mengajukan form baru."
                )

            # TOMBOL BATALKAN JADWAL PEMERIKSAAN
            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
            if st.button("❌ Batalkan Rencana Pemeriksaan Fisik", use_container_width=True):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE pasien_tb 
                    SET status_pemeriksaan = 'Menunggu Pengisian Data Sosiodemografi',
                        lokasi_faskes = NULL, jadwal_kunjungan = NULL, no_antrean = NULL
                    WHERE id_rekam = %s
                """, (row_id_terakhir,))
                conn.commit()
                conn.close()
                
                try:
                    st.cache_data.clear()
                except Exception:
                    pass
                
                if 'tiket_antrean' in st.session_state:
                    del st.session_state['tiket_antrean']
                
                st.success("Jadwal pemeriksaan berhasil dibatalkan. Anda dapat merencanakan ulang jadwal yang baru.")
                st.rerun()

    # JIKA TIDAK ADA ANTREAN AKTIF (Bisa isi form & pilih jadwal baru)
    if not pemeriksaan_aktif:
        st.markdown(f"""<div style='margin-bottom: 1.5rem; padding-left: 0.5rem;'>
<h1 style='color: #0f172a; font-size: 2.4rem; font-weight: 800; margin-bottom: 0.2rem; margin-top: 0;'>Layanan Utama</h1>
<p style='color: #475569; font-size: 1.05rem; font-weight: 400; margin-top: 0; line-height: 1.6;'>
Lengkapi data sosiodemografi di bawah ini sebagai tahap awal prediksi risiko stunting. Setelah pengisian form ini, Anda akan dijadwalkan untuk melakukan pemeriksaan fisik lanjutan di Puskesmas. <br>
ID Pasien Anda: <strong style='color:#0f172a;'>{id_aktif}</strong>
</p>
</div>""", unsafe_allow_html=True)
        
        with st.form("form_kuesioner_pasien"):
            st.markdown("<div class='main-form-wrapper'></div>", unsafe_allow_html=True)
            
            st.markdown("<p style='font-size: 1.1rem; font-weight: 600; color: #1e293b; margin-bottom: 0.5rem;'>A. Identitas Dasar & Demografi</p>", unsafe_allow_html=True)
            col_id1, col_id2 = st.columns(2)
        
            with col_id1: 
                usia = st.number_input("Usia Anda saat ini (Tahun)", min_value=15, max_value=49, value=None, placeholder="Ketik usia di sini...", step=1)
            
            with col_id2: 
                pend_opt = st.selectbox("Pendidikan Terakhir Anda?", ["SD / SMP / Sederajat", "SMA / SMK / Sederajat", "Diploma / Sarjana (S1/S2/S3)"], index=None, placeholder="Pilih Pendidikan...")
            
            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
            
            st.markdown("<p style='font-size: 1.1rem; font-weight: 600; color: #1e293b; margin-bottom: 0.5rem;'>B. Kondisi Lingkungan & Ekonomi</p>", unsafe_allow_html=True)
            col_en1, col_en2 = st.columns(2)
            with col_en1: pendapatan_opt = st.selectbox("Rata-rata pendapatan bulanan keluarga Anda?", ["< Rp 2.000.000 (Rendah)", "Rp 2.000.000 - Rp 5.000.000 (Sedang)", "> Rp 5.000.000 (Tinggi)"], index=None, placeholder="Pilih Pendapatan...")
            with col_en2:
                air_opt = st.radio("Apakah rumah Anda memiliki akses air bersih yang layak?", ["Ya", "Tidak"], index=None, horizontal=True)
                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                faskes_opt = st.radio("Apakah Anda memiliki kemudahan akses ke layanan kesehatan?", ["Ya (Mudah)", "Tidak (Sulit)"], index=None, horizontal=True)
            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

            st.markdown("<p style='font-size: 1.1rem; font-weight: 600; color: #1e293b; margin-bottom: 0.5rem;'>C. Kuesioner Pengetahuan Gizi Wanita Usia Subur</p>", unsafe_allow_html=True)
            q1 = st.radio("Menurut Anda, apakah anemia (kurang darah) pada WUS dapat memicu kelahiran bayi stunting?", ["Ya", "Tidak"], index=None, horizontal=True)
            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            q2 = st.radio("Berapa ukuran minimal LILA (Lingkar Lengan Atas) normal bagi WUS agar terhindar dari KEK?", ["23.5 cm", "20.0 cm"], index=None, horizontal=True)
            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            q3 = st.radio("Apakah konsumsi Tablet Tambah Darah (TTD) penting dilakukan secara rutin oleh wanita usia subur?", ["Sangat Penting", "Tidak Terlalu Penting"], index=None, horizontal=True)
            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            q4 = st.radio("Zat gizi apa yang paling krusial untuk mencegah cacat tabung saraf pada awal kehamilan?", ["Asam Folat", "Vitamin C"], index=None, horizontal=True)
            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            q5 = st.radio("Berapa lama durasi minimal pemberian ASI Eksklusif yang disarankan bagi bayi?", ["6 Bulan", "2 Bulan"], index=None, horizontal=True)
            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

            st.markdown("<p style='font-size: 1.1rem; font-weight: 600; color: #1e293b; margin-bottom: 0.5rem;'>D. Rencana Pemeriksaan Fisik (Biro KIA Puskesmas)</p>", unsafe_allow_html=True)
            st.markdown("""<div style='background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1rem; margin-bottom: 1.5rem;'>
<p style='margin-top: 0; font-weight: 700; color: #0f172a; font-size: 0.95rem;'>🕒 JAM OPERASIONAL PUSKESMAS SURAKARTA:</p>
<ul style='margin-bottom: 0; color: #475569; font-size: 0.9rem;'>
<li><strong>Senin - Kamis:</strong> 4 Sesi (07:30 - 12:00 WIB)</li>
<li><strong>Jumat:</strong> 2 Sesi (07:30 - 10:00 WIB)</li>
<li><strong>Sabtu:</strong> 3 Sesi (07:30 - 11:00 WIB)</li>
<li><strong style='color: #dc2626;'>Minggu: Tutup (Closed)</strong></li>
</ul>
<p style='margin-top: 5px; margin-bottom: 0; font-weight: 700; color: #dc2626; font-size: 0.85rem;'>*Maksimal Kuota: 4 Pasien per Sesi.</p>
</div>""", unsafe_allow_html=True)

            col_jadwal1, col_jadwal2, col_jadwal3 = st.columns([1.5, 1, 1])
            with col_jadwal1: 
                lokasi_puskesmas = st.selectbox("Pilih Lokasi Puskesmas", list(KODE_FASKES.keys()), index=None, placeholder="Pilih Puskesmas...")
            
            with col_jadwal2:
                besok = datetime.date.today() + datetime.timedelta(days=1)
                tanggal_kunjungan = st.date_input("Tanggal Cek Fisik", min_value=besok, value=besok)
            
            with col_jadwal3: 
                pilihan_sesi = ["Sesi 1 (07.30 - 09.00)", "Sesi 2 (09.00 - 10.00)", "Sesi 3 (10.00 - 11.00)", "Sesi 4 (11.00 - 12.00)"]
                sesi_kedatangan = st.selectbox("Pilih Sesi", pilihan_sesi, index=None, placeholder="Pilih Sesi...")

            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
            submit_btn = st.form_submit_button("SIMPAN & AJUKAN DATA KUESIONER", type="primary", use_container_width=True)
            
            if submit_btn:
                hari_kunjungan = tanggal_kunjungan.weekday()
                # 1. Pengecekan Usia Kosong (Prioritas Utama)
                if usia is None:
                    st.error("⚠️ Gagal Menyimpan! Kolom 'Usia Anda saat ini' wajib diisi. Silakan ketik angka usia Anda di bagian Identitas Dasar.")
                
                # 2. Pengecekan Dropdown/Pilihan yang Kosong
                elif pend_opt is None or pendapatan_opt is None or air_opt is None or faskes_opt is None or lokasi_puskesmas is None or sesi_kedatangan is None or None in [q1, q2, q3, q4, q5]:
                    st.warning("⚠️ Mohon lengkapi seluruh isian data kuesioner dan pastikan Anda telah memilih sesi Puskesmas tanpa ada yang terlewat.")
                
                # 3. Pengecekan Hari Libur dan Sesi Berdasarkan Hari Kunjungan
                elif hari_kunjungan == 6:
                    st.error("❌ Puskesmas tutup pada hari Minggu. Silakan pilih tanggal kunjungan yang lain.")
                
                elif hari_kunjungan == 4 and sesi_kedatangan in ["Sesi 3 (10.00 - 11.00)", "Sesi 4 (11.00 - 12.00)"]:
                    st.error("❌ Hari Jumat hanya melayani Sesi 1 dan Sesi 2 (hingga pukul 10:00 WIB). Silakan pilih sesi yang sesuai.")
                
                elif hari_kunjungan == 5 and sesi_kedatangan == "Sesi 4 (11.00 - 12.00)":
                    st.error("❌ Hari Sabtu hanya melayani Sesi 1, 2, dan 3 (hingga pukul 11:00 WIB). Silakan pilih sesi yang sesuai.")
                
                # Jika semua lolos validasi, proses pendaftaran
                else:
                    # Persiapan Data
                    l_pendidikan = 1 if "SD" in pend_opt else (2 if "SMA" in pend_opt else 3)
                    l_pendapatan = 1 if "Rendah" in pendapatan_opt else (2 if "Sedang" in pendapatan_opt else 3)
                    air_bersih = 1 if air_opt == "Ya" else 0
                    akses_faskes = 1 if "Ya" in faskes_opt else 0
                    skor_gizi = sum([q1 == "Ya", q2 == "23.5 cm", q3 == "Sangat Penting", q4 == "Asam Folat", q5 == "6 Bulan"])
                    
                    kode_faskes = KODE_FASKES.get(lokasi_puskesmas, "KIA")
                    kode_sesi = sesi_kedatangan.split(" ")[1]
                    jadwal_lengkap = f"{tanggal_kunjungan.strftime('%d %B %Y')} - {sesi_kedatangan} WIB"
                    waktu_pengisian_sekarang = datetime.datetime.now().strftime("%d %B %Y - %H:%M WIB")

                    conn = get_db_connection()
                    cursor = conn.cursor()

                    # --- CEK KUOTA (MAKSIMAL 4 PASIEN PER SESI) ---
                    cursor.execute("SELECT COUNT(*) FROM pasien_tb WHERE lokasi_faskes = %s AND jadwal_kunjungan = %s", (lokasi_puskesmas, jadwal_lengkap))
                    jumlah_orang_sesi_ini = cursor.fetchone()[0]
                    
                    if jumlah_orang_sesi_ini >= 4:
                        conn.close()
                        st.error(f"⚠️ **KUOTA PENUH:** Maaf, {sesi_kedatangan} di {lokasi_puskesmas} pada tanggal {tanggal_kunjungan.strftime('%d/%m/%Y')} sudah mencapai batas maksimal (4 Pasien). Silakan pilih sesi atau hari yang berbeda.")
                    else:
                        # PROSES PENDAFTARAN JIKA KUOTA TERSEDIA
                        no_antrean_terstruktur = f"{kode_faskes}-S{kode_sesi}-{jumlah_orang_sesi_ini + 1:03d}" 

                        if status_terakhir == 'Selesai Diperiksa':
                            cursor.execute("""
                                INSERT INTO pasien_tb (
                                    id_pasien, nama, usia, pendapatan_bulanan, akses_air_bersih, 
                                    akses_layanan_kesehatan, pendidikan_terakhir, skor_pengetahuan_gizi,
                                    lokasi_faskes, jadwal_kunjungan, no_antrean, status_pemeriksaan, tanggal_pengisian
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Menunggu Pemeriksaan Fisik', %s)
                            """, (id_aktif, nama_user, usia, l_pendapatan, air_bersih, akses_faskes, l_pendidikan, skor_gizi, lokasi_puskesmas, jadwal_lengkap, no_antrean_terstruktur, waktu_pengisian_sekarang))
                        else:
                            cursor.execute("""
                                UPDATE pasien_tb 
                                SET usia = %s, pendapatan_bulanan = %s, akses_air_bersih = %s, 
                                    akses_layanan_kesehatan = %s, pendidikan_terakhir = %s, skor_pengetahuan_gizi = %s,
                                    lokasi_faskes = %s, jadwal_kunjungan = %s, no_antrean = %s,
                                    status_pemeriksaan = 'Menunggu Pemeriksaan Fisik', tanggal_pengisian = %s
                                WHERE id_rekam = %s
                            """, (usia, l_pendapatan, air_bersih, akses_faskes, l_pendidikan, skor_gizi, lokasi_puskesmas, jadwal_lengkap, no_antrean_terstruktur, waktu_pengisian_sekarang, row_id_terakhir))
                        
                        conn.commit()
                        conn.close()

                        try:
                            st.cache_data.clear()
                        except Exception:
                            pass

                        st.session_state['tiket_antrean'] = {'faskes': lokasi_puskesmas, 'jadwal': jadwal_lengkap, 'no': no_antrean_terstruktur}
                        st.rerun()

def format_tanggal_indo(tgl_string):
    """Fungsi helper untuk menerjemahkan format tanggal ke Bahasa Indonesia lengkap dengan nama Hari"""
    if tgl_string == '-' or not tgl_string:
        return '-'
    try:
        dt_obj = datetime.datetime.strptime(tgl_string, '%d %B %Y')
        hari_indo = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"][dt_obj.weekday()]
        bulan_indo = {
            "January": "Jan", "February": "Feb", "March": "Mar", "April": "Apr", "May": "Mei", "June": "Jun", 
            "July": "Jul", "August": "Agt", "September": "Sep", "October": "Okt", "November": "Nov", "December": "Des"
        }
        bln_eng = dt_obj.strftime("%B")
        bln_ind = bulan_indo.get(bln_eng, bln_eng)
        return f"{hari_indo}, {dt_obj.day} {bln_ind} {dt_obj.year}"
    except:
        return tgl_string

def show_patient_history():
    """
    Menampilkan riwayat lengkap pemeriksaan medis pasien dengan UI Modern.
    Tabel terurut Ascending (terlama di atas, terbaru di bawah) dengan format Tanggal Hari yang rapi.
    """
    nama_user = st.session_state.get('username', '')
    patient_id_active = st.session_state.get('patient_id', '') 
    
    if not patient_id_active:
        st.warning("ID Pasien tidak ditemukan.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id_rekam, id_pasien, usia, tanggal_pengisian, jadwal_kunjungan, lokasi_faskes, status_pemeriksaan, hasil_risiko, rekomendasi, hb_darah, lila, imt, no_antrean
        FROM pasien_tb 
        WHERE id_pasien = %s
        ORDER BY id_rekam ASC
    """, (patient_id_active,))
    rows = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]
    df_history = pd.DataFrame(rows, columns=col_names) if rows else pd.DataFrame(columns=col_names)
    conn.close()
    
    st.markdown(f"""<div style='margin-bottom: 2rem; padding-left: 0.5rem;'>
<span style='background-color: #dcfce7; color: #047857; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px;'>✔ PASIEN TERVERIFIKASI</span>
<h1 style='color: #0f172a; font-size: 2.2rem; font-weight: 800; margin-top: 0.5rem; margin-bottom: 0;'>Status Kesehatan Saya <span style='color: #006c49;'>({nama_user})</span></h1>
</div>""", unsafe_allow_html=True)
    
    if df_history.empty:
        st.info("Belum ada rekam medis yang terdaftar di dalam sistem.")
        return

    list_tgl_isi = []
    list_jadwal_fisik = []
    list_urutan = []

    for idx, row in df_history.iterrows():
        list_urutan.append(f"Sesi Ke-{idx + 1}")
        if pd.isna(row['usia']) or pd.isna(row['lokasi_faskes']):
            df_history.at[idx, 'status_pemeriksaan'] = 'Menunggu Pengisian Form'
            df_history.at[idx, 'lokasi_faskes'] = '-'
            list_tgl_isi.append('-')
            list_jadwal_fisik.append('-')
        else:
            list_tgl_isi.append(row['tanggal_pengisian'] if pd.notna(row['tanggal_pengisian']) else '-')
            tgl = row['jadwal_kunjungan'].split(" - ")[0] if pd.notna(row['jadwal_kunjungan']) else '-'
            list_jadwal_fisik.append(tgl)
            
        if pd.isna(row['hasil_risiko']):
            df_history.at[idx, 'hasil_risiko'] = 'Belum Dihitung'

    df_history['Tanggal Cek Fisik'] = list_jadwal_fisik
    df_history['Sesi ID'] = list_urutan
    
    data_terakhir_aktual = df_history.iloc[-1]
    
    df_selesai = df_history[df_history['status_pemeriksaan'] == 'Selesai Diperiksa']
    ada_data_selesai = not df_selesai.empty

    if data_terakhir_aktual['status_pemeriksaan'] == 'Menunggu Pemeriksaan Fisik':
        st.warning("⏳ **Catatan:** Anda telah mengisi form kuesioner. Saat ini Anda berstatus **Menunggu Pemeriksaan Fisik** di fasilitas kesehatan (Puskesmas). Silakan datang sesuai jadwal.")
    elif data_terakhir_aktual['status_pemeriksaan'] == 'Menunggu Pengisian Form':
        st.info("ℹ️ **Catatan:** Sesi aktif Anda saat ini masih menunggu pengisian form sosiodemografi. Segera lengkapi di menu **Layanan Utama**.")
    
    col_kiri, col_kanan = st.columns([1, 1.8])
    
    with col_kiri:
        if ada_data_selesai:
            # TAMPILKAN PANEL REKOMENDASI HANYA JIKA ADA DATA YANG SELESAI
            data_tampil_card = df_selesai.iloc[-1]
            val_hb = f"{float(data_tampil_card['hb_darah']):.1f}" if not pd.isna(data_tampil_card['hb_darah']) else "-"
            val_lila = f"{float(data_tampil_card['lila']):.1f}" if not pd.isna(data_tampil_card['lila']) else "-"
            val_imt = f"{float(data_tampil_card['imt']):.1f}" if not pd.isna(data_tampil_card['imt']) else "-"
            tgl_update_raw = data_tampil_card['Tanggal Cek Fisik']
            tgl_update = format_tanggal_indo(tgl_update_raw)
            
            badge_color = "#10b981" 
            badge_bg = "#d1fae5"
            if "TINGGI" in str(data_tampil_card['hasil_risiko']).upper():
                badge_color = "#ef4444" 
                badge_bg = "#fee2e2"
                
            st.markdown(f"""<div style='background-color: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);'>
<div style='display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem;'>
<div>
<p style='margin: 0; font-size: 0.9rem; font-weight: 700; color: #0f172a;'>Hasil Prediksi AI</p>
<p style='margin: 0; font-size: 0.75rem; color: #64748b;'>{tgl_update}</p>
</div>
<div style='background-color: {badge_bg}; color: {badge_color}; padding: 6px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; text-align: center;'>
{data_tampil_card['hasil_risiko'].upper()}
</div>
</div>
<div style='background-color: #f8fafc; border-radius: 12px; padding: 1rem; margin-bottom: 0.8rem; border: 1px solid #f1f5f9;'>
<p style='margin: 0 0 5px 0; font-size: 0.75rem; font-weight: 700; color: #475569; letter-spacing: 0.5px;'>HEMOGLOBIN (Hb)</p>
<div style='display: flex; align-items: baseline; gap: 5px;'>
<span style='font-size: 2rem; font-weight: 800; color: #006c49; line-height: 1;'>{val_hb}</span>
<span style='font-size: 0.9rem; font-weight: 600; color: #64748b;'>g/dL</span>
</div>
</div>
<div style='background-color: #f8fafc; border-radius: 12px; padding: 1rem; margin-bottom: 0.8rem; border: 1px solid #f1f5f9;'>
<p style='margin: 0 0 5px 0; font-size: 0.75rem; font-weight: 700; color: #475569; letter-spacing: 0.5px;'>LINGKAR LENGAN (LILA)</p>
<div style='display: flex; align-items: baseline; gap: 5px;'>
<span style='font-size: 2rem; font-weight: 800; color: #006c49; line-height: 1;'>{val_lila}</span>
<span style='font-size: 0.9rem; font-weight: 600; color: #64748b;'>cm</span>
</div>
</div>
<div style='background-color: #f8fafc; border-radius: 12px; padding: 1rem; border: 1px solid #f1f5f9;'>
<p style='margin: 0 0 5px 0; font-size: 0.75rem; font-weight: 700; color: #475569; letter-spacing: 0.5px;'>BMI (IMT)</p>
<div style='display: flex; align-items: baseline; gap: 5px;'>
<span style='font-size: 2rem; font-weight: 800; color: #006c49; line-height: 1;'>{val_imt}</span>
<span style='font-size: 0.9rem; font-weight: 600; color: #64748b;'>kg/m²</span>
</div>
</div>
</div>""", unsafe_allow_html=True)
            
            rekomendasi_teks = data_tampil_card['rekomendasi'] if pd.notna(data_tampil_card['rekomendasi']) else "Belum ada rekomendasi dari Nakes."
            rekomendasi_display = rekomendasi_teks.replace('\n', '<br>')
            
            st.markdown(f"""<div style='background-color: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);'>
<div style='display: flex; align-items: center; gap: 8px; margin-bottom: 1rem;'>
<span style='background-color: #ecfdf5; color: #10b981; border-radius: 50%; width: 24px; height: 24px; display: inline-flex; justify-content: center; align-items: center; font-size: 14px;'>✓</span>
<p style='margin: 0; font-size: 0.95rem; font-weight: 800; color: #0f172a;'>Rekomendasi Intervensi Terakhir</p>
</div>
<div style='font-size: 0.9rem; color: #475569; line-height: 1.6; margin-bottom: 1.5rem;'>
{rekomendasi_display}
</div>
</div>""", unsafe_allow_html=True)
            
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            
            wrapper = textwrap.TextWrapper(width=70)
            lines = rekomendasi_teks.split('\n')
            wrapped_lines = [wrapper.fill(text=line) for line in lines]
            rekomendasi_wrapped = '\n'.join(wrapped_lines)
            
            isi_laporan = f"""LAPORAN REKAM MEDIS (DIGIMIND)
=========================================

IDENTITAS PASIEN
-----------------------------------------
Nama Pasien : {nama_user}
ID Pasien   : {patient_id_active}
Tanggal Cek : {tgl_update}
Faskes      : {data_tampil_card['lokasi_faskes']}

HASIL PEMERIKSAAN FISIK
-----------------------------------------
Kadar Hb    : {val_hb} g/dL
Ukuran LILA : {val_lila} cm
BMI (IMT)   : {val_imt} kg/m²

DIAGNOSIS AI
-----------------------------------------
Status      : {data_tampil_card['hasil_risiko'].upper()}

REKOMENDASI INTERVENSI
-----------------------------------------
{rekomendasi_wrapped}

=========================================
*Dokumen ini dicetak otomatis oleh Sistem DigiMind*
"""
            buf_pdf = io.BytesIO()
            fig_pdf, ax_pdf = plt.subplots(figsize=(8.27, 11.69), facecolor='white') 
            ax_pdf.axis('off') 
            
            ax_pdf.text(0.08, 0.95, isi_laporan, transform=ax_pdf.transAxes, fontsize=11, 
                        verticalalignment='top', horizontalalignment='left', family='monospace')
            
            plt.savefig(buf_pdf, format='pdf', bbox_inches='tight')
            buf_pdf.seek(0)
            plt.close(fig_pdf)

            st.download_button(
                label="📄 Unduh Laporan Lengkap (PDF)", 
                data=buf_pdf, 
                file_name=f"Laporan_Medis_{patient_id_active}.pdf", 
                mime="application/pdf",
                use_container_width=True
            )
        
        else:
            # JIKA BELUM ADA DATA SELESAI, TAMPILKAN PANEL KOSONG
            st.markdown(f"""<div style='background-color: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);'>
<div style='display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem;'>
<div>
<p style='margin: 0; font-size: 0.9rem; font-weight: 700; color: #0f172a;'>Hasil Prediksi AI</p>
<p style='margin: 0; font-size: 0.75rem; color: #64748b;'>-</p>
</div>
<div style='background-color: #f1f5f9; color: #64748b; padding: 6px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; text-align: center;'>
BELUM DIHITUNG
</div>
</div>
<div style='background-color: #f8fafc; border-radius: 12px; padding: 1rem; margin-bottom: 0.8rem; border: 1px solid #f1f5f9;'>
<p style='margin: 0 0 5px 0; font-size: 0.75rem; font-weight: 700; color: #475569; letter-spacing: 0.5px;'>HEMOGLOBIN (Hb)</p>
<div style='display: flex; align-items: baseline; gap: 5px;'>
<span style='font-size: 2rem; font-weight: 800; color: #94a3b8; line-height: 1;'>-</span>
<span style='font-size: 0.9rem; font-weight: 600; color: #94a3b8;'>g/dL</span>
</div>
</div>
<div style='background-color: #f8fafc; border-radius: 12px; padding: 1rem; margin-bottom: 0.8rem; border: 1px solid #f1f5f9;'>
<p style='margin: 0 0 5px 0; font-size: 0.75rem; font-weight: 700; color: #475569; letter-spacing: 0.5px;'>LINGKAR LENGAN (LILA)</p>
<div style='display: flex; align-items: baseline; gap: 5px;'>
<span style='font-size: 2rem; font-weight: 800; color: #94a3b8; line-height: 1;'>-</span>
<span style='font-size: 0.9rem; font-weight: 600; color: #94a3b8;'>cm</span>
</div>
</div>
<div style='background-color: #f8fafc; border-radius: 12px; padding: 1rem; border: 1px solid #f1f5f9;'>
<p style='margin: 0 0 5px 0; font-size: 0.75rem; font-weight: 700; color: #475569; letter-spacing: 0.5px;'>BMI (IMT)</p>
<div style='display: flex; align-items: baseline; gap: 5px;'>
<span style='font-size: 2rem; font-weight: 800; color: #94a3b8; line-height: 1;'>-</span>
<span style='font-size: 0.9rem; font-weight: 600; color: #94a3b8;'>kg/m²</span>
</div>
</div>
</div>""", unsafe_allow_html=True)

    with col_kanan:
        html_tabel = """<div style='background-color: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);'>
<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>
<h3 style='margin: 0; font-size: 1.1rem; font-weight: 800; color: #0f172a;'>Riwayat Pemeriksaan</h3>
</div>\n"""

        # --- PERBAIKAN FILTER TABEL: HIDE DRAFT & DELETED QUEUE ---
        kondisi_selesai = df_history['status_pemeriksaan'] == 'Selesai Diperiksa'
        kondisi_menunggu_valid = (df_history['status_pemeriksaan'] == 'Menunggu Pemeriksaan Fisik') & \
                                 (df_history['no_antrean'].notna()) & \
                                 (df_history['no_antrean'].astype(str).str.strip() != '') & \
                                 (df_history['no_antrean'].astype(str).str.strip() != '-') & \
                                 (df_history['no_antrean'].astype(str).str.lower() != 'none')
                                 
        df_tabel_valid = df_history[kondisi_selesai | kondisi_menunggu_valid]
        
        if df_tabel_valid.empty:
            html_tabel += "<div style='text-align: center; padding: 2rem 0; color: #94a3b8;'><p style='margin: 0; font-size: 0.95rem; font-weight: 500;'>Belum ada riwayat antrean atau pemeriksaan yang valid.</p></div>"
        else:
            html_tabel += """<div style='display: flex; border-bottom: 2px solid #f1f5f9; padding-bottom: 0.75rem; margin-bottom: 0.5rem;'>
<div style='flex: 0.6; font-size: 0.75rem; font-weight: 700; color: #64748b; letter-spacing: 0.5px;'>KE-</div>
<div style='flex: 1.5; font-size: 0.75rem; font-weight: 700; color: #64748b; letter-spacing: 0.5px;'>TANGGAL</div>
<div style='flex: 1.2; font-size: 0.75rem; font-weight: 700; color: #64748b; letter-spacing: 0.5px;'>ANTREAN</div>
<div style='flex: 1.5; font-size: 0.75rem; font-weight: 700; color: #64748b; letter-spacing: 0.5px;'>FASKES</div>
<div style='flex: 1; font-size: 0.75rem; font-weight: 700; color: #64748b; letter-spacing: 0.5px;'>STATUS</div>
<div style='flex: 1.5; font-size: 0.75rem; font-weight: 700; color: #64748b; letter-spacing: 0.5px;'>HASIL AI</div>
</div>\n"""
            
            for i, (idx, row) in enumerate(df_tabel_valid.iterrows()):
                dot_color = "#10b981" if "rendah" in str(row['hasil_risiko']).lower() or "normal" in str(row['hasil_risiko']).lower() else ("#ef4444" if "tinggi" in str(row['hasil_risiko']).lower() else "#cbd5e1")
                
                st_color = "#047857" if row['status_pemeriksaan'] == 'Selesai Diperiksa' else "#b45309"
                st_bg = "#dcfce7" if row['status_pemeriksaan'] == 'Selesai Diperiksa' else "#fef3c7"
                st_text = "SELESAI" if row['status_pemeriksaan'] == 'Selesai Diperiksa' else "MENUNGGU"
                
                antrean = row['no_antrean']
                faskes_nama = row['lokasi_faskes'].replace('Puskesmas ', '') if pd.notna(row['lokasi_faskes']) and row['lokasi_faskes'] != '-' else '-'
                tgl_format = format_tanggal_indo(row['Tanggal Cek Fisik'])
                
                teks_hasil_ai = row['hasil_risiko'] if row['status_pemeriksaan'] == 'Selesai Diperiksa' else "Belum Dihitung"
                
                html_tabel += f"""<div style='display: flex; align-items: center; border-bottom: 1px solid #f1f5f9; padding: 1rem 0;'>
<div style='flex: 0.6; font-size: 0.85rem; font-weight: 600; color: #475569;'>Ke-{i + 1}</div>
<div style='flex: 1.5; font-size: 0.85rem; font-weight: 600; color: #0f172a;'>{tgl_format}</div>
<div style='flex: 1.2; font-size: 0.85rem; font-weight: 600; color: #0f172a;'>{antrean}</div>
<div style='flex: 1.5; font-size: 0.85rem; font-weight: 500; color: #0f172a;'>{faskes_nama}</div>
<div style='flex: 1;'>
<span style='background-color: {st_bg}; color: {st_color}; padding: 4px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700;'>{st_text}</span>
</div>
<div style='flex: 1.5; font-size: 0.85rem; font-weight: 600; color: #0f172a; display: flex; align-items: center; gap: 6px;'>
<span style='display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: {dot_color};'></span>
{teks_hasil_ai}
</div>
</div>\n"""
                
        html_tabel += "</div>"
        st.markdown(html_tabel, unsafe_allow_html=True)
        
        st.markdown("""<div style='background-color: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);'>
<h3 style='margin: 0 0 0.2rem 0; font-size: 1.1rem; font-weight: 800; color: #0f172a;'>Trend Parameter Kesehatan</h3>
<p style='margin: 0 0 1.5rem 0; font-size: 0.85rem; color: #64748b;'>Visualisasi perkembangan parameter klinis Anda.</p>""", unsafe_allow_html=True)
        
        # HANYA GAMBAR GRAFIK JIKA ADA DATA "SELESAI" YANG VALID
        if ada_data_selesai:
            df_plot = df_selesai.copy() 
            for col in ['hb_darah', 'lila', 'imt']:
                if col in df_plot.columns: df_plot[col] = pd.to_numeric(df_plot[col], errors='coerce')
            
            df_plot_clean = df_plot.dropna(subset=['hb_darah', 'lila', 'imt'])
            
            if not df_plot_clean.empty:
                opsi_grafik = st.selectbox("Pilih Parameter Klinis:", ["Hemoglobin (Hb)", "Lingkar Lengan Atas (LILA)", "BMI (IMT)"], label_visibility="collapsed")
                map_col = {"Hemoglobin (Hb)": "hb_darah", "Lingkar Lengan Atas (LILA)": "lila", "BMI (IMT)": "imt"}
                target_col = map_col[opsi_grafik]
                
                x_data = df_plot_clean['Sesi ID'].tolist()
                y_data = df_plot_clean[target_col].tolist()
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=x_data, y=y_data, 
                    mode='lines+markers+text',
                    line=dict(color='#10b981', width=3),
                    marker=dict(size=10, color='white', line=dict(width=2, color='#10b981')),
                    fill='tozeroy', 
                    fillcolor='rgba(16, 185, 129, 0.1)',
                    text=[f"{v:.1f}" for v in y_data],
                    textposition="top center",
                    textfont=dict(color="#006c49", size=11, weight="bold")
                ))
                
                fig.update_layout(
                    margin=dict(l=0, r=0, t=30, b=0),
                    height=250,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False, zeroline=False, linecolor='#e2e8f0', tickfont=dict(color='#64748b', size=10)),
                    yaxis=dict(showgrid=True, gridcolor='#f1f5f9', zeroline=False, tickfont=dict(color='#64748b', size=10), showticklabels=False)
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
                if len(y_data) > 1:
                    selisih = y_data[-1] - y_data[-2]
                    arah = "peningkatan" if selisih > 0 else ("penurunan" if selisih < 0 else "kestabilan")
                    simbol = "+" if selisih > 0 else ""
                    analisis_teks = f"Tingkat {opsi_grafik} Anda menunjukkan **{arah} ({simbol}{selisih:.1f})** pada pemeriksaan terakhir dibandingkan sesi sebelumnya."
                else:
                    analisis_teks = f"Data dasar {opsi_grafik} Anda telah terekam. Lakukan pemeriksaan rutin untuk melihat tren perkembangan."
                    
                st.markdown(f"""<div style='background-color: #f8fafc; border-left: 4px solid #10b981; padding: 1rem; border-radius: 4px; margin-top: 1rem;'>
<p style='margin: 0; font-size: 0.8rem; font-weight: 700; color: #0f172a;'>📈 Analisis Trend</p>
<p style='margin: 5px 0 0 0; font-size: 0.85rem; color: #475569;'>{analisis_teks}</p>
</div>""", unsafe_allow_html=True)
            else:
                st.info("Grafik trend akan muncul setelah hasil rekam medis fisik Anda diinput oleh Tenaga Kesehatan.")
        else:
            st.info("Grafik trend akan muncul setelah hasil rekam medis fisik Anda diinput oleh Tenaga Kesehatan.")
            
        st.markdown("</div>", unsafe_allow_html=True)