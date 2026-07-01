import streamlit as st

def inject_modern_css():
    """
    Menyuntikkan CSS kustom untuk memperindah tampilan aplikasi dengan tema modern (putih/hijau zamrud).
    Disesuaikan untuk mendukung tampilan form input dan card UI yang premium.
    """
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

            /* --- GAYA VISUAL GLOBAL & BACKGROUND MINT GRADASI --- */
            html, body, [class*="css"], .stApp {
                font-family: 'Inter', sans-serif !important;
            }

            [data-testid="stAppViewContainer"] {
                background: radial-gradient(circle at 85% 85%, #d1fae5 0%, #f8fafc 100%) !important;
            }

            .block-container {
                max-width: 1300px !important;
                padding-top: 2rem !important;
            }

            /* HAPUS: Aturan global p, span, div { color: #334155; } yang menyebabkan warna teks nabrak di tombol. 
               Sebagai gantinya kita gunakan warna default Streamlit yang sudah cerdas mengatur kontras. */

            /* ==========================================
               1. 🚨 REKAYASA TOTAL SIDEBAR PREMIUM
               ========================================== */
            [data-testid="stSidebar"] {
                background-color: #034833 !important; 
                color: #ffffff !important;
                padding-top: 1rem;
            }

            [data-testid="stSidebarCollapseButton"], 
            button[aria-label="Close sidebar"],
            button[title="Collapse sidebar"] {
                background-color: rgba(255, 255, 255, 0.2) !important;
                border: 1px solid rgba(255, 255, 255, 0.35) !important;
                border-radius: 10px !important;
                color: #ffffff !important;
                padding: 6px !important;
                transition: all 0.2s ease-in-out !important;
                margin-right: 0.75rem !important;
            }
            [data-testid="stSidebarCollapseButton"] svg, 
            button[aria-label="Close sidebar"] svg,
            button[title="Collapse sidebar"] svg {
                fill: #ffffff !important;
                color: #ffffff !important;
                width: 1.5rem !important;
                height: 1.5rem !important;
            }
            [data-testid="stSidebarCollapseButton"]:hover, 
            button[aria-label="Close sidebar"]:hover,
            button[title="Collapse sidebar"]:hover {
                background-color: rgba(255, 255, 255, 0.35) !important;
                transform: scale(1.08);
            }

            div[data-testid="collapsedControl"] button,
            button[aria-label="Expand sidebar"],
            button[title="Expand sidebar"] {
                background-color: #034833 !important;
                border: 2px solid #10b981 !important; 
                border-radius: 50% !important;
                width: 46px !important;
                height: 46px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                box-shadow: 0 4px 14px rgba(3, 72, 51, 0.4) !important; 
                transition: all 0.2s ease-in-out !important;
                margin-top: 0.5rem !important;
                margin-left: 0.5rem !important;
            }
            div[data-testid="collapsedControl"] button svg,
            button[aria-label="Expand sidebar"] svg {
                fill: #ffffff !important;
                color: #ffffff !important;
                width: 1.4rem !important;
                height: 1.4rem !important;
            }
            div[data-testid="collapsedControl"] button:hover,
            button[aria-label="Expand sidebar"]:hover {
                background-color: #006c49 !important;
                transform: scale(1.1);
                box-shadow: 0 6px 20px rgba(0, 108, 73, 0.5) !important;
            }

            [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
                color: #ffffff !important;
            }

            /* TOMBOL NAVIGASI BAWAAN (TIDAK AKTIF / SECONDARY) */
            [data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
                background-color: transparent !important;
                border: 1px solid transparent !important;
                border-radius: 12px !important;
                padding: 0.75rem 1rem !important;
                height: 48px !important;
                margin-bottom: 0.5rem !important;
                display: flex !important;
                justify-content: flex-start !important;
                transition: all 0.2s ease-in-out;
            }
            
            [data-testid="stSidebar"] div.stButton > button[kind="secondary"] *,
            [data-testid="stSidebar"] div.stButton > button[kind="secondary"] p,
            [data-testid="stSidebar"] div.stButton > button[kind="secondary"] span {
                color: #a7f3d0 !important; 
                font-weight: 700 !important;
                font-size: 0.95rem !important;
            }

            [data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
                background-color: rgba(255,255,255,0.05) !important;
                border-color: rgba(255,255,255,0.1) !important;
                transform: translateX(2px);
            }

            /* TOMBOL NAVIGASI AKTIF (PRIMARY) */
            [data-testid="stSidebar"] div.stButton > button[kind="primary"] {
                background-color: #006c49 !important;
                border: 1px solid #10b981 !important;
                border-radius: 12px !important;
                height: 48px !important;
                margin-bottom: 0.5rem !important;
                display: flex !important;
                justify-content: flex-start !important;
                box-shadow: 0 4px 12px rgba(0, 108, 73, 0.3) !important;
            }
            
            [data-testid="stSidebar"] div.stButton > button[kind="primary"],
            [data-testid="stSidebar"] div.stButton > button[kind="primary"] *,
            [data-testid="stSidebar"] div.stButton > button[kind="primary"] p,
            [data-testid="stSidebar"] div.stButton > button[kind="primary"] div,
            [data-testid="stSidebar"] div.stButton > button[kind="primary"] span {
                color: #ffffff !important; 
                font-weight: 700 !important;
                font-size: 0.95rem !important;
            }

            /* TOMBOL DARURAT & BANTUAN (KUNING) */
            [data-testid="stSidebar"] div.element-container:nth-last-child(3) div.stButton > button,
            [data-testid="stSidebar"] div.element-container:nth-last-child(2) div.stButton > button {
                background-color: #f59e0b !important; 
                border: none !important;
                height: 42px !important;
                border-radius: 10px !important;
                box-shadow: 0 4px 12px rgba(245, 158, 11, 0.2) !important;
                display: flex !important;
                justify-content: center !important;
            }
            
            [data-testid="stSidebar"] div.element-container:nth-last-child(3) div.stButton > button *,
            [data-testid="stSidebar"] div.element-container:nth-last-child(2) div.stButton > button * {
                color: #034833 !important; 
                font-weight: 800 !important;
            }
            
            [data-testid="stSidebar"] div.element-container:nth-last-child(3) div.stButton > button:hover,
            [data-testid="stSidebar"] div.element-container:nth-last-child(2) div.stButton > button:hover {
                background-color: #d97706 !important;
                transform: translateY(-1px) !important;
            }

            /* TOMBOL KELUAR / LOGOUT (MERAH) */
            [data-testid="stSidebar"] div.element-container:nth-last-child(1) div.stButton > button {
                background-color: #dc2626 !important;
                border: none !important;
                height: 42px !important;
                border-radius: 10px !important;
                display: flex !important;
                justify-content: center !important;
            }
            
            [data-testid="stSidebar"] div.element-container:nth-last-child(1) div.stButton > button * {
                color: #ffffff !important; 
                font-weight: 800 !important;
            }

            [data-testid="stSidebar"] div.element-container:nth-last-child(1) div.stButton > button:hover {
                background-color: #b91c1c !important;
                transform: translateY(-1px) !important;
            }

            /* ==========================================
               2. 🎛️ TOMBOL PILIHAN PERAN LOGIN (PILLS) & BUTTON PRIMARY GLOBAL
               ========================================== */
            
            /* Styling General Primary Button (Termasuk tombol submit form & tombol simpan) */
            button[data-testid="baseButton-primary"] {
                background-color: #006c49 !important; 
                border: none !important;
                border-radius: 8px !important;
                padding: 0.75rem 1.5rem !important;
                transition: all 0.3s ease !important;
                box-shadow: 0 4px 6px -1px rgba(0, 108, 73, 0.3) !important;
            }
            
            /* FORCE TEXT PUTIH UNTUK TOMBOL PRIMARY */
            button[data-testid="baseButton-primary"],
            button[data-testid="baseButton-primary"] *,
            button[data-testid="baseButton-primary"] p,
            button[data-testid="baseButton-primary"] div,
            button[data-testid="baseButton-primary"] span {
                color: #ffffff !important;
                font-weight: 700 !important;
                font-size: 1rem !important;
            }
            
            button[data-testid="baseButton-primary"]:hover {
                background-color: #005236 !important; 
                box-shadow: 0 6px 12px -2px rgba(0, 108, 73, 0.4) !important;
                transform: translateY(-2px) !important;
            }
               
            div.element-container:has(button[key^="btn_pill_"]) button[kind="secondary"] {
                background-color: #ffffff !important;
                border: 1px solid #cbd5e1 !important;
                border-radius: 12px !important;
                padding: 0.6rem !important;
                transition: all 0.2s ease-in-out;
            }
            div.element-container:has(button[key^="btn_pill_"]) button[kind="secondary"] * {
                color: #475569 !important;
                font-weight: 600 !important;
                font-size: 0.95rem !important;
            }
            div.element-container:has(button[key^="btn_pill_"]) button[kind="secondary"]:hover {
                background-color: #f8fafc !important;
                border-color: #94a3b8 !important;
            }

            /* FORCE TEXT PUTIH UNTUK TOMBOL PILL AKTIF */
            div.element-container:has(button[key^="btn_pill_"]) button[kind="primary"] {
                background-color: #006c49 !important;
                border: 1px solid #005236 !important;
                border-radius: 12px !important;
                padding: 0.6rem !important;
                box-shadow: 0 4px 12px rgba(0, 108, 73, 0.25) !important;
            }
            div.element-container:has(button[key^="btn_pill_"]) button[kind="primary"],
            div.element-container:has(button[key^="btn_pill_"]) button[kind="primary"] *,
            div.element-container:has(button[key^="btn_pill_"]) button[kind="primary"] p,
            div.element-container:has(button[key^="btn_pill_"]) button[kind="primary"] div,
            div.element-container:has(button[key^="btn_pill_"]) button[kind="primary"] span {
                color: #ffffff !important;
                font-weight: 700 !important;
                font-size: 0.95rem !important;
            }

            /* ==========================================
               3. 📝 FORM KARTU LOGIN PUTIH & TEXT INPUT
               ========================================== */
            div[data-testid="stForm"] {
                background-color: #ffffff !important;
                padding: 2.5rem 2.25rem !important;
                border-radius: 28px !important;
                box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.06), 0 4px 12px -2px rgba(0, 0, 0, 0.03) !important;
                border: 1px solid rgba(226, 232, 240, 0.8) !important;
                margin-top: 1.5rem !important;
                margin-bottom: 1.5rem !important;
            }

            .stTextInput label, .stNumberInput label, .stSelectbox label, .stRadio label, .stDateInput label, .stTimeInput label {
                color: #1e293b !important; 
                font-weight: 600 !important;
            }

            div[data-testid="stTextInput"] input, 
            div[data-testid="stNumberInput"] input,
            [data-testid="stSelectbox"]>div>div>div,
            div[data-testid="stDateInput"] input,
            div[data-testid="stTimeInput"] input {
                background-color: #f8fafc !important; 
                border-radius: 10px !important;
                border: 1px solid #cbd5e1 !important;
                padding: 0.65rem 1rem !important;
                font-size: 0.95rem !important;
                color: #1e293b !important;
                transition: all 0.2s ease-in-out;
            }
            
            div[data-testid="stTextInput"] input:focus, 
            div[data-testid="stNumberInput"] input:focus,
            [data-testid="stSelectbox"]>div>div>div:focus,
            div[data-testid="stDateInput"] input:focus,
            div[data-testid="stTimeInput"] input:focus {
                border-color: #10b981 !important;
                box-shadow: 0 0 0 1px #10b981 !important;
            }

            div[data-testid="stTabs"] [data-baseweb="tab-list"] { display: none !important; }

            /* Tombol Submit di dalam st.form() (Login/Daftar) */
            div[data-testid="stForm"] button[type="submit"] {
                background-color: #006c49 !important;
                border-radius: 10px !important;
                padding: 0.75rem 1.5rem !important;
                border: none !important;
                box-shadow: 0 4px 12px rgba(0, 108, 73, 0.15) !important;
                transition: all 0.2s ease;
            }
            div[data-testid="stForm"] button[type="submit"],
            div[data-testid="stForm"] button[type="submit"] *,
            div[data-testid="stForm"] button[type="submit"] p,
            div[data-testid="stForm"] button[type="submit"] div,
            div[data-testid="stForm"] button[type="submit"] span {
                color: #ffffff !important;
                font-weight: 700 !important;
                font-size: 1rem !important;
            }
            div[data-testid="stForm"] button[type="submit"]:hover {
                background-color: #005236 !important;
                transform: translateY(-1px) !important;
            }

            /* ==========================================
               4. 🟢 REKAYASA RADIO BUTTON JADI TOMBOL KOTAK
               ========================================== */
            div.stRadio > div[role="radiogroup"] { gap: 0.75rem; }
            
            div.stRadio label[data-baseweb="radio"] {
                background-color: #f8fafc !important;
                border: 1px solid #cbd5e1 !important;
                border-radius: 10px !important;
                padding: 0.8rem 1.2rem !important;
                margin: 0 !important;
                cursor: pointer !important;
                transition: all 0.2s ease-in-out !important;
                box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
                flex: 1; display: flex; justify-content: center; align-items: center;
            }
            
            div.stRadio label[data-baseweb="radio"] > div:first-child { display: none !important; }
            
            /* Warna teks RADIO saat TIDAK dipilih */
            div.stRadio label[data-baseweb="radio"] div {
                color: #475569 !important; font-weight: 600 !important; font-size: 0.95rem !important;
            }
            
            div.stRadio label[data-baseweb="radio"]:hover {
                border-color: #10b981 !important; background-color: #f0fdf4 !important;
            }
            
            /* WARNA SAAT DIPILIH (AKTIF/CHECKED) -> Menjadi Hijau DigiMind & TEKS PUTIH */
            div.stRadio label[data-baseweb="radio"]:has(input:checked) {
                background-color: #006c49 !important; border-color: #005236 !important;
                box-shadow: 0 4px 12px rgba(0, 108, 73, 0.25) !important;
            }
            
            div.stRadio label[data-baseweb="radio"]:has(input:checked),
            div.stRadio label[data-baseweb="radio"]:has(input:checked) *,
            div.stRadio label[data-baseweb="radio"]:has(input:checked) p,
            div.stRadio label[data-baseweb="radio"]:has(input:checked) div,
            div.stRadio label[data-baseweb="radio"]:has(input:checked) span {
                color: #ffffff !important; 
                font-weight: 700 !important;
            }
            
            /* ==========================================
               5. 🔳 STYLING CONTAINER FORM UTAMA (Fix White Card Bocor)
               ========================================== */
               
            /* HANYA berikan efek Card Putih Premium pada container yang memiliki class .main-form-wrapper */
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.main-form-wrapper) {
                background-color: #ffffff !important; 
                border-radius: 16px !important;
                padding: 2.5rem !important;
                border: 1px solid #e2e8f0 !important;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01) !important;
                margin-bottom: 2rem !important;
            }

            /* MENGHILANGKAN EFEK CARD PADA ELEMEN LAIN YANG TIDAK PERLU */
            div[data-testid="stVerticalBlockBorderWrapper"]:not(:has(.main-form-wrapper)) {
                background-color: transparent !important;
                border: none !important;
                box-shadow: none !important;
                padding: 0 !important;
            }

            .modern-card {
                background-color: #ffffff; border-radius: 16px; padding: 2rem;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
                margin-bottom: 2rem; border: 1px solid #e2e8f0;
            }
            
            .premium-input-card {
                background-color: #ffffff; border-radius: 16px; padding: 2.5rem;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02);
                border: 1px solid #f1f5f9; margin-bottom: 2rem;
            }
            
            .custom-warning {
                background-color: #fffbeb; border-left: 4px solid #f59e0b; padding: 1rem;
                border-radius: 0 8px 8px 0; color: #92400e; margin-bottom: 1rem;
            }

            /* --- TABLE STYLING --- */
            [data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0; }
            [data-testid="stDataFrame"] table { color: #334155; }
            [data-testid="stDataFrame"] th { background-color: #f8fafc !important; color: #0f172a !important; font-weight: 700 !important; border-bottom: 2px solid #e2e8f0 !important; }

            /* ==========================================
               6. 🌐 LANDING PAGE / EDUCATION DASHBOARD
               ========================================== */
            .hero-section {
                display: flex; align-items: center; justify-content: space-between; gap: 3rem;
                padding: 4rem; background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
                border-radius: 30px; border: 1px solid #e2e8f0; margin-bottom: 4rem;
            }
            .hero-text { flex: 1.2; display: flex; flex-direction: column; align-items: flex-start; }
            .hero-image-wrapper { flex: 1; display: flex; justify-content: flex-end; }
            .hero-image { width: 100%; max-width: 580px; border-radius: 24px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); object-fit: cover; }
            .hero-badge { background: #dcfce7; color: #15803d; padding: 8px 16px; border-radius: 999px; font-size: 0.9rem; font-weight: 600; margin-bottom: 1.5rem; }
            .hero-title { font-size: 3.2rem; font-weight: 800; line-height: 1.2; color: #1e293b; margin-bottom: 1.5rem; }
            .hero-title span { color: #10b981; }
            .hero-subtitle { font-size: 1.1rem; color: #64748b; line-height: 1.6; margin-bottom: 2.5rem; max-width: 90%; }
            .btn-mulai { background: #064e3b; color: white !important; text-decoration: none !important; padding: 14px 28px; border-radius: 12px; font-weight: 600; font-size: 1.05rem; transition: 0.3s; box-shadow: 0 4px 14px rgba(6, 78, 59, 0.2); }
            .btn-mulai:hover { background: #047857; transform: translateY(-2px); box-shadow: 0 8px 20px rgba(4, 120, 87, 0.3); }
            .section-title { text-align: center; font-size: 2.2rem; font-weight: 700; color: #0f172a; margin-bottom: 0.5rem; }
            .section-subtitle { text-align: center; color: #64748b; margin-bottom: 3rem; }
            .feature-card { background: white; border: 1px solid #e2e8f0; border-radius: 20px; padding: 2rem; height: 100%; transition: transform 0.2s, box-shadow 0.2s; }
            .feature-card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,0,0,0.05); border-color: #10b981; }
            .feature-title { font-size: 1.2rem; font-weight: 700; margin-bottom: 0.8rem; color: #0f172a; }
            .feature-desc { color: #64748b; line-height: 1.6; font-size: 0.95rem; }
            .banner { background: linear-gradient(135deg, #064e3b, #065f46); color: white; border-radius: 24px; padding: 3.5rem; margin-top: 2rem; margin-bottom: 3rem; text-align: center; box-shadow: 0 15px 30px rgba(6, 78, 59, 0.2); }
            .banner h2 { color: white; margin-bottom: 1rem; font-weight: 700; }
            .banner p { color: #a7f3d0; font-size: 1.1rem; margin: 0; }

            @media (max-width: 900px) {
                .hero-section { flex-direction: column; text-align: center; padding: 3rem 2rem; }
                .hero-text { align-items: center; }
                .hero-subtitle { max-width: 100%; }
                .hero-title { font-size: 2.5rem; }
                .hero-image-wrapper { margin-top: 2rem; }
            }
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
    """, unsafe_allow_html=True)

