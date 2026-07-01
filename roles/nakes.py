import streamlit as st
import pandas as pd
import numpy as np
import io
import datetime
import plotly.express as px
import plotly.graph_objects as go
import re
from modules.database import get_all_patients, get_db_connection

# Mapping Kode Puskesmas untuk ditampilkan di Dropdown Filter
KODE_FASKES = {
    "Puskesmas Penumping": "PNP",
    "Puskesmas Jayengan": "JYG",
    "Puskesmas Sangkrah": "SKR",
    "Puskesmas Pucang Sawit": "PCS",
    "Puskesmas Nusukan": "NSK"
}

def format_tanggal_indo(tgl_string):
    """Fungsi helper untuk menerjemahkan format tanggal ke Bahasa Indonesia"""
    if tgl_string == '-' or not tgl_string or pd.isna(tgl_string): return '-'
    try:
        dt_obj = datetime.datetime.strptime(tgl_string, '%d %B %Y')
        hari_indo = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"][dt_obj.weekday()]
        bulan_indo = {"January": "Jan", "February": "Feb", "March": "Mar", "April": "Apr", "May": "Mei", "June": "Jun", "July": "Jul", "August": "Agt", "September": "Sep", "October": "Okt", "November": "Nov", "December": "Des"}
        return f"{hari_indo}, {dt_obj.day} {bulan_indo.get(dt_obj.strftime('%B'), dt_obj.strftime('%B'))} {dt_obj.year}"
    except:
        return tgl_string

def generate_ai_recommendation(imt, lila, hb, prediksi, pendapatan, air, faskes, pendidikan, gizi):
    """
    Fungsi cerdas bertingkat berdasarkan batas ambang (cut-off) resmi Kemenkes RI,
    WHO, dan konseptual malnutrisi UNICEF (Faktor Klinis & Sosio-Demografi).
    """
    catatan = []
    
    # 1. ANALISIS KESIMPULAN STATUS AI
    if prediksi == 2:
        catatan.append("⚠️ [STATUS PRIORITAS: RISIKO TINGGI STUNTING]")
        catatan.append("- Pasien menunjukkan akumulasi indikator klinis kritis. Diperlukan rujukan prioritas ke Dokter Puskesmas dan intervensi gizi spesifik segera.")
    elif prediksi == 1:
        catatan.append("🟡 [STATUS WASPADA: RENTAN RISIKO STUNTING]")
        # Logika Tambahan: Deteksi jika fisiknya normal tapi sosial demografinya rendah
        if hb >= 12.0 and lila >= 23.5 and 18.5 <= imt <= 25.0:
            catatan.append("- Peringatan Khusus: Meskipun kondisi pemeriksaan fisik/klinis saat ini terpantau NORMAL, pasien berada dalam kategori RENTAN karena adanya kerentanan pada faktor pendukung sosio-demografi dan sanitasi lingkungan yang rawan memicu malnutrisi di kemudian hari.")
        else:
            catatan.append("- Ditemukan beberapa parameter fungsional yang kurang optimal. Memerlukan penanganan preventif dini agar tidak memburuk menjadi kondisi risiko tinggi.")
    else:
        catatan.append("✅ [STATUS AMAN: RISIKO RENDAH / NORMAL]")
        catatan.append("- Kondisi antropometri, klinis, lingkungan, dan sosial-ekonomi pasien terpantau sangat mendukung kesiapan reproduksi sehat.")
    
    # 2. ANALISIS PILAR KLINIS (ANTROPOMETRI)
    catatan.append("\n🩺 [ANALISIS KLINIS & ANTROPOMETRI]:")
    if hb < 12.0:
        catatan.append(f"- Kadar Hb {hb} g/dL (🔴 ANEMIA): Suplai oksigen dan nutrisi mikro ke janin rawan terhambat. Rekomendasi: Konsumsi Tablet Tambah Darah (TTD) 1 tablet/hari secara konsisten ditambah Vitamin C.")
    else:
        catatan.append(f"- Kadar Hb {hb} g/dL (🟢 NORMAL): Kadar hemoglobin memenuhi standar kesehatan.")

    if lila < 23.5:
        catatan.append(f"- Ukuran LILA {lila} cm (🔴 KURANG ENERGI KRONIS / KEK): Menandakan kekurangan cadangan energi jangka panjang. Pasien wajib masuk program PMT (Pemberian Makanan Tambahan) Pemulihan.")
    else:
        catatan.append(f"- Ukuran LILA {lila} cm (🟢 NORMAL): Cadangan otot dan lemak tubuh mencukupi.")

    if imt < 18.5:
        catatan.append(f"- Nilai IMT {imt:.1f} (🔴 UNDERWEIGHT / KURUS): Perlu peningkatan densitas kalori harian lewat gizi makro seimbang.")
    elif 18.5 <= imt <= 25.0:
        catatan.append(f"- Nilai IMT {imt:.1f} (🟢 NORMAL / IDEAL): Berat badan proporsional.")
    else:
        catatan.append(f"- Nilai IMT {imt:.1f} (🟡 OVERWEIGHT): Disarankan pengaturan pola makan padat nutrisi terkontrol kalori.")

    # 3. ANALISIS PILAR SOSIO-DEMOGRAFI & LINGKUNGAN (Tambahan Baru)
    catatan.append("\n🌍 [ANALISIS FAKTOR DETERMINAN LINGKUNGAN & SOSIAL]:")
    
    # Faktor Ekonomi & Pangan
    if pendapatan == 1:
        catatan.append("- Pendapatan Keluarga (🔴 RENDAH): Berisiko membatasi daya beli pangan bergizi seimbang (protein hewani). Rekomendasi: Daftarkan pasien sebagai prioritas penerima bantuan jaminan sosial/pangan daerah.")
    else:
        catatan.append("- Pendapatan Keluarga (🟢 CUKUP/TINGGI): Daya beli pangan mencukupi untuk pemenuhan gizi mandiri.")
        
    # Faktor Sanitasi Penyakit Infeksi
    if air == 0:
        catatan.append("- Akses Air Bersih (🔴 TIDAK ADA / KURANG LAYAK): Meningkatkan risiko infeksi bakteri saluran pencernaan (diare berulang) yang merusak penyerapan usus. Rekomendasi: Edukasi nakes mengenai perebusan air hingga matang sempurna dan koordinasikan dengan program sanitasi kelurahan.")
    else:
        catatan.append("- Akses Air Bersih (🟢 LAYAK): Mengurangi risiko penyakit infeksi lingkungan.")

    # Faktor Literasi Pola Asuh
    if gizi <= 2 or pendidikan == 1:
        catatan.append(f"- Pengetahuan Gizi & Pendidikan (🔴 RENDAH - Skor: {gizi}/5): Berisiko memicu pola asuh dan pengolahan makanan yang keliru. Rekomendasi: Berikan konseling gizi personal mengenai piring makanku dan demonstrasi masak MP-ASI/Pangan Sehat di Puskesmas.")
    else:
        catatan.append(f"- Pengetahuan Gizi & Pendidikan (🟢 BAIK - Skor: {gizi}/5): Tingkat literasi kesehatan sangat mendukung pola asuh mandiri.")

    # Faktor Deteksi Dini
    if faskes == 0:
        catatan.append("- Akses Fasilitas Kesehatan (🔴 SULIT/TERBATAS): Keterbatasan jangkauan rawan menunda intervensi darurat. Rekomendasi: Optimalkan pemantauan berkala via kunjungan rumah kader kesehatan/Posyandu terdekat.")
        
    return "\n".join(catatan)

