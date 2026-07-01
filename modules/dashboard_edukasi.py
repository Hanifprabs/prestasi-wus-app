import streamlit as st
from modules.ui_components import inject_modern_css

def show_education_dashboard():
    """
    Menampilkan halaman Dashboard utama/edukasi yang dapat diakses oleh semua pengguna.
    Berisi informasi komprehensif tentang stunting dan panduan gizi Wanita Usia Subur (WUS).
    """
    # Menyuntikkan CSS global agar style komponen HTML seragam
    inject_modern_css()

    # ==========================================
    # 1. HERO SECTION (BANNER UTAMA)
    # ==========================================
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; gap: 2rem; background: linear-gradient(135deg, #006c49 0%, #10b981 100%); padding: 2.5rem 2rem; border-radius: 20px; color: white; margin-bottom: 3rem; box-shadow: 0 10px 25px -5px rgba(0, 108, 73, 0.3);">
        <div style="flex: 1.3; max-width: 60%;">
            <div style="background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 20px; display: inline-block; font-size: 0.8rem; font-weight: 700; margin-bottom: 1rem; letter-spacing: 0.5px;">🛡️ PLATFORM KESEHATAN PREDIKTIF AI</div>
            <h1 style="margin: 0; font-size: 2.5rem; font-weight: 800; letter-spacing: -0.025em; line-height: 1.2; color: white;">Cegah Stunting Sejak Dini untuk <br><span style="color: #a7f3d0;">Generasi Masa Depan</span></h1>
            <p style="margin: 1rem 0 2rem 0; font-size: 1.05rem; opacity: 0.95; line-height: 1.6;">Sistem analisis risiko stunting berbasis <i>Artificial Intelligence</i> yang dirancang khusus untuk membantu Wanita Usia Subur (WUS) memantau parameter kesehatan secara mandiri, proaktif, dan profesional.</p>
        </div>
        <div style="flex: 0.9; display: flex; justify-content: flex-end;">
            <img src="https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&w=600&q=80" alt="DigiMind AI Project" style="width: 100%; max-width: 420px; height: 280px; object-fit: cover; border-radius: 16px; box-shadow: 0 8px 16px rgba(0,0,0,0.1);">
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- TOMBOL LOGIKA PINTAR (SMART ROUTING) ---
    # Jika sudah login -> Ke Layanan Utama. Jika belum -> Ke halaman Login.
    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        if st.button("Mulai Skrining AI Sekarang ➔", type="primary", use_container_width=True):
            if st.session_state.get('logged_in', False):
                st.session_state['menu_internal_active'] = "Layanan Utama"
                st.rerun()
            else:
                st.session_state['tampilkan_login'] = True
                st.rerun()

    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

    # ==========================================
    # 2. METRIK KESEHATAN IDEAL WUS (DITENGAHKAN)
    # ==========================================
    st.markdown("<h2 style='color:#0f172a; font-weight: 800; font-size: 1.5rem; margin-bottom: 1.2rem; text-align: center;'>🎯 Target Parameter Medis Ideal (WUS)</h2>", unsafe_allow_html=True)
    
    spacer_kiri, c1, c2, c3, spacer_kanan = st.columns([0.5, 2, 2, 2, 0.5], gap="large")
    
    def metric_card(icon, title, value, desc, bg_color, border_color):
        return f"""
        <div style="background-color: {bg_color}; border-top: 4px solid {border_color}; border-radius: 12px; padding: 1.5rem 1rem; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); height: 100%;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
            <p style="margin: 0; color: #64748b; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">{title}</p>
            <h3 style="margin: 0.2rem 0; color: #0f172a; font-size: 1.6rem; font-weight: 800;">{value}</h3>
            <p style="margin: 0; color: #475569; font-size: 0.75rem; font-weight: 500;">{desc}</p>
        </div>
        """
        
    with c1: st.markdown(metric_card("⚖️", "IMT Normal", "18.5 - 24.9", "Indeks Massa Tubuh", "#ffffff", "#0ea5e9"), unsafe_allow_html=True)
    with c2: st.markdown(metric_card("📏", "Minimal LILA", "≥ 23.5 cm", "Bebas Kurang Energi Kronis", "#ffffff", "#10b981"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card("🩸", "Hemoglobin (Hb)", "≥ 12.0", "g/dL (Bebas Anemia)", "#ffffff", "#ef4444"), unsafe_allow_html=True)

    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

    # ==========================================
    # 3. APA ITU STUNTING (SPLIT LAYOUT)
    # ==========================================
    st.markdown("<h2 style='color:#0f172a; font-weight: 800; font-size: 1.5rem; margin-bottom: 1.2rem; text-align: center;'>🔍 Memahami Urgensi Stunting</h2>", unsafe_allow_html=True)

    col_stunt1, col_stunt2 = st.columns([1, 1], gap="large")
    
    with col_stunt1:
        st.markdown("""
        <img src="https://images.unsplash.com/photo-1519689680058-324335c77eba?auto=format&fit=crop&q=80&w=800" 
             style="width: 100%; height: 350px; object-fit: cover; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
        """, unsafe_allow_html=True)
        
    with col_stunt2:
        st.markdown("""
        <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 2rem; height: 350px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); display: flex; flex-direction: column; justify-content: center;">
            <h3 style='color:#0f172a; font-weight: 800; font-size: 1.4rem; margin-top: 0; margin-bottom: 0.8rem;'>Apa Itu Stunting?</h3>
            <p style="color: #475569; font-size: 0.95rem; line-height: 1.6; margin-bottom: 1.5rem;">
                Stunting adalah <b>kegagalan perkembangan fisik dan struktur otak</b> anak akibat malnutrisi kronis dan infeksi berulang yang tidak ditangani dengan baik pada masa awal pertumbuhan.
            </p>
            <div style="background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 1rem 1.5rem; border-radius: 0 8px 8px 0;">
                <p style="margin: 0 0 0.5rem 0; font-weight: 700; color: #b91c1c; font-size: 0.9rem;">⚠️ Bahaya Jangka Panjang:</p>
                <ul style="margin: 0; color: #7f1d1d; font-size: 0.85rem; padding-left: 1.2rem; line-height: 1.5;">
                    <li>Penurunan kecerdasan kognitif (sulit berprestasi di sekolah).</li>
                    <li>Sistem imun melemah (anak mudah terserang infeksi).</li>
                    <li>Risiko tinggi menderita obesitas dan penyakit jantung di masa dewasa.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

    # ==========================================
    # 4. EDUKASI BARU: 1.000 HARI PERTAMA KEHIDUPAN
    # ==========================================
    st.markdown("<h2 style='color:#0f172a; font-weight: 800; font-size: 1.5rem; margin-bottom: 0.2rem; text-align: center;'>⏳ Masa Keemasan: 1.000 Hari Pertama Kehidupan (HPK)</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b; font-size: 0.95rem; margin-bottom: 2rem; text-align: center;'>Periode kritis yang tidak bisa diulang untuk mencetak generasi cerdas.</p>", unsafe_allow_html=True)
    
    col_hpk1, col_hpk2, col_hpk3 = st.columns(3, gap="medium")
    
    with col_hpk1:
        st.markdown("""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-top: 4px solid #f59e0b; border-radius: 12px; padding: 1.5rem; height: 100%;">
            <div style="background: #fef3c7; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; color: #b45309; margin-bottom: 1rem;">1</div>
            <h4 style="color: #0f172a; font-size: 1.05rem; font-weight: 800; margin-bottom: 0.5rem;">Masa Kehamilan (270 Hari)</h4>
            <p style="color: #475569; font-size: 0.85rem; line-height: 1.5; margin: 0;">Fase penentuan kualitas janin. Ibu hamil wajib terbebas dari anemia, mengonsumsi Asam Folat, dan rutin memeriksakan kandungan agar plasenta berkembang optimal.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_hpk2:
        st.markdown("""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-top: 4px solid #0ea5e9; border-radius: 12px; padding: 1.5rem; height: 100%;">
            <div style="background: #e0f2fe; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; color: #0369a1; margin-bottom: 1rem;">2</div>
            <h4 style="color: #0f172a; font-size: 1.05rem; font-weight: 800; margin-bottom: 0.5rem;">0 - 6 Bulan Pertama (180 Hari)</h4>
            <p style="color: #475569; font-size: 0.85rem; line-height: 1.5; margin: 0;">Pemberian <b>ASI Eksklusif</b> tanpa tambahan cairan/makanan lain. ASI memberikan antibodi terbaik yang melindungi pencernaan bayi dari bakteri berbahaya.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_hpk3:
        st.markdown("""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-top: 4px solid #10b981; border-radius: 12px; padding: 1.5rem; height: 100%;">
            <div style="background: #d1fae5; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; color: #047857; margin-bottom: 1rem;">3</div>
            <h4 style="color: #0f172a; font-size: 1.05rem; font-weight: 800; margin-bottom: 0.5rem;">Usia 6 - 24 Bulan (550 Hari)</h4>
            <p style="color: #475569; font-size: 0.85rem; line-height: 1.5; margin: 0;">Fase pemberian Makanan Pendamping ASI (MPASI) yang kaya protein hewani untuk memastikan tulang dan otak anak berkembang pesat mengejar target pertumbuhannya.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

    # ==========================================
    # 5. EDUKASI BARU: FAKTOR SOSIODEMOGRAFI LINGKUNGAN
    # ==========================================
    st.markdown("""
    <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 16px; padding: 2rem; display: flex; gap: 2rem; align-items: center; margin-bottom: 3rem;">
        <div style="flex: 1;">
            <h3 style="color:#006c49; font-weight: 800; font-size: 1.4rem; margin-top: 0; margin-bottom: 0.8rem;">Mengapa Faktor Lingkungan Penting?</h3>
            <p style="color: #475569; font-size: 0.95rem; line-height: 1.6; margin-bottom: 1rem;">
                Gizi yang baik akan sia-sia jika sanitasi lingkungan buruk. Anak yang sering diare akibat air tidak bersih akan kehilangan nutrisi berharga, menghambat penyerapan gizi, dan berujung pada stunting.
            </p>
            <ul style="margin: 0; color: #334155; font-size: 0.9rem; padding-left: 1.2rem; line-height: 1.6; font-weight: 500;">
                <li><b>Air Bersih:</b> Mencegah penyakit infeksi pencernaan (diare/cacingan).</li>
                <li><b>Akses Faskes:</b> Memastikan pemantauan kondisi kehamilan tepat waktu.</li>
                <li><b>Pengetahuan Gizi:</b> Mengubah kebiasaan konsumsi karbohidrat berlebih menjadi kaya protein hewani.</li>
            </ul>
        </div>
        <div style="flex: 0.6; text-align: center;">
            <div style="background: white; border-radius: 50%; width: 150px; height: 150px; display: flex; align-items: center; justify-content: center; margin: 0 auto; box-shadow: 0 4px 10px rgba(0, 108, 73, 0.1);">
                <span style="font-size: 4rem;">🚰</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


    # ==========================================
    # 6. PANDUAN GIZI (PHOTO CARDS GRID)
    # ==========================================
    st.markdown("<h2 style='color:#0f172a; font-weight: 800; font-size: 1.5rem; margin-bottom: 0.2rem; text-align: center;'>🥗 Panduan Gizi Kemenkes</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b; font-size: 0.95rem; margin-bottom: 2rem; text-align: center;'>Terapkan 3 langkah proteksi nutrisi ini dalam pola hidup harian Anda.</p>", unsafe_allow_html=True)
    
    col_card1, col_card2, col_card3 = st.columns(3, gap="medium")
    
    def photo_card(img_url, title, desc):
        return f"""
        <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 10px -1px rgba(0,0,0,0.04); height: 100%;">
            <img src="{img_url}" style="width: 100%; height: 180px; object-fit: cover;">
            <div style="padding: 1.5rem;">
                <h3 style="margin: 0 0 0.5rem 0; color: #0f172a; font-size: 1.1rem; font-weight: 800;">{title}</h3>
                <p style="margin: 0; color: #475569; font-size: 0.85rem; line-height: 1.5;">{desc}</p>
            </div>
        </div>
        """

    with col_card1:
        st.markdown(photo_card(
            "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&q=80&w=600",
            "Porsi 'Isi Piringku'",
            "Membagi piring makan menjadi: 1/3 makanan pokok, 1/3 sayuran hijau, 1/6 lauk-pauk protein, dan 1/6 buah-buahan."
        ), unsafe_allow_html=True)
        
    with col_card2:
        st.markdown(photo_card(
            "https://images.unsplash.com/photo-1606787366850-de6330128bfc?auto=format&fit=crop&q=80&w=600",
            "Prioritas Protein Hewani",
            "Asam amino dari protein hewani (telur, ikan, daging) terbukti klinis lebih mudah diserap untuk mencegah kegagalan pertumbuhan."
        ), unsafe_allow_html=True)

    with col_card3:
        st.markdown(photo_card(
            "https://images.unsplash.com/photo-1584017911766-d451b3d0e843?auto=format&fit=crop&q=80&w=600",
            "Tablet Tambah Darah",
            "Mengkonsumsi rutin 1 TTD seminggu sekali. Upaya penanggulangan zat besi paling efektif untuk memutus rantai anemia bawaan."
        ), unsafe_allow_html=True)

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)