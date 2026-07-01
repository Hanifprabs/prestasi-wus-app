import streamlit as st
from modules.ui_components import inject_modern_css  # <-- SOLUSI: Mengimpor fungsi CSS

def show_education_dashboard():
    """
    Menampilkan antarmuka Dashboard Edukasi Stunting & Gizi WUS Premium.
    Dilengkapi dengan foto ilustrasi dan parameter medis.
    """
    # Memastikan gaya CSS modern (tombol hijau, rounded corner) teraplikasi di halaman ini
    inject_modern_css() 
    
    # ==========================================
    # 1. HERO BANNER (SPLIT LAYOUT DENGAN FOTO)
    # ==========================================
    col_hero1, col_hero2 = st.columns([1.5, 1], gap="large")
    
    with col_hero1:
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <h1 style="margin: 0; font-size: 2.8rem; font-weight: 800; color: #006c49; letter-spacing: -0.02em; line-height: 1.1;">
            Kesehatan Anda Hari Ini,<br>Masa Depan Mereka Nanti. 🌱
        </h1>
        <p style="margin: 1.2rem 0 1.5rem 0; font-size: 1.1rem; color: #475569; line-height: 1.6;">
            Langkah pertama mencegah stunting tidak dimulai saat bayi lahir, melainkan sejak Anda mempersiapkan diri menjadi ibu. Mari pahami standar kesehatan dan gizi seimbang untuk mencetak generasi cerdas.
        </p>
        """, unsafe_allow_html=True)
        
        # Tombol Call to Action yang memicu action login (jika belum login)
        if st.button("Mulai Skrining AI Sekarang ➔", type="primary"):
            if not st.session_state.get('logged_in', False):
                st.session_state['tampilkan_login'] = True
                st.rerun()

    with col_hero2:
        # Foto ilustrasi wanita sehat (Placeholder HD dari Unsplash)
        st.markdown("""
        <img src="https://images.unsplash.com/photo-1590650153855-d9e808231d41?auto=format&fit=crop&q=80&w=800" 
             style="width: 100%; height: 320px; object-fit: cover; border-radius: 20px; box-shadow: 0 10px 25px rgba(0, 108, 73, 0.2);">
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

    # ==========================================
    # 2. METRIK KESEHATAN IDEAL WUS
    # ==========================================
    st.markdown("<h2 style='color:#0f172a; font-weight: 800; font-size: 1.4rem; margin-bottom: 1rem; text-align: center;'>🎯 Target Parameter Medis Ideal (WUS)</h2>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    
    # Fungsi pembantu untuk membuat card metrik
    def metric_card(icon, title, value, desc, bg_color, border_color):
        return f"""
        <div style="background-color: {bg_color}; border-top: 4px solid {border_color}; border-radius: 12px; padding: 1.5rem 1rem; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02); height: 100%;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
            <p style="margin: 0; color: #64748b; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">{title}</p>
            <h3 style="margin: 0.2rem 0; color: #0f172a; font-size: 1.6rem; font-weight: 800;">{value}</h3>
            <p style="margin: 0; color: #475569; font-size: 0.75rem;">{desc}</p>
        </div>
        """
        
    with c1: st.markdown(metric_card("⚖️", "IMT Normal", "18.5 - 24.9", "Indeks Massa Tubuh", "#f8fafc", "#0ea5e9"), unsafe_allow_html=True)
    with c2: st.markdown(metric_card("📏", "Minimal LILA", "≥ 23.5 cm", "Bebas Kurang Energi Kronis", "#f8fafc", "#10b981"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card("🩸", "Hemoglobin (Hb)", "≥ 12.0", "g/dL (Bebas Anemia)", "#f8fafc", "#ef4444"), unsafe_allow_html=True)
    with c4: st.markdown(metric_card("🩺", "Tekanan Darah", "120/80", "mmHg (Tensi Normal)", "#f8fafc", "#8b5cf6"), unsafe_allow_html=True)

    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

    # ==========================================
    # 3. APA ITU STUNTING (SPLIT LAYOUT)
    # ==========================================
    col_stunt1, col_stunt2 = st.columns([1, 1.2], gap="large")
    
    with col_stunt1:
        st.markdown("""
        <img src="https://images.unsplash.com/photo-1519689680058-324335c77eba?auto=format&fit=crop&q=80&w=800" 
             style="width: 100%; height: 350px; object-fit: cover; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        """, unsafe_allow_html=True)
        
    with col_stunt2:
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:#0f172a; font-weight: 800; font-size: 1.6rem; margin-bottom: 0.5rem;'>Apa Itu Stunting?</h2>", unsafe_allow_html=True)
        st.markdown("""
        <p style="color: #475569; font-size: 1rem; line-height: 1.6; margin-bottom: 1.5rem;">
            Stunting bukan sekadar soal anak yang terlahir pendek. Stunting adalah <b>kegagalan perkembangan otak dan fisik</b> akibat kekurangan gizi kronis pada 1.000 Hari Pertama Kehidupan (sejak dalam kandungan hingga usia 2 tahun).
        </p>
        <div style="background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 1rem 1.5rem; border-radius: 0 8px 8px 0;">
            <p style="margin: 0 0 0.5rem 0; font-weight: 700; color: #b91c1c;">⚠️ Dampak Jangka Panjang:</p>
            <ul style="margin: 0; color: #7f1d1d; font-size: 0.9rem; padding-left: 1.2rem;">
                <li>Penurunan tingkat kecerdasan (IQ) dan lambat belajar.</li>
                <li>Sistem imun lemah (mudah sakit infeksi).</li>
                <li>Risiko tinggi terkena diabetes, stroke, dan penyakit jantung di usia dewasa.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

    # ==========================================
    # 4. PANDUAN GIZI (PHOTO CARDS GRID)
    # ==========================================
    st.markdown("<h2 style='color:#0f172a; font-weight: 800; font-size: 1.6rem; margin-bottom: 0.2rem; text-align: center;'>Panduan Gizi & Pencegahan Kemenkes</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b; font-size: 1rem; margin-bottom: 2rem; text-align: center;'>Terapkan 3 langkah ini dalam keseharian Anda.</p>", unsafe_allow_html=True)
    
    col_card1, col_card2, col_card3 = st.columns(3, gap="medium")
    
    def photo_card(img_url, title, desc):
        return f"""
        <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); height: 100%; transition: transform 0.3s ease;">
            <img src="{img_url}" style="width: 100%; height: 160px; object-fit: cover;">
            <div style="padding: 1.5rem;">
                <h3 style="margin: 0 0 0.5rem 0; color: #0f172a; font-size: 1.1rem; font-weight: 800;">{title}</h3>
                <p style="margin: 0; color: #475569; font-size: 0.9rem; line-height: 1.5;">{desc}</p>
            </div>
        </div>
        """

    with col_card1:
        st.markdown(photo_card(
            "https://images.unsplash.com/photo-1490645935967-10de6ba17061?auto=format&fit=crop&q=80&w=600",
            "Porsi 'Isi Piringku'",
            "Proporsi ideal: 1/3 karbohidrat, 1/3 sayuran hijau, 1/6 lauk pauk (protein), dan 1/6 buah-buahan segar."
        ), unsafe_allow_html=True)
        
    with col_card2:
        st.markdown(photo_card(
            "https://images.unsplash.com/photo-1599058917212-97d14cbce2bc?auto=format&fit=crop&q=80&w=600",
            "Prioritas Protein Hewani",
            "Asam amino dari protein hewani (Telur, Ikan, Ayam) jauh lebih mudah diserap oleh tubuh untuk regenerasi sel dan perkembangan janin kelak."
        ), unsafe_allow_html=True)

    with col_card3:
        st.markdown(photo_card(
            "https://images.unsplash.com/photo-1584308666744-24d5e4b78ae6?auto=format&fit=crop&q=80&w=600",
            "Tablet Tambah Darah",
            "Minum 1 TTD seminggu sekali. Upaya paling efektif untuk mencegah Anemia yang merupakan penyebab utama melahirkan bayi Berat Badan Lahir Rendah (BBLR)."
        ), unsafe_allow_html=True)

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    import streamlit as st
from modules.ui_components import inject_modern_css

def show_education_dashboard():
    """
    Menampilkan halaman Dashboard utama/edukasi yang dapat diakses oleh semua pengguna.
    Berisi informasi umum tentang stunting dan tujuan aplikasi.
    """
    inject_modern_css()

    st.markdown("""
    <div class="hero-section">
        <div class="hero-text">
            <div class="hero-badge">🛡️ Platform Kesehatan Terpercaya</div>
            <div class="hero-title">Cegah Stunting Sejak Dini untuk <br><span>Generasi Masa Depan</span></div>
            <div class="hero-subtitle">Sistem Prediksi Risiko Stunting berbasis Artificial Intelligence yang dirancang khusus untuk membantu Wanita Usia Subur (WUS) memantau kesehatan secara mandiri dan profesional.</div>
            <a href="?action=login" target="_self" class="btn-mulai">Mulai Deteksi Sekarang ➔</a>
        </div>
        <div class="hero-image-wrapper">
            <img class="hero-image" src="https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&w=1200&q=80" alt="DigiMind AI Project">
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <h2 class="section-title">Apa itu Stunting?</h2>
    <p class="section-subtitle">Memahami akar masalah untuk pencegahan yang lebih proaktif dan efektif.</p>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='feature-card'><div class='feature-title'>📉 Definisi Medis</div><div class='feature-desc'>Stunting adalah gangguan pertumbuhan fisik dan perkembangan otak anak akibat malnutrisi kronis dan infeksi berulang yang terjadi pada 1.000 Hari Pertama Kehidupan (HPK).</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='feature-card'><div class='feature-title'>⚠️ Dampak Jangka Panjang</div><div class='feature-desc'>Selain postur tubuh yang lebih pendek dari standar usia, stunting menurunkan kecerdasan kognitif, melemahkan imunitas, dan meningkatkan risiko penyakit metabolik di masa dewasa.</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='feature-card'><div class='feature-title'>👩‍⚕️ Peran Penting WUS</div><div class='feature-desc'>Pencegahan paling krusial dimulai sebelum kehamilan. Memastikan Wanita Usia Subur memiliki status gizi baik (terbebas dari anemia & KEK) adalah kunci memutus rantai stunting.</div></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="banner">
        <h2 style="font-size: 2.2rem;">Membangun Masa Depan Sehat</h2>
        <p>Kami berdedikasi untuk menurunkan angka stunting di Indonesia melalui inovasi teknologi yang inklusif.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="modern-card">
        <h3 style="text-align:center;color:#064e3b;margin-bottom:0.5rem;">🎯 Parameter Ideal Wanita Usia Subur</h3>
        <p style="text-align:center;color:#64748b;margin-bottom:0;">Indikator kesehatan penting yang perlu diperhatikan sebelum kehamilan.</p>
    </div>
    """, unsafe_allow_html=True)

    col_metric1, col_metric2, col_metric3 = st.columns(3)
    with col_metric1: st.metric("Lingkar Lengan Atas (LILA)", "≥ 23.5 cm", "Aman dari KEK")
    with col_metric2: st.metric("Kadar Hemoglobin (Hb)", "≥ 12 g/dL", "Bebas Anemia")
    with col_metric3: st.metric("Indeks Massa Tubuh (IMT)", "18.5 - 25", "Status Gizi Baik")