def show_nakes_main_menu():
    """
    Dashboard Tenaga Kesehatan: Filter Global, Metrik, Tabel Antrean, dan Form Sesi Aktif.
    """
    st.markdown("<div style='margin-bottom: 2rem;'><h1 style='color: #0f172a; font-size: 2.2rem; font-weight: 800; margin-bottom: 0.2rem; margin-top: 0;'>Dashboard Tenaga Kesehatan</h1><p style='color: #64748b; font-size: 1rem; margin-top: 0;'>Kelola antrean pemeriksaan fisik pasien KIA dan input parameter klinis untuk diagnosis AI.</p></div>", unsafe_allow_html=True)

    df_patients = get_all_patients()
    if df_patients.empty:
        st.info("Belum ada data pasien di dalam sistem.")
        return

    with st.container(border=True):
        col_f, col_d, col_s = st.columns(3)
        list_faskes = ["Semua Puskesmas"] + list(KODE_FASKES.keys())
        with col_f: filter_faskes = st.selectbox("Pilih Faskes / Puskesmas", list_faskes)
        with col_d: filter_tgl = st.date_input("Tanggal Kunjungan", value=None, format="DD/MM/YYYY")
        list_sesi = ["Semua Sesi", "Sesi 1 (07.30 - 09.00)", "Sesi 2 (09.00 - 10.00)", "Sesi 3 (10.00 - 11.00)", "Sesi 4 (11.00 - 12.00)"]
        with col_s: filter_sesi = st.selectbox("Filter Sesi", list_sesi)

    df_filtered = df_patients.copy()
    
    # --- PERBAIKAN: Sembunyikan pasien tanpa antrean DAN pasien yang statusnya di-reset (DRAFT) oleh Admin ---
    kondisi_punya_antrean = df_filtered['no_antrean'].notna() & \
                            (df_filtered['no_antrean'].astype(str).str.strip() != '') & \
                            (df_filtered['no_antrean'].astype(str).str.strip() != '-') & \
                            (df_filtered['no_antrean'].astype(str).str.lower() != 'none')
                            
    kondisi_status_valid = df_filtered['status_pemeriksaan'].isin(['Menunggu Pemeriksaan Fisik', 'Selesai Diperiksa'])
    
    df_filtered = df_filtered[kondisi_punya_antrean & kondisi_status_valid]
    # ---------------------------------------------------------------------------------------------------------
    
    if filter_faskes != "Semua Puskesmas":
        df_filtered = df_filtered[df_filtered['lokasi_faskes'] == filter_faskes]
        
    str_tgl_display = "Semua Tanggal"
    if filter_tgl is not None:
        tgl_format_db_1 = filter_tgl.strftime('%d %B %Y') 
        tgl_format_db_2 = filter_tgl.strftime('%d/%m/%Y') 
        df_filtered = df_filtered[df_filtered['jadwal_kunjungan'].str.contains(tgl_format_db_1, case=False, na=False) | df_filtered['jadwal_kunjungan'].str.contains(tgl_format_db_2, case=False, na=False)]
        str_tgl_display = filter_tgl.strftime('%d/%m/%Y')
        
    if filter_sesi != "Semua Sesi":
        if "Sesi 1" in filter_sesi:
            kondisi_sesi = df_filtered['jadwal_kunjungan'].str.contains('Sesi 1|07:30|07\.30|08:00|08\.00|08:30|08\.30', case=False, na=False)
        elif "Sesi 2" in filter_sesi:
            s2_raw = df_filtered['jadwal_kunjungan'].str.contains('Sesi 2|09:00|09\.00|09:30|09\.30', case=False, na=False)
            s1_raw = df_filtered['jadwal_kunjungan'].str.contains('Sesi 1', case=False, na=False)
            kondisi_sesi = s2_raw & ~s1_raw
        elif "Sesi 3" in filter_sesi:
            s3_raw = df_filtered['jadwal_kunjungan'].str.contains('Sesi 3|10:00|10\.00|10:30|10\.30', case=False, na=False)
            s2_raw = df_filtered['jadwal_kunjungan'].str.contains('Sesi 2', case=False, na=False)
            kondisi_sesi = s3_raw & ~s2_raw
        elif "Sesi 4" in filter_sesi:
            s4_raw = df_filtered['jadwal_kunjungan'].str.contains('Sesi 4|11:00|11\.00|11:30|11\.30|12:00|12\.00', case=False, na=False)
            s3_raw = df_filtered['jadwal_kunjungan'].str.contains('Sesi 3', case=False, na=False)
            kondisi_sesi = s4_raw & ~s3_raw
        else:
            kondisi_sesi = df_filtered['jadwal_kunjungan'].str.contains(filter_sesi, case=False, na=False)
            
        df_filtered = df_filtered[kondisi_sesi]

    total_antrean = len(df_filtered)
    menunggu = len(df_filtered[df_filtered['status_pemeriksaan'] == 'Menunggu Pemeriksaan Fisik'])
    selesai = len(df_filtered[df_filtered['status_pemeriksaan'] == 'Selesai Diperiksa'])

    metrik_html = f"<div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-bottom: 2rem;'>"
    metrik_html += f"<div style='background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center;'><div><p style='margin:0; color:#64748b; font-size:0.85rem; font-weight:700;'>Total Antrean Terpilih</p><h2 style='margin:0; color:#0f172a; font-size:2rem; font-weight:800;'>{total_antrean} <span style='font-size:1rem; color:#94a3b8;'>Pasien</span></h2></div><div style='background:#f1f5f9; padding:12px; border-radius:12px;'><span class='material-symbols-outlined' style='color:#64748b; font-size:28px;'>groups</span></div></div>"
    metrik_html += f"<div style='background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center;'><div><p style='margin:0; color:#64748b; font-size:0.85rem; font-weight:700;'>Menunggu Cek Fisik</p><h2 style='margin:0; color:#0f172a; font-size:2rem; font-weight:800;'>{menunggu} <span style='font-size:1rem; color:#94a3b8;'>Pasien</span></h2></div><div style='background:#fffbeb; padding:12px; border-radius:12px;'><span class='material-symbols-outlined' style='color:#f59e0b; font-size:28px;'>timer</span></div></div>"
    metrik_html += f"<div style='background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center;'><div><p style='margin:0; color:#64748b; font-size:0.85rem; font-weight:700;'>Selesai Diperiksa</p><h2 style='margin:0; color:#0f172a; font-size:2rem; font-weight:800;'>{selesai} <span style='font-size:1rem; color:#94a3b8;'>Pasien</span></h2></div><div style='background:#ecfdf5; padding:12px; border-radius:12px;'><span class='material-symbols-outlined' style='color:#10b981; font-size:28px;'>check_circle</span></div></div>"
    metrik_html += "</div>"
    st.markdown(metrik_html, unsafe_allow_html=True)

    col_kiri, col_kanan = st.columns([1.6, 1])

    with col_kiri:
        st.markdown(f"<div style='margin-bottom: 1rem;'><h3 style='margin: 0; font-size: 1.2rem; font-weight: 800; color: #0f172a;'>Antrean Pasien Hari Ini</h3><p style='margin: 0; font-size: 0.85rem; color: #64748b;'>Menampilkan data: {filter_faskes} | {str_tgl_display} | {filter_sesi}</p></div>", unsafe_allow_html=True)
        
        html_tabel = "<div style='background-color: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);'>"
        html_tabel += "<div style='display: flex; border-bottom: 2px solid #f1f5f9; padding-bottom: 0.75rem; margin-bottom: 0.5rem;'><div style='flex: 0.8; font-size: 0.7rem; font-weight: 700; color: #64748b;'>KE-</div><div style='flex: 1.5; font-size: 0.7rem; font-weight: 700; color: #64748b;'>NO. ANTREAN</div><div style='flex: 2; font-size: 0.7rem; font-weight: 700; color: #64748b;'>ID & NAMA PASIEN</div><div style='flex: 1.5; font-size: 0.7rem; font-weight: 700; color: #64748b;'>SESI/WAKTU</div><div style='flex: 1; font-size: 0.7rem; font-weight: 700; color: #64748b;'>STATUS</div></div>"
        html_tabel += "<div style='max-height: 320px; overflow-y: auto; padding-right: 5px; scrollbar-width: thin;'>"
        
        for i, (idx, row) in enumerate(df_filtered.iterrows()):
            if row['status_pemeriksaan'] == 'Selesai Diperiksa':
                st_color, st_bg, st_text = "#047857", "#dcfce7", "SELESAI"
            elif row['status_pemeriksaan'] == 'Menunggu Pemeriksaan Fisik':
                st_color, st_bg, st_text = "#b45309", "#fef3c7", "MENUNGGU"
            else:
                st_color, st_bg, st_text = "#475569", "#f1f5f9", "DRAFT"
                
            antrean = row['no_antrean'] if pd.notna(row['no_antrean']) else "-"
            jadwal_str = str(row['jadwal_kunjungan'])
            sesi_waktu = jadwal_str.split(' - ')[1] if ' - ' in jadwal_str else (jadwal_str[-15:] if len(jadwal_str) > 15 else jadwal_str)
            
            html_tabel += f"<div style='display: flex; align-items: center; border-bottom: 1px solid #f1f5f9; padding: 0.8rem 0;'><div style='flex: 0.8; font-size: 0.85rem; font-weight: 600; color: #475569;'>P-{i + 1:02d}</div><div style='flex: 1.5; font-size: 0.85rem; font-weight: 700; color: #0f172a;'>{antrean}</div><div style='flex: 2; display: flex; flex-direction: column;'><span style='font-size: 0.75rem; color: #64748b;'>{row['id_pasien']}</span><span style='font-size: 0.85rem; font-weight: 600; color: #006c49;'>{row['nama']}</span></div><div style='flex: 1.5; font-size: 0.85rem; font-weight: 500; color: #475569;'>{sesi_waktu}</div><div style='flex: 1;'><span style='background-color: {st_bg}; color: {st_color}; padding: 4px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700;'>{st_text}</span></div></div>"
            
        html_tabel += "</div></div>"
        st.markdown(html_tabel, unsafe_allow_html=True)

    with col_kanan:
        st.markdown("<h3 style='margin: 0 0 1rem 0; font-size: 1.2rem; font-weight: 800; color: #0f172a;'>Sesi Pemeriksaan Aktif</h3>", unsafe_allow_html=True)
        
        df_menunggu = df_filtered[df_filtered['status_pemeriksaan'] == 'Menunggu Pemeriksaan Fisik']
        list_pilihan = []
        for _, row in df_menunggu.iterrows():
            list_pilihan.append(f"{row['no_antrean']} | {row['nama']} (ID: {row['id_pasien']}) | REKAM-{row['id_rekam']}")
            
        pasien_terpilih = st.selectbox("Pilih Pasien untuk Diperiksa:", list_pilihan, index=None, placeholder="Pilih pasien dari antrean...", label_visibility="collapsed")
        
        with st.container(border=True):
            if not pasien_terpilih:
                st.info("Silakan pilih pasien pada dropdown di atas untuk memulai pemeriksaan fisik dan prediksi AI.")
            else:
                # --- SEMUA KODE DI BAWAH INI HARUS MENJOROK KE DALAM BLOK ELSE ---
                id_rekam_aktif = int(pasien_terpilih.split(" | ")[-1].replace("REKAM-", ""))
                data_aktif = df_patients[df_patients['id_rekam'] == id_rekam_aktif].iloc[0]
                
                st.markdown(f"<div style='background: #f8fafc; border: 1px solid #e2e8f0; padding: 1rem; border-radius: 12px; display: flex; gap: 15px; align-items: center; margin-bottom: 1.5rem;'><div style='background: #d1fae5; min-width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center;'><span class='material-symbols-outlined' style='color: #047857;'>person</span></div><div><p style='margin: 0; font-weight: 800; color: #0f172a; font-size: 0.95rem;'>Pasien: {data_aktif['nama']} ({data_aktif['usia']} Tahun)</p><p style='margin: 0; font-size: 0.75rem; color: #64748b;'>ID: {data_aktif['id_pasien']} | No. Antrean: {data_aktif['no_antrean']}</p></div></div>", unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                with c1:
                    hb = st.number_input("Kadar Hb (g/dL)", min_value=4.0, max_value=20.0, value=None, placeholder="Ketik kadar Hb pasien...", step=0.1)
                    bb = st.number_input("Berat Badan (kg)", min_value=30.0, max_value=120.0, value=None, placeholder="Ketik berat badan (kg)...", step=0.1)
                with c2:
                    lila = st.number_input("Lingkar Lengan (LILA) (cm)", min_value=10.0, max_value=50.0, value=None, placeholder="Ketik ukuran LILA (cm)...", step=0.1)
                    tb = st.number_input("Tinggi Badan (cm)", min_value=120.0, max_value=200.0, value=None, placeholder="Ketik tinggi badan (cm)...", step=0.1)

                if 'id_rekam_sementara' not in st.session_state or st.session_state['id_rekam_sementara'] != id_rekam_aktif:
                    st.session_state['temp_hasil_ai'] = None
                    st.session_state['id_rekam_sementara'] = id_rekam_aktif

                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                
                # --- LOGIKA TOMBOL PREDIKSI DENGAN VALIDASI PENGAMAN ANTI-KOSONG ---
                if st.button("PROSES PREDIKSI RISIKO STUNTING (AI) 🧠", use_container_width=True):
                    if hb is None or bb is None or lila is None or tb is None:
                        st.error("⚠️ **Gagal Memproses:** Seluruh parameter pemeriksaan fisik (Kadar Hb, Berat Badan, LILA, dan Tinggi Badan) wajib diisi lengkap tanpa ada yang terlewat.")
                    else:
                        imt = bb / ((tb / 100) ** 2)
                        model = st.session_state['ai_model']
                        
                        v_pendapatan = int(data_aktif['pendapatan_bulanan']) if not pd.isna(data_aktif['pendapatan_bulanan']) else 2
                        v_air = int(data_aktif['akses_air_bersih']) if not pd.isna(data_aktif['akses_air_bersih']) else 1
                        v_faskes = int(data_aktif['akses_layanan_kesehatan']) if not pd.isna(data_aktif['akses_layanan_kesehatan']) else 1
                        v_pendidikan = int(data_aktif['pendidikan_terakhir']) if not pd.isna(data_aktif['pendidikan_terakhir']) else 2
                        v_gizi = int(data_aktif['skor_pengetahuan_gizi']) if not pd.isna(data_aktif['skor_pengetahuan_gizi']) else 3
                        
                        input_features = np.array([[int(data_aktif['usia']), float(bb), float(tb), float(hb), float(imt), float(lila), v_pendapatan, v_air, v_faskes, v_pendidikan, v_gizi]])
                        prediksi = model.predict(input_features)[0]
                        probabilitas = model.predict_proba(input_features)[0][prediksi] * 100
                        
                        if prediksi == 2:
                            hasil_teks = f"RISIKO TINGGI ({probabilitas:.1f}%)"
                            badge_bg = "#fee2e2"
                            badge_color = "#dc2626"
                        elif prediksi == 1:
                            hasil_teks = f"RENTAN ({probabilitas:.1f}%)"
                            badge_bg = "#fffbeb"
                            badge_color = "#d97706"
                        else:
                            hasil_teks = f"RISIKO RENDAH / NORMAL ({probabilitas:.1f}%)"
                            badge_bg = "#d1fae5"
                            badge_color = "#047857"
                        
                        rekomendasi_ai_otomatis = generate_ai_recommendation(
                        imt=imt, 
                        lila=lila, 
                        hb=hb, 
                        prediksi=prediksi,
                        pendapatan=v_pendapatan,
                        air=v_air,
                        faskes=v_faskes,
                        pendidikan=v_pendidikan,
                        gizi=v_gizi 
                        )
                        
                        
                        st.session_state['temp_hasil_ai'] = {
                            'imt': imt, 'bb': bb, 'tb': tb, 'hb': hb, 'lila': lila,
                            'hasil_teks': hasil_teks, 'bg': badge_bg, 'color': badge_color,
                            'rekomendasi_ai': rekomendasi_ai_otomatis
                        }
                        st.rerun()

               # --- PANEL AREA HASIL PREDIKSI & INPUT REKOMENDASI NAKES ---
                if st.session_state.get('temp_hasil_ai'):
                    res = st.session_state['temp_hasil_ai']
                    
                    # 1. TAMPILAN KARTU UTAMA HASIL AI
                    st.markdown(f"""
                    <div style='background: {res['bg']}; border: 1px solid {res['color']}; padding: 1.5rem; border-radius: 12px; text-align: center; margin-top: 1rem; margin-bottom: 1.5rem;'>
                        <p style='margin: 0; font-size: 0.8rem; font-weight: 700; color: {res['color']}; opacity: 0.8; letter-spacing: 1px;'>HASIL KEPUTUSAN KLASIFIKASI AI (IMT: {res['imt']:.1f})</p>
                        <h2 style='margin: 0.2rem 0 0 0; color: {res['color']}; font-size: 1.6rem; font-weight: 800;'>{res['hasil_teks']}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 2. CATATAN OTOMATIS BERBASIS POHON KEPUTUSAN RANDOM FOREST
                    st.markdown("<p style='font-size: 0.85rem; font-weight: 700; color: #1e293b; margin-bottom: 0.2rem;'>🤖 Rekomendasi & Hasil Diagnosis Otomatis Sistem AI</p>", unsafe_allow_html=True)
                    
                    # Mengubah karakter newline (\n) dari fungsi rekomendasi menjadi tag <br> agar rapi di HTML Streamlit
                    html_rekomendasi_ai = res['rekomendasi_ai'].replace('\n', '<br>')
                    st.markdown(f"""
                    <div style='background-color: #f8fafc; padding: 16px; border-radius: 12px; border-left: 5px solid {res['color']}; border-dash: 1px solid #e2e8f0; margin-bottom: 1.5rem; font-size: 0.85rem; color: #334155; line-height: 1.6; font-family: sans-serif;'>
                        {html_rekomendasi_ai}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 3. PANEL INPUT RESEP/TINDAKAN OLEH TENAGA KESEHATAN AKTUAL
                    st.markdown("<p style='font-size: 0.85rem; font-weight: 700; color: #1e293b; margin-bottom: 0.2rem;'>✍️ Catatan Tambahan, Resep Obat & Intervensi (Nakes)</p>", unsafe_allow_html=True)
                    rekomendasi_nakes = st.text_area("Rekomendasi Nakes", placeholder="Ketikkan resep obat faskes (misal: PMT biskuit, Vitamin C, TTD), jadwal kontrol ulang, atau instruksi rujukan di sini...", label_visibility="collapsed")
                    
                    # 4. PROSES PENYIMPANAN PERMANEN KE DATABASE POSTGRESQL
                    if st.button("SIMPAN & CETAK REKAM MEDIS", type="primary", use_container_width=True):
                        if not rekomendasi_nakes.strip():
                            st.error("⚠️ Gagal Menyimpan! Sebagai Tenaga Kesehatan, Anda wajib menuliskan instruksi medis/resep tambahan pada kolom di atas.")
                        else:
                            # Menggabungkan hasil analisis sistem AI dan resep manual dari Nakes ke dalam satu kolom teks database
                            rekomendasi_gabungan = f"[ANALISIS DINAMIS SISTEM AI]:\n{res['rekomendasi_ai']}\n\n[REKOMENDASI & INTERVENSI NAKES]:\n{rekomendasi_nakes}"
                            
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("""
                            UPDATE pasien_tb SET 
                                berat_badan = %s, tinggi_badan = %s, hb_darah = %s, imt = %s, lila = %s,
                                status_pemeriksaan = 'Selesai Diperiksa', hasil_risiko = %s, rekomendasi = %s
                            WHERE id_rekam = %s
                            """, (res['bb'], res['tb'], res['hb'], res['imt'], res['lila'], res['hasil_teks'], rekomendasi_gabungan, id_rekam_aktif))
                            conn.commit()
                            conn.close()
                            
                            try:
                                st.cache_data.clear()
                            except Exception:
                                pass
                            
                            st.session_state['temp_hasil_ai'] = None
                            st.success("🎉 Rekam Medis Berhasil Terkunci di Database! Status Pasien: Selesai Diperiksa.")
                            st.rerun()
                            
                            
def show_nakes_history_dashboard():
    """
    Dashboard Riwayat & Statistik Komprehensif Nakes dengan Fitur Filter Data.
    Ditulis dengan HTML single-line (tanpa indent) agar terhindar dari bug kode Markdown Streamlit.
    """
    df = get_all_patients()
    df_selesai_raw = df[df['status_pemeriksaan'] == 'Selesai Diperiksa'].copy()
    
    # 1. HEADER SECTION
    col_header1, col_header2 = st.columns([2, 1])
    with col_header1:
        st.markdown("<h1 style='color: #0f172a; font-size: 2.2rem; font-weight: 800; margin: 0;'>Riwayat & Statistik Pasien</h1><p style='color: #64748b; font-size: 1rem;'>Analisis komprehensif data klinis, sosiodemografi, dan rekam medis pasien KIA.</p>", unsafe_allow_html=True)

    if df_selesai_raw.empty:
        st.info("Belum ada data pasien yang selesai diperiksa. Statistik akan muncul di sini setelah ada pemeriksaan yang diselesaikan.")
        return
        
    # 2. FILTER BAR SECTION
    with st.container(border=True):
        st.markdown("<p style='font-size: 0.85rem; font-weight: 700; color: #64748b; margin-bottom: 0.5rem; letter-spacing: 0.5px;'>🔍 FILTER DATA STATISTIK</p>", unsafe_allow_html=True)
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            faskes_opts = ["Semua Puskesmas"] + sorted([f for f in df_selesai_raw['lokasi_faskes'].unique() if pd.notna(f) and str(f).strip() not in ['', '-']])
            filter_faskes = st.selectbox("Lokasi Faskes", faskes_opts, label_visibility="collapsed")
        with col_f2:
            kec_opts = ["Semua Kecamatan"] + sorted([k for k in df_selesai_raw['alamat_kecamatan'].unique() if pd.notna(k) and str(k).strip() not in ['', '-']])
            filter_kec = st.selectbox("Kecamatan Pasien", kec_opts, label_visibility="collapsed")

    # PROSES FILTERING DATA
    df_selesai = df_selesai_raw.copy()
    if filter_faskes != "Semua Puskesmas":
        df_selesai = df_selesai[df_selesai['lokasi_faskes'] == filter_faskes]
    if filter_kec != "Semua Kecamatan":
        df_selesai = df_selesai[df_selesai['alamat_kecamatan'] == filter_kec]
        
    # RENDER TOMBOL EXPORT (DI KANAN ATAS, MENGGUNAKAN DATA YANG SUDAH DIFILTER)
    with col_header2:
        st.markdown("<br>", unsafe_allow_html=True)
        if not df_selesai.empty:
            cols_export = [col for col in ['id_rekam', 'id_pasien', 'nama', 'email', 'no_hp', 'alamat', 'alamat_kecamatan', 'usia', 'lokasi_faskes', 'jadwal_kunjungan', 'berat_badan', 'tinggi_badan', 'imt', 'lila', 'hb_darah', 'hasil_risiko', 'rekomendasi', 'tanggal_pengisian'] if col in df_selesai.columns]
            df_export = df_selesai[cols_export].copy()
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Export Data Filtered (.CSV)", data=csv, file_name=f'Laporan_KIA_{filter_faskes}_{filter_kec}.csv', mime='text/csv', type="primary", use_container_width=True)

    if df_selesai.empty:
        st.warning(f"Tidak ada data rekam medis pasien yang sesuai dengan filter lokasi: {filter_faskes} & {filter_kec}.")
        return

    for col in ['lila', 'imt', 'hb_darah', 'usia']:
        df_selesai[col] = pd.to_numeric(df_selesai[col], errors='coerce')

    # 3. TOP ROW: CLINICAL & MAIN METRICS (MUTAKHIR: MENDUKUNG 3 LABEL STATUS)
    total_pasien = len(df_selesai)
    risiko_tinggi = len(df_selesai[df_selesai['hasil_risiko'].str.contains('TINGGI', case=False, na=False)])
    rentan = len(df_selesai[df_selesai['hasil_risiko'].str.contains('RENTAN', case=False, na=False)])
    normal = total_pasien - risiko_tinggi - rentan
    
    avg_lila = df_selesai['lila'].mean()
    avg_imt = df_selesai['imt'].mean()
    avg_hb = df_selesai['hb_darah'].mean()

    st.markdown("<style>.metric-card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); } .metric-title { font-size: 0.8rem; color: #64748b; font-weight: 700; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.5px; } .metric-val { font-size: 1.8rem; font-weight: 800; color: #0f172a; margin: 0; line-height: 1; } .metric-sub { font-size: 0.85rem; font-weight: 600; margin-top: 0.2rem; }</style>", unsafe_allow_html=True)

    # Memperluas baris menjadi 7 kolom agar Kartu Penghitungan 'Rentan' termuat seimbang
    m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
    m1.markdown(f"<div class='metric-card'><div class='metric-title'>Total Diperiksa</div><p class='metric-val'>{total_pasien}</p><p class='metric-sub' style='color:#64748b;'>Data Filter</p></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='metric-card' style='border-bottom: 4px solid #ef4444;'><div class='metric-title'>Risiko Tinggi</div><p class='metric-val' style='color:#ef4444;'>{risiko_tinggi}</p><p class='metric-sub' style='color:#ef4444;'>{(risiko_tinggi/total_pasien)*100 if total_pasien > 0 else 0:.1f}%</p></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='metric-card' style='border-bottom: 4px solid #f59e0b;'><div class='metric-title'>Status Rentan</div><p class='metric-val' style='color:#d97706;'>{rentan}</p><p class='metric-sub' style='color:#d97706;'>{(rentan/total_pasien)*100 if total_pasien > 0 else 0:.1f}%</p></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='metric-card' style='border-bottom: 4px solid #10b981;'><div class='metric-title'>Normal / Aman</div><p class='metric-val' style='color:#10b981;'>{normal}</p><p class='metric-sub' style='color:#10b981;'>{(normal/total_pasien)*100 if total_pasien > 0 else 0:.1f}%</p></div>", unsafe_allow_html=True)
    m5.markdown(f"<div class='metric-card'><div class='metric-title'>Rata-rata LILA</div><p class='metric-val'>{avg_lila if pd.notna(avg_lila) else 0:.1f}</p><p class='metric-sub' style='color:#64748b;'>cm</p></div>", unsafe_allow_html=True)
    m6.markdown(f"<div class='metric-card'><div class='metric-title'>Rata-rata IMT</div><p class='metric-val'>{avg_imt if pd.notna(avg_imt) else 0:.1f}</p><p class='metric-sub' style='color:#64748b;'>kg/m²</p></div>", unsafe_allow_html=True)
    hb_color = "#ef4444" if avg_hb < 12.0 else "#0f172a"
    m7.markdown(f"<div class='metric-card'><div class='metric-title'>Rata-rata Hb</div><p class='metric-val' style='color:{hb_color};'>{avg_hb if pd.notna(avg_hb) else 0:.1f}</p><p class='metric-sub' style='color:#64748b;'>g/dL</p></div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 4. MIDDLE SECTION: SOCIO-DEMOGRAPHIC INSIGHTS
    st.markdown("<h3 style='font-size: 1.2rem; font-weight: 800; color: #0f172a; margin-bottom: 1rem;'>Profil Sosiodemografi & Lingkungan Pasien</h3>", unsafe_allow_html=True)
    
    avg_usia = df_selesai['usia'].mean()
    air_baik_pct = (len(df_selesai[df_selesai['akses_air_bersih'] == 1]) / total_pasien) * 100
    faskes_mudah_pct = (len(df_selesai[df_selesai['akses_layanan_kesehatan'] == 1]) / total_pasien) * 100
    
    pend_df = df_selesai['pendidikan_terakhir'].value_counts(normalize=True) * 100
    p_sd = pend_df.get(1, 0.0)
    p_sma = pend_df.get(2, 0.0)
    p_sarjana = pend_df.get(3, 0.0)
    
    uang_df = df_selesai['pendapatan_bulanan'].value_counts(normalize=True) * 100
    u_rendah = uang_df.get(1, 0.0)
    u_sedang = uang_df.get(2, 0.0)
    u_tinggi = uang_df.get(3, 0.0)
    
    gizi_df = df_selesai['skor_pengetahuan_gizi']
    gizi_baik_pct = (len(gizi_df[gizi_df >= 4]) / total_pasien) * 100
    gizi_rendah_pct = 100 - gizi_baik_pct

    html_demo = "<div style='background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; flex-wrap: wrap; gap: 2rem;'>"
    html_demo += "<div style='flex: 1; min-width: 250px;'><p style='font-size: 0.8rem; font-weight: 700; color: #64748b; letter-spacing: 0.5px; margin-bottom: 1rem;'>STATISTIK DASAR</p>"
    html_demo += f"<div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 0.5rem; margin-bottom: 1rem;'><span style='font-size: 0.9rem; font-weight: 600; color: #334155;'>Rata-rata Usia WUS</span><span style='font-size: 1rem; font-weight: 800; color: #047857;'>{avg_usia if pd.notna(avg_usia) else 0:.0f} Tahun</span></div>"
    html_demo += "<div style='margin-bottom: 0.5rem;'><div style='display: flex; justify-content: space-between; margin-bottom: 0.3rem;'><span style='font-size: 0.9rem; font-weight: 600; color: #334155;'>Tingkat Pengetahuan Gizi</span></div>"
    html_demo += f"<div style='width: 100%; background-color: #f1f5f9; border-radius: 999px; height: 8px; display: flex; overflow: hidden;'><div style='width: {gizi_rendah_pct}%; background-color: #f59e0b;'></div><div style='width: {gizi_baik_pct}%; background-color: #10b981;'></div></div>"
    html_demo += f"<div style='display: flex; justify-content: space-between; margin-top: 0.3rem;'><span style='font-size: 0.75rem; color: #64748b;'>Rendah ({gizi_rendah_pct:.0f}%)</span><span style='font-size: 0.75rem; color: #64748b;'>Baik ({gizi_baik_pct:.0f}%)</span></div></div></div>"
    
    html_demo += "<div style='flex: 1; min-width: 250px;'><p style='font-size: 0.8rem; font-weight: 700; color: #64748b; letter-spacing: 0.5px; margin-bottom: 1rem;'>LINGKUNGAN & SANITASI</p>"
    html_demo += f"<div style='margin-bottom: 1rem;'><div style='display: flex; justify-content: space-between; margin-bottom: 0.3rem;'><span style='font-size: 0.9rem; font-weight: 600; color: #334155;'>Akses Air Bersih Layak</span><span style='font-size: 0.9rem; font-weight: 800; color: #0f172a;'>{air_baik_pct:.0f}%</span></div><div style='width: 100%; background-color: #f1f5f9; border-radius: 999px; height: 8px; overflow: hidden;'><div style='width: {air_baik_pct}%; background-color: #047857; height: 100%; border-radius: 999px;'></div></div></div>"
    html_demo += f"<div style='margin-bottom: 1rem;'><div style='display: flex; justify-content: space-between; margin-bottom: 0.3rem;'><span style='font-size: 0.9rem; font-weight: 600; color: #334155;'>Akses Faskes (Mudah)</span><span style='font-size: 0.9rem; font-weight: 800; color: #0f172a;'>{faskes_mudah_pct:.0f}%</span></div><div style='width: 100%; background-color: #f1f5f9; border-radius: 999px; height: 8px; overflow: hidden;'><div style='width: {faskes_mudah_pct}%; background-color: #047857; height: 100%; border-radius: 999px;'></div></div></div></div>"
    
    html_demo += "<div style='flex: 1; min-width: 250px; display: flex; gap: 1rem;'><div style='flex: 1;'><p style='font-size: 0.8rem; font-weight: 700; color: #64748b; letter-spacing: 0.5px; margin-bottom: 1rem;'>PENDIDIKAN</p>"
    html_demo += f"<div style='display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.5rem;'><span style='color:#334155;'>SD/SMP</span><strong style='color:#0f172a;'>{p_sd:.0f}%</strong></div><div style='display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.5rem;'><span style='color:#334155;'>SMA/SMK</span><strong style='color:#0f172a;'>{p_sma:.0f}%</strong></div><div style='display: flex; justify-content: space-between; font-size: 0.85rem;'><span style='color:#334155;'>Diploma/S1</span><strong style='color:#0f172a;'>{p_sarjana:.0f}%</strong></div></div>"
    html_demo += "<div style='flex: 1;'><p style='font-size: 0.8rem; font-weight: 700; color: #64748b; letter-spacing: 0.5px; margin-bottom: 1rem;'>EKONOMI</p>"
    html_demo += f"<div style='display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.5rem;'><span style='color:#334155;'>Rendah</span><strong style='color:#0f172a;'>{u_rendah:.0f}%</strong></div><div style='display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.5rem;'><span style='color:#334155;'>Menengah</span><strong style='color:#0f172a;'>{u_sedang:.0f}%</strong></div><div style='display: flex; justify-content: space-between; font-size: 0.85rem;'><span style='color:#334155;'>Tinggi</span><strong style='color:#0f172a;'>{u_tinggi:.0f}%</strong></div></div></div></div>"
    
    st.markdown(html_demo, unsafe_allow_html=True)
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 5. VISUALIZATIONS ROWS (MENDUKUNG 3 LABEL PADA DONUT CHART)
    st.markdown("<h3 style='font-size: 1.2rem; font-weight: 800; color: #0f172a; margin-bottom: 1rem;'>Visualisasi & Distribusi Data</h3>", unsafe_allow_html=True)
    
    # PERSIAPAN DATA KECAMATAN
    kec_df = df_selesai['alamat_kecamatan'].value_counts().reset_index()
    kec_df.columns = ['Kecamatan', 'Jumlah']
    kec_df = kec_df[~kec_df['Kecamatan'].isin(['', '-', 'None', 'nan'])]
    
    # --- BARIS 1: 3 DONUT CHARTS ---
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("<div class='metric-card' style='height: 100%;'><h4 style='margin-top:0; font-size:1rem; color:#0f172a;'>Status Prediksi AI</h4>", unsafe_allow_html=True)
        # PENYEMPURNAAN: Menambahkan label 'Rentan' ke dalam Donut Chart Status AI
        proporsi_df = pd.DataFrame({
            'Status': ['Risiko Tinggi', 'Rentan', 'Normal / Aman'], 
            'Jumlah': [risiko_tinggi, rentan, normal]
        })
        fig1 = px.pie(proporsi_df, names='Status', values='Jumlah', hole=0.7, color='Status', 
                      color_discrete_map={'Risiko Tinggi': '#ef4444', 'Rentan': '#f59e0b', 'Normal / Aman': '#10b981'})
        fig1.update_traces(textposition='none') 
        fig1.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5), height=250)
        fig1.add_annotation(text=f"<b>{total_pasien}</b><br><span style='font-size:10px; color:gray;'>TOTAL</span>", x=0.5, y=0.5, showarrow=False, font=dict(size=24, color="#0f172a"))
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='metric-card' style='height: 100%;'><h4 style='margin-top:0; font-size:1rem; color:#0f172a;'>Sebaran per Puskesmas</h4>", unsafe_allow_html=True)
        faskes_df = df_selesai['lokasi_faskes'].value_counts().reset_index()
        faskes_df.columns = ['Faskes', 'Jumlah']
        faskes_df['Faskes'] = faskes_df['Faskes'].str.replace('Puskesmas ', '') 
        fig2 = px.pie(faskes_df, names='Faskes', values='Jumlah', hole=0.6, color_discrete_sequence=['#064e3b', '#047857', '#10b981', '#34d399', '#a7f3d0'])
        fig2.update_traces(textposition='none')
        fig2.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False, height=250)
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c3:
        st.markdown("<div class='metric-card' style='height: 100%;'><h4 style='margin-top:0; font-size:1rem; color:#0f172a;'>Sebaran per Kecamatan</h4>", unsafe_allow_html=True)
        if not kec_df.empty:
            fig3 = px.pie(kec_df, names='Kecamatan', values='Jumlah', hole=0.6, color_discrete_sequence=['#0ea5e9', '#38bdf8', '#7dd3fc', '#bae6fd', '#e0f2fe'])
            fig3.update_traces(textposition='none')
            fig3.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False, height=250)
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Data kecamatan tidak tersedia.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    # --- BARIS 2: 2 BAR CHARTS ---
    c4, c5 = st.columns(2)
    
    with c4:
        st.markdown("<div class='metric-card' style='height: 100%;'><h4 style='margin-top:0; font-size:1rem; color:#0f172a;'>Distribusi Faskes (Bar)</h4>", unsafe_allow_html=True)
        fig4 = go.Figure(go.Bar(x=faskes_df['Jumlah'][::-1], y=faskes_df['Faskes'][::-1], orientation='h', marker=dict(color='#047857', line=dict(width=0)), text=faskes_df['Jumlah'][::-1], textposition='outside'))
        fig4.update_layout(margin=dict(t=10, b=10, l=0, r=20), xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(showgrid=False), height=250, plot_bgcolor='white')
        st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c5:
        st.markdown("<div class='metric-card' style='height: 100%;'><h4 style='margin-top:0; font-size:1rem; color:#0f172a;'>Distribusi Kecamatan (Bar)</h4>", unsafe_allow_html=True)
        if not kec_df.empty:
            fig5 = go.Figure(go.Bar(x=kec_df['Jumlah'][::-1], y=kec_df['Kecamatan'][::-1], orientation='h', marker=dict(color='#0ea5e9', line=dict(width=0)), text=kec_df['Jumlah'][::-1], textposition='outside'))
            fig5.update_layout(margin=dict(t=10, b=10, l=0, r=20), xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(showgrid=False), height=250, plot_bgcolor='white')
            st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Data kecamatan tidak tersedia.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 6. BOTTOM SECTION: COMPLETE PATIENT DATABASE TABLE (MENDUKUNG BADGE RENTAN)
    st.markdown("<h3 style='font-size: 1.2rem; font-weight: 800; color: #0f172a; margin-bottom: 0.5rem;'>Database Rekam Medis Pasien</h3><p style='font-size: 0.9rem; color: #64748b; margin-bottom: 1rem;'>Menampilkan data lengkap dari pendaftaran akun hingga hasil pemeriksaan klinis.</p>", unsafe_allow_html=True)

    html_table_db = "<div style='background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 0.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.02);'>"
    html_table_db += "<div style='max-height: 500px; overflow: auto; scrollbar-width: thin; padding-right: 5px;'>"
    html_table_db += "<table style='width: 100%; border-collapse: collapse; text-align: left; white-space: nowrap; background-color: #ffffff;'>"
    html_table_db += "<thead style='position: sticky; top: 0; background-color: #ffffff; z-index: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'><tr style='border-bottom: 2px solid #e2e8f0;'>"
    
    cols_display = ['ID / NO ANTREAN', 'NAMA & KONTAK', 'ALAMAT PASIEN', 'LOKASI FASKES', 'TGL PERIKSA', 'KLINIS FISIK', 'SOSIOLOGIS DEMOGRAFIS', 'HASIL AI']
    
    for col in cols_display:
        html_table_db += f"<th style='padding: 12px 10px; color: #64748b; font-size: 0.75rem; font-weight: 700; background-color: #ffffff;'>{col}</th>"
    html_table_db += "</tr></thead><tbody>"

    df_db_sorted = df_selesai.sort_values(by='id_rekam', ascending=False)
    
    for _, row in df_db_sorted.iterrows():
        id_p = row.get('id_pasien', '-')
        nama = row.get('nama', '-')
        usia = row.get('usia', '-')
        if str(usia).replace('.','',1).isdigit():
            usia = f"{float(usia):.0f}"
            
        email_val = row.get('email', '')
        email_str = str(email_val) if pd.notna(email_val) and str(email_val).strip() not in ['', 'nan', 'None', '-'] else '-'
        
        hp_val = row.get('no_hp', '')
        hp_str = str(hp_val) if pd.notna(hp_val) and str(hp_val).strip() not in ['', 'nan', 'None', '-'] else '-'
        
        alamat_val = row.get('alamat', '')
        alamat_str = str(alamat_val) if pd.notna(alamat_val) and str(alamat_val).strip() not in ['', 'nan', 'None', '-'] else ''
        
        kec_val = str(row.get('alamat_kecamatan', '-')).title()
        
        if alamat_str and kec_val != "-":
            alamat_display = f"{alamat_str}<br><span style='color: #94a3b8; font-size: 0.7rem;'>Kec. {kec_val}</span>"
        elif kec_val != "-":
            alamat_display = f"<span style='color: #334155; font-size: 0.85rem;'>Kec. {kec_val}</span>"
        elif alamat_str:
            alamat_display = f"<span style='color: #334155; font-size: 0.85rem;'>{alamat_str}</span>"
        else:
            alamat_display = "-"
            
        antrean = str(row.get('no_antrean', '-'))
        
        faskes_str = f"Puskesmas {kec_val}" if kec_val != "-" else "Puskesmas Pusat"
        if pd.notna(row.get('lokasi_faskes')):
            faskes_str = row.get('lokasi_faskes')
            
        jadwal_raw = str(row.get('jadwal_kunjungan', '-')).strip()
        if pd.isna(jadwal_raw) or jadwal_raw == '-' or jadwal_raw == 'None' or jadwal_raw == '':
            tgl_str = format_tanggal_indo(row['Tanggal Cek Fisik']) if 'Tanggal Cek Fisik' in row else "-"
        else:
            match_jam = re.search(r'(\d{2}[:.]\d{2})', jadwal_raw)
            jam_terdeteksi = match_jam.group(1).replace('.', ':') if match_jam else ""
            tgl_whitespace_clean = " ".join(jadwal_raw.split())
            tgl_bersih = tgl_whitespace_clean
            if jam_terdeteksi:
                tgl_bersih = re.sub(r'\d{2}[:.]\d{2}', '', tgl_bersih)
            hapus_kata = ["Sesi 1", "Sesi 2", "Sesi 3", "Sesi 4", "Pukul", "WIB", "wib", "(", ")", "-", ","]
            for kata in hapus_kata:
                tgl_bersih = tgl_bersih.replace(kata, "")
            tgl_bersih = " ".join(tgl_bersih.split())
            if jam_terdeteksi:
                tgl_str = f"{tgl_bersih} - {jam_terdeteksi} WIB"
            else:
                tgl_str = f"{tgl_bersih}"
                
        tb = row.get('tinggi_badan', '-')
        bb = row.get('berat_badan', '-')
        hb = row.get('hb_darah', '-')
        lila = row.get('lila', '-')
        klinis_str = f"<span style='background:#f1f5f9; padding:2px 6px; border-radius:4px; font-size:0.7rem; font-weight:700; color:#475569;'>TB: {tb}</span> <span style='background:#f1f5f9; padding:2px 6px; border-radius:4px; font-size:0.7rem; font-weight:700; color:#475569;'>BB: {bb}</span> <br><div style='margin-top:4px;'></div><span style='background:#f1f5f9; padding:2px 6px; border-radius:4px; font-size:0.7rem; font-weight:700; color:#475569;'>Hb: {hb}</span> <span style='background:#f1f5f9; padding:2px 6px; border-radius:4px; font-size:0.7rem; font-weight:700; color:#475569;'>LILA: {lila}</span>"
        
        val_pendapatan = row.get('pendapatan_bulanan')
        val_air = row.get('akses_air_bersih')
        val_faskes = row.get('akses_layanan_kesehatan')
        val_pendidikan = row.get('pendidikan_terakhir')
        val_gizi = row.get('skor_pengetahuan_gizi', '-')
        
        pendapatan_kategori = "Rendah" if val_pendapatan == 1 else ("Sedang/Tinggi" if val_pendapatan in [2,3] else "-")
        air_kategori = "Ada" if val_air == 1 else ("Tidak" if pd.notna(val_air) and val_air != "-" else "-")
        faskes_kategori = "Mudah" if val_faskes == 1 else ("Sulit" if pd.notna(val_faskes) and val_faskes != "-" else "-")
        pend_kategori = "Dasar" if val_pendidikan == 1 else ("Lanjut" if pd.notna(val_pendidikan) and val_pendidikan != "-" else "-")
        
        sosio_str = f"<div style='font-size:0.75rem; color:#64748b; line-height: 1.4;'>Eko: <b style='color:#334155;'>{pendapatan_kategori}</b> | Air: <b style='color:#334155;'>{air_kategori}</b><br>Faskes: <b style='color:#334155;'>{faskes_kategori}</b> | Pddk: <b style='color:#334155;'>{pend_kategori}</b><br>Pengetahuan Gizi: <b style='color:#047857;'>Skor {val_gizi}</b></div>"

        # --- PENYEMPURNAAN MUTAKHIR: STRUKTUR HISTORI BADGE 3 LABEL ---
        target_val = str(row.get('hasil_risiko', 'NORMAL'))
        target_val_upper = target_val.upper()
        
        pct_str = ""
        if "(" in target_val and "%" in target_val:
            try:
                pct = target_val.split("(")[1].split(")")[0]
                pct_str = f"<div style='margin-top: 3px; font-size: 0.65rem; background: rgba(0,0,0,0.06); padding: 1px 4px; border-radius: 4px; display: inline-block;'>{pct}</div>"
            except:
                pass
                
        # Menentukan visual warna dan teks spesifik berdasarkan 3 level
        if "TINGGI" in target_val_upper:
            badge_bg = "#fee2e2"
            badge_color = "#b91c1c"
            base_text = "Risiko<br>Tinggi"
        elif "RENTAN" in target_val_upper:
            badge_bg = "#fffbeb"
            badge_color = "#d97706"
            base_text = "Status<br>Rentan"
        else:
            badge_bg = "#ecfdf5"
            badge_color = "#047857"
            base_text = "Risiko<br>Rendah"
            
        label_visual = f"{base_text}{pct_str}"
        
        html_table_db += f"<tr style='background-color: #ffffff; border-bottom: 1px solid #f1f5f9;'>"
        html_table_db += f"<td style='padding: 12px 10px; color: #0f172a; font-size: 0.85rem; font-weight: 800; vertical-align: top;'>#{id_p}<br><span style='font-size:0.75rem; color:#64748b; font-weight:500;'>Antrean:<br>{antrean}</span></td>"
        html_table_db += f"<td style='padding: 12px 10px; vertical-align: top;'><b style='color: #0f172a; font-size: 0.85rem;'>{nama}</b> <span style='font-size:0.75rem; color:#64748b;'>(Usia: {usia} Thn)</span><br><div style='font-size:0.75rem; color:#64748b; margin-top:4px;'>✉️ {email_str}<br>📞 {hp_str}</div></td>"
        html_table_db += f"<td style='padding: 12px 10px; color: #475569; font-size: 0.85rem; vertical-align: top;'>{alamat_display}</td>"
        html_table_db += f"<td style='padding: 12px 10px; color: #475569; font-size: 0.85rem; vertical-align: top;'>{faskes_str}</td>"
        html_table_db += f"<td style='padding: 12px 10px; color: #475569; font-size: 0.85rem; vertical-align: top;'>{tgl_str}</td>"
        html_table_db += f"<td style='padding: 12px 10px; vertical-align: top;'>{klinis_str}</td>"
        html_table_db += f"<td style='padding: 12px 10px; vertical-align: top;'>{sosio_str}</td>"
        html_table_db += f"<td style='padding: 12px 10px; text-align:center; vertical-align: top;'><div style='background: {badge_bg}; color: {badge_color}; padding: 6px 12px; border-radius: 8px; font-size: 0.75rem; font-weight: 800; line-height:1.2; display:inline-block;'>{label_visual}</div></td>"
        html_table_db += "</tr>"

    html_table_db += "</tbody></table></div></div>"
    st.markdown(html_table_db, unsafe_allow_html=True)