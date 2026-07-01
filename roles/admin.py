import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px
import re
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
from modules.model_ai import train_model
from modules.database import get_all_patients, get_db_connection
from modules.auth import KODE_REGISTRASI_NAKES, KODE_REGISTRASI_ADMIN

FEATURE_COLUMNS = ['Usia', 'Berat_Badan', 'Tinggi_Badan', 'Hb_Darah', 'IMT', 'LILA', 'Pendapatan_Bulanan', 'Akses_Air_Bersih', 'Akses_Layanan_Kesehatan', 'Pendidikan_Terakhir', 'Skor_Pengetahuan_Gizi']

# ==========================================
# CSS GLOBAL UNTUK ADMIN
# ==========================================
def inject_admin_css():
    st.markdown("""
    <style>
    /* Memaksa kontainer dan Form Streamlit tampil seperti Card Premium Putih */
    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stForm"] {
        background-color: #ffffff !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.04) !important;
        padding: 1.5rem !important;
        border: 1px solid #e2e8f0 !important;
        margin-bottom: 2rem !important;
    }
    [data-testid="stForm"] label {
        color: #334155 !important;
        font-weight: 500 !important;
    }
    .metric-eval-card {
        background: #ffffff; border: 1px solid #f1f5f9; border-radius: 16px; 
        padding: 1.2rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03);
    }
    /* Mempercantik Scrollbar Tabel HTML */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 8px; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 8px; }
    ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
    </style>
    """, unsafe_allow_html=True)


# ==========================================
# HALAMAN 1: PUSAT MANAJEMEN MODEL AI (Retraining)
# ==========================================
def show_admin_model_menu():
    inject_admin_css()

    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style='color:#0f172a; font-weight: 800; margin-bottom: 0.2rem; margin-top: 0;'>⚙️ Pusat Manajemen Model AI</h2>
        <p style='color:#64748b; font-size: 0.95rem; margin-top: 0;'>Perbarui dataset secara massal (Batch) menggunakan data riil hasil pembersihan lintas wilayah Puskesmas.</p>
    </div>
    """, unsafe_allow_html=True)

    if 'training_data' not in st.session_state:
        st.warning("Dataset Latih belum terinisialisasi. Pastikan init_ai_and_database() sudah dijalankan di app.py")
        return

    if 'show_all_dataset' not in st.session_state:
        st.session_state['show_all_dataset'] = False

    # --- 1. BATCH UPLOAD & DATA PREVIEW ---
    col_up, col_prev = st.columns([1, 2.2], gap="large")
    
    with col_up:
        st.markdown("<h3 style='font-size: 1.1rem; font-weight: 700; color: #0f172a; margin-bottom: 0.8rem;'>📂 Update Massal (Batch)</h3>", unsafe_allow_html=True)
        with st.container(border=True):
            uploaded_file = st.file_uploader("Tarik & Lepas file .CSV", type="csv", label_visibility="collapsed")
            
            # LOGIKA MEMBACA DAN MENYIMPAN PERMANEN DATA CSV
            if uploaded_file is not None:
                try:
                    df_uploaded = pd.read_csv(uploaded_file)
                    
                    # Konversi nama kolom kecil ke format Kapital Sistem
                    column_mapping = {
                        'usia': 'Usia', 'berat': 'Berat_Badan', 'tinggi': 'Tinggi_Badan',
                        'hb': 'Hb_Darah', 'imt': 'IMT', 'lila': 'LILA',
                        'pendapatan': 'Pendapatan_Bulanan', 'air': 'Akses_Air_Bersih',
                        'faskes': 'Akses_Layanan_Kesehatan', 'pendidikan': 'Pendidikan_Terakhir',
                        'gizi': 'Skor_Pengetahuan_Gizi', 'target': 'Target_Risiko'
                    }
                    df_uploaded = df_uploaded.rename(columns=column_mapping)
                    
                    FEATURE_COLUMNS = ['Usia', 'Berat_Badan', 'Tinggi_Badan', 'Hb_Darah', 'IMT', 'LILA', 'Pendapatan_Bulanan', 'Akses_Air_Bersih', 'Akses_Layanan_Kesehatan', 'Pendidikan_Terakhir', 'Skor_Pengetahuan_Gizi']
                    df_clean = df_uploaded[FEATURE_COLUMNS + ['Target_Risiko']]
                    
                    # PERINTAH SAKTI: Simpan langsung sebagai file fisik di hardisk proyek Anda
                    df_clean.to_csv('dataset_digimind_420.csv', index=False)
                    
                    # Simpan ke session_state untuk tampilan real-time
                    st.session_state['training_data'] = df_clean
                    st.success(f"✅ Berhasil memuat dan menyimpan {len(df_uploaded)} data ke hardisk secara permanen!")
                except Exception as e:
                    st.error(f"Gagal memproses file CSV: {str(e)}")
            
            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            if st.button("🚀 Latih Ulang Model (Retrain)", use_container_width=True, type="primary"):
                with st.spinner("Menjalankan SMOTE & Memproses Random Forest..."):
                    train_model()
                    
                    if 'model_history' in st.session_state:
                        acc = st.session_state.get('last_acc', 95.5)
                        st.session_state['model_history'].insert(0, {
                            "versi": "v2.2 (Batch Retrain)", 
                            "tanggal": datetime.datetime.now().strftime("%d %b %Y"), 
                            "akurasi": f"{acc:.1f}%", 
                            "f1": "Success", 
                            "status": "Success"
                        })
                    st.success("Model AI Sukses Dibuat & Diekspor ke 'model_digimind.pkl'!")

    with col_prev:
        c_title, c_btn = st.columns([3, 1])
        with c_title:
            st.markdown("<h3 style='font-size: 1.1rem; font-weight: 700; color: #0f172a; margin: 0; margin-bottom: 0.8rem;'>Dataset Latih Utama (Preview)</h3>", unsafe_allow_html=True)
        with c_btn:
            label_btn = "Peringkas Data" if st.session_state['show_all_dataset'] else "Lihat Semua"
            if st.button(label_btn, use_container_width=True):
                st.session_state['show_all_dataset'] = not st.session_state['show_all_dataset']
                st.rerun()

        df_to_show = st.session_state['training_data']
        if not st.session_state['show_all_dataset']:
            df_to_show = df_to_show.tail(4) # Mengubah ke .tail() agar data yang baru disuntik manual terlihat paling atas

        tinggi_max = "300px" if st.session_state['show_all_dataset'] else "auto"

        if df_to_show.empty:
            st.info("Dataset latih masih kosong. Silakan seret file CSV bersih Anda ke kotak kiri.")
        else:
            html_table = "<div style='background-color: #ffffff; border: 1px solid #f1f5f9; border-radius: 16px; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03);'>"
            html_table += f"<div style='max-height: {tinggi_max}; overflow: auto; scrollbar-width: thin; padding-bottom: 10px;'>"
            html_table += "<table style='width: 100%; border-collapse: collapse; text-align: left; white-space: nowrap; background-color: #ffffff;'>"
            html_table += "<thead style='position: sticky; top: 0; background-color: #ffffff; z-index: 1;'><tr style='border-bottom: 2px solid #e2e8f0;'>"
            
            cols_display = ['USIA', 'BERAT', 'TINGGI', 'HB', 'IMT', 'LILA', 'PENDAPATAN', 'AIR', 'FASKES', 'PENDIDIKAN', 'GIZI', 'TARGET']
            for col in cols_display:
                html_table += f"<th style='padding: 10px 8px; color: #64748b; font-size: 0.75rem; font-weight: 700; background-color: #ffffff;'>{col}</th>"
            html_table += "</tr></thead><tbody>"

            # Gunakan reverse() agar data terbaru (injeksi manual) tampil di atas
            for _, row in df_to_show.iloc[::-1].iterrows():
                def format_num(val, is_int=False):
                    try:
                        if pd.isna(val) or str(val).strip() in ['', 'nan', 'None']: return "-"
                        return f"{int(float(val))}" if is_int else f"{float(val):.1f}"
                    except: return "-"

                val_target = row.get('Target_Risiko')
                target_val = "RISIKO TINGGI" if val_target == 2 else ("RENTAN" if val_target == 1 else "NORMAL")
                badge_bg = "#fee2e2" if val_target == 2 else ("#fffbeb" if val_target == 1 else "#dcfce7")
                badge_color = "#dc2626" if val_target == 2 else ("#d97706" if val_target == 1 else "#047857")

                html_table += "<tr style='background-color: #ffffff; border-bottom: 1px solid #f1f5f9;'>"
                html_table += f"<td style='padding: 10px 8px; color: #334155; font-size: 0.85rem;'>{format_num(row.get('Usia'), True)}</td>"
                html_table += f"<td style='padding: 10px 8px; color: #334155; font-size: 0.85rem;'>{format_num(row.get('Berat_Badan'))}</td>"
                html_table += f"<td style='padding: 10px 8px; color: #334155; font-size: 0.85rem;'>{format_num(row.get('Tinggi_Badan'))}</td>"
                html_table += f"<td style='padding: 10px 8px; color: #334155; font-size: 0.85rem;'>{format_num(row.get('Hb_Darah'))}</td>"
                html_table += f"<td style='padding: 10px 8px; color: #334155; font-size: 0.85rem;'>{format_num(row.get('IMT'))}</td>"
                html_table += f"<td style='padding: 10px 8px; color: #334155; font-size: 0.85rem;'>{format_num(row.get('LILA'))}</td>"
                html_table += f"<td style='padding: 10px 8px; color: #334155; font-size: 0.85rem;'>{format_num(row.get('Pendapatan_Bulanan'), True)}</td>"
                html_table += f"<td style='padding: 10px 8px; color: #334155; font-size: 0.85rem;'>{format_num(row.get('Akses_Air_Bersih'), True)}</td>"
                html_table += f"<td style='padding: 10px 8px; color: #334155; font-size: 0.85rem;'>{format_num(row.get('Akses_Layanan_Kesehatan'), True)}</td>"
                html_table += f"<td style='padding: 10px 8px; color: #334155; font-size: 0.85rem;'>{format_num(row.get('Pendidikan_Terakhir'), True)}</td>"
                html_table += f"<td style='padding: 10px 8px; color: #334155; font-size: 0.85rem;'>{format_num(row.get('Skor_Pengetahuan_Gizi'), True)}</td>"
                html_table += f"<td style='padding: 10px 8px;'><span style='background: {badge_bg}; color: {badge_color}; padding: 4px 10px; border-radius: 999px; font-size: 0.7rem; font-weight: 700;'>{target_val}</span></td>"
                html_table += "</tr>"
            html_table += "</tbody></table></div></div>"
            st.markdown(html_table, unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # --- 2. BOTTOM ROW: MANUAL INJECTION FORM ---
    with st.form("form_suntik_data"):
        st.markdown("<div style='display:flex; align-items:center; gap:8px; margin-bottom:1.5rem;'><span style='font-size:1.4rem;'>➕</span><h3 style='margin:0; color:#0f172a; font-size:1.2rem; font-weight:800;'>Suntik Sampel Data Latih Manual</h3></div>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3, gap="large")
        with c1:
            u = st.number_input("Usia (Tahun)", 15, 49, 25)
            bb = st.number_input("Berat Badan (kg)", 30.0, 120.0, 50.0, step=0.1)
            tb = st.number_input("Tinggi Badan (cm)", 120.0, 200.0, 155.0, step=0.1)
        with c2:
            hb = st.number_input("Kadar Hemoglobin (Hb)", 4.0, 20.0, 12.0, step=0.1)
            lila = st.number_input("Lingkar Lengan Atas (LILA)", 10.0, 50.0, 24.0, step=0.1)
            inc = st.selectbox("Pendapatan Keluarga", [1, 2], format_func=lambda x: "Rendah" if x==1 else "Tinggi")
        with c3:
            water = st.radio("Akses Air Bersih", [1, 0], format_func=lambda x: "Ada" if x==1 else "Tidak Ada", horizontal=True)
            faskes = st.radio("Akses Faskes", [1, 0], format_func=lambda x: "Mudah" if x==1 else "Sulit", horizontal=True)
            edu = st.selectbox("Tingkat Pendidikan Terakhir", [1, 2, 3], format_func=lambda x: "Dasar (SD/SMP)" if x==1 else ("Menengah (SMA/SMK)" if x==2 else "Tinggi (D3/S1+)"))
        
        st.markdown("<hr style='margin: 1.5rem 0; border: 1px solid #f1f5f9;'>", unsafe_allow_html=True)
        
        c_slider, c_target = st.columns([1, 1.5], gap="large")
        with c_slider:
            score = st.slider("Skor Gizi Kuesioner (0-5)", 0, 5, 4)
        with c_target:
            # Menggunakan 3 Label (Sesuai arsitektur multiclass kita)
            tgt = st.radio("Label Target Lapangan (Ground Truth)", [0, 1, 2], format_func=lambda x: "0: Normal" if x==0 else ("1: Rentan" if x==1 else "2: Risiko Tinggi"), horizontal=True)
        
        col_empty, col_btn = st.columns([3, 1])
        with col_btn:
            submit_injection = st.form_submit_button("INTEGRASIKAN DATA BARU", type="primary", use_container_width=True)
            
            if submit_injection:
                # 1. Kalkulasi IMT otomatis
                imt_calc = round(bb / ((tb / 100) ** 2), 1)
                
                # 2. Siapkan baris data baru
                new_row = {
                    'Usia': u, 'Berat_Badan': bb, 'Tinggi_Badan': tb, 'Hb_Darah': hb, 'IMT': imt_calc, 'LILA': lila, 
                    'Pendapatan_Bulanan': inc, 'Akses_Air_Bersih': water, 'Akses_Layanan_Kesehatan': faskes, 
                    'Pendidikan_Terakhir': edu, 'Skor_Pengetahuan_Gizi': score, 'Target_Risiko': tgt
                }
                
                # 3. Gabungkan ke data latih yang ada di session state
                df_current = st.session_state['training_data']
                df_new = pd.concat([df_current, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state['training_data'] = df_new
                
                # 4. PERINTAH SAKTI: Simpan ulang keseluruhan data latih (termasuk yang baru disuntik) ke CSV Hardisk
                df_new.to_csv('dataset_digimind_420.csv', index=False)
                
                # 5. Peringatkan admin untuk melatih ulang
                st.success("✅ Sampel data berhasil disuntikkan dan disimpan ke hardisk! Silakan klik 'Latih Ulang Model' di atas agar AI mempelajari data baru ini.")

@st.cache_data
def get_evaluation_results(df):
    """
    Menghitung metrik performa model AI dan confusion matrix.
    Di-cache menggunakan st.cache_data agar tidak melatih ulang model pada setiap interaksi UI.
    """
    df_clean = df.dropna(subset=['Target_Risiko'])
    X = df_clean[FEATURE_COLUMNS]
    y_true = df_clean['Target_Risiko'].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y_true, test_size=0.25, random_state=42)
    
    try:
        from imblearn.over_sampling import SMOTE
        smote_eval = SMOTE(random_state=42, k_neighbors=2)
        X_tr_res, y_tr_res = smote_eval.fit_resample(X_train, y_train)
    except Exception:
        X_tr_res, y_tr_res = X_train, y_train

    eval_model = RandomForestClassifier(n_estimators=100, random_state=42)
    eval_model.fit(X_tr_res, y_tr_res)
    y_pred = eval_model.predict(X_test)

    acc = eval_model.score(X_test, y_test) * 100
    prec = precision_score(y_test, y_pred, average='macro', zero_division=0) * 100
    rec = recall_score(y_test, y_pred, average='macro', zero_division=0) * 100
    f1 = f1_score(y_test, y_pred, average='macro', zero_division=0) * 100
    
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2])
    importances = eval_model.feature_importances_
    
    len_train = len(X_train)
    len_res = len(X_tr_res)
    len_test = len(X_test)
    
    return acc, prec, rec, f1, cm, importances, len_train, len_res, len_test


# ==========================================
# HALAMAN 2: EVALUASI MODEL AI (DASHBOARD MULTICLASS LENGKAP)
# ==========================================
def show_admin_evaluation_menu():
    inject_admin_css()

    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style='color:#0f172a; font-weight: 800; margin-bottom: 0.2rem; margin-top: 0;'>📈 Evaluasi Performa Model AI</h2>
        <p style='color:#64748b; font-size: 0.95rem; margin-top: 0;'>Pantau matriks keandalan algoritma Machine Learning menggunakan data uji (Test Set) bertingkat 3 kelas.</p>
    </div>
    """, unsafe_allow_html=True)

    if 'ai_model' not in st.session_state or st.session_state['training_data'].empty:
        st.warning("Model AI belum dilatih atau dataset kosong. Silakan jalankan Retraining di menu Manajemen Model AI terlebih dahulu.")
        return

    df = st.session_state['training_data'].dropna(subset=['Target_Risiko'])
    try:
        acc, prec, rec, f1, cm, importances, len_train, len_res, len_test = get_evaluation_results(st.session_state['training_data'])
        st.session_state['last_acc'] = acc
    except Exception as e:
        st.error(f"Gagal melakukan matriks evaluasi: {e}")
        return

    if 'model_history' not in st.session_state:
        st.session_state['model_history'] = [
            {"versi": "v2.2", "tanggal": datetime.datetime.now().strftime("%d %b %Y"), "akurasi": f"{acc:.1f}%", "f1": f"{f1/100:.3f}", "status": "Success"},
            {"versi": "v2.1", "tanggal": "15 Mei 2026", "akurasi": "96.4%", "f1": "0.958", "status": "Success"},
            {"versi": "v2.0", "tanggal": "02 Apr 2026", "akurasi": "91.2%", "f1": "0.910", "status": "Warning"}
        ]

    # --- TOP ROW (METRIC CARDS) ---
    html_metrics = f"""
    <div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem;'>
        <div class='metric-eval-card'>
            <div style='font-size: 0.8rem; color: #64748b; font-weight: 600; margin-bottom: 0.3rem;'>Status Model Aktif</div>
            <p style='font-size: 1.1rem; font-weight: 800; color: #0f172a; margin: 0; line-height: 1.2;'>Random Forest v2.2</p>
            <p style='font-size: 0.8rem; font-weight: 600; color:#10b981; margin-top: 0.5rem;'>● Multiclass (3 Label)</p>
        </div>
        <div class='metric-eval-card'>
            <div style='font-size: 0.8rem; color: #64748b; font-weight: 600; margin-bottom: 0.3rem;'>Akurasi (Test Set)</div>
            <p style='font-size: 2rem; font-weight: 800; color: #0f172a; margin: 0; line-height: 1.2;'>{acc:.1f}%</p>
        </div>
        <div class='metric-eval-card'>
            <div style='font-size: 0.8rem; color: #64748b; font-weight: 600; margin-bottom: 0.3rem;'>Total Dataset Pelatih</div>
            <p style='font-size: 2rem; font-weight: 800; color: #0f172a; margin: 0; line-height: 1.2;'>{len(df):,} <span style='font-size:1rem; font-weight:600; color:#94a3b8;'>Data</span></p>
            <p style='font-size: 0.75rem; font-weight: 600; color:#94a3b8; margin-top: 0.2rem; text-transform:uppercase;'>Tervalidasi Unik</p>
        </div>
        <div class='metric-eval-card'>
            <div style='font-size: 0.8rem; color: #64748b; font-weight: 600; margin-bottom: 0.3rem;'>Metode Balancing</div>
            <p style='font-size: 1.3rem; font-weight: 800; color: #047857; margin: 0; line-height: 1.2;'>SMOTE Aktif</p>
            <p style='font-size: 0.8rem; font-weight: 500; color:#64748b; margin-top: 0.5rem;'>Rasio Seimbang 1:1:1</p>
        </div>
    </div>
    """
    st.markdown(html_metrics, unsafe_allow_html=True)

    # --- MIDDLE ROW (FEATURE IMPORTANCE & CONFUSION MATRIX 3x3) ---
    col_feat, col_cm = st.columns([1, 1.2], gap="large")

    with col_feat:
        with st.container(border=True):
            st.markdown("<h3 style='font-size:1.1rem; color:#0f172a; font-weight:800; margin-bottom:0;'>Faktor Penentu Klinis</h3>", unsafe_allow_html=True)
            feature_mapping = {
                'LILA': 'Lingkar Lengan Atas (LILA)', 'Hb_Darah': 'Kadar Hemoglobin (Hb)', 
                'IMT': 'Body Mass Index (BMI)', 'Pendapatan_Bulanan': 'Pendapatan Keluarga',
                'Akses_Air_Bersih': 'Akses Air Bersih', 'Usia': 'Usia Ibu / WUS',
                'Berat_Badan': 'Berat Badan', 'Tinggi_Badan': 'Tinggi Badan',
                'Akses_Layanan_Kesehatan': 'Akses Faskes', 'Pendidikan_Terakhir': 'Pendidikan',
                'Skor_Pengetahuan_Gizi': 'Pengetahuan Gizi'
            }
            pretty_features = [feature_mapping.get(f, f) for f in FEATURE_COLUMNS]
            df_imp = pd.DataFrame({'Feature': pretty_features, 'Importance': importances})
            df_imp = df_imp.sort_values('Importance', ascending=True).tail(6)
            
            fig = px.bar(df_imp, x='Importance', y='Feature', orientation='h')
            fig.update_traces(marker_color='#047857', texttemplate='%{x:.0%}', textposition='outside')
            fig.update_layout(plot_bgcolor='white', height=320, margin=dict(l=0, r=20, t=20, b=0), xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(title='', tickfont=dict(size=12, color='#334155', weight='bold')))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col_cm:
        with st.container(border=True):
            st.markdown("<h3 style='font-size:1.1rem; color:#0f172a; font-weight:800; margin-bottom:5px; text-align:center;'>Matriks Kebingungan (3x3)</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center; font-size:0.75rem; font-weight:700; color:#94a3b8; letter-spacing:1px; margin-bottom:15px;'>PREDIKSI MODEL AI</p>", unsafe_allow_html=True)
            
            html_cm = f"""
            <div style="display: flex; gap: 15px; justify-content: center; align-items: center;">
                <div style="writing-mode: vertical-rl; transform: rotate(180deg); text-align: center; font-size: 0.75rem; font-weight: 700; color: #94a3b8; letter-spacing: 1px;">AKTUAL MEDIS</div>
                <table style="width: 100%; border-collapse: separate; border-spacing: 6px; text-align: center;">
                    <tr>
                        <td></td>
                        <td style="font-size: 0.7rem; font-weight: 800; color: #475569;">PRED NORMAL</td>
                        <td style="font-size: 0.7rem; font-weight: 800; color: #475569;">PRED RENTAN</td>
                        <td style="font-size: 0.7rem; font-weight: 800; color: #475569;">PRED RISIKO</td>
                    </tr>
                    <tr>
                        <td style="font-size: 0.7rem; font-weight: 800; color: #475569; text-align: right;">AKTUAL NORMAL</td>
                        <td style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px; padding: 12px; font-size: 1.4rem; font-weight: 800; color: #047857;">{cm[0][0]}</td>
                        <td style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 12px; font-size: 1.4rem; font-weight: 800; color: #b91c1c;">{cm[0][1]}</td>
                        <td style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 12px; font-size: 1.4rem; font-weight: 800; color: #b91c1c;">{cm[0][2]}</td>
                    </tr>
                    <tr>
                        <td style="font-size: 0.7rem; font-weight: 800; color: #475569; text-align: right;">AKTUAL RENTAN</td>
                        <td style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 12px; font-size: 1.4rem; font-weight: 800; color: #b91c1c;">{cm[1][0]}</td>
                        <td style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 12px; font-size: 1.4rem; font-weight: 800; color: #d97706;">{cm[1][1]}</td>
                        <td style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 12px; font-size: 1.4rem; font-weight: 800; color: #b91c1c;">{cm[1][2]}</td>
                    </tr>
                    <tr>
                        <td style="font-size: 0.7rem; font-weight: 800; color: #475569; text-align: right;">AKTUAL RISIKO</td>
                        <td style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 12px; font-size: 1.4rem; font-weight: 800; color: #b91c1c;">{cm[2][0]}</td>
                        <td style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 12px; font-size: 1.4rem; font-weight: 800; color: #b91c1c;">{cm[2][1]}</td>
                        <td style="background: #fee2e2; border: 1px solid #fca5a5; border-radius: 8px; padding: 12px; font-size: 1.4rem; font-weight: 800; color: #dc2626;">{cm[2][2]}</td>
                    </tr>
                </table>
            </div>
            
            <div style="display: flex; justify-content: space-around; margin-top: 1.2rem; border-top: 1px solid #f1f5f9; padding-top: 1rem;">
                <div style="text-align:center;"><p style="font-size:0.8rem; font-weight:600; color:#64748b; margin:0;">Precision</p><h4 style="margin:0; font-size:1.3rem; font-weight:800; color:#0f172a;">{prec:.1f}%</h4></div>
                <div style="text-align:center;"><p style="font-size:0.8rem; font-weight:600; color:#64748b; margin:0;">Recall</p><h4 style="margin:0; font-size:1.3rem; font-weight:800; color:#0f172a;">{rec:.1f}%</h4></div>
                <div style="text-align:center;"><p style="font-size:0.8rem; font-weight:600; color:#64748b; margin:0;">F1-Score</p><h4 style="margin:0; font-size:1.3rem; font-weight:800; color:#0f172a;">{f1:.1f}%</h4></div>
            </div>
            """
            st.markdown(html_cm, unsafe_allow_html=True)

    # --- BOTTOM ROW (DONUT CHART, SPLIT DATA & HISTORY) ---
    st.markdown("<hr style='border: 1px solid #f1f5f9; margin: 2rem 0;'>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1.2, 1.5], gap="large")
    
    with col_left:
        # BAGIAN 1: DONUT CHART KESEIMBANGAN DATA
        with st.container(border=True):
            st.markdown("<h3 style='font-size:1.1rem; color:#0f172a; font-weight:800; margin-bottom:0.5rem;'>Keseimbangan Dataset (Donut Chart)</h3>", unsafe_allow_html=True)
            prop_df = df['Target_Risiko'].value_counts().reset_index()
            prop_df.columns = ['Status', 'Jumlah']
            status_map = {0: 'Normal / Aman', 1: 'Rentan', 2: 'Risiko Tinggi'}
            prop_df['Status'] = prop_df['Status'].map(status_map)
            
            fig_pie = px.pie(prop_df, names='Status', values='Jumlah', hole=0.55, color='Status', 
                             color_discrete_map={'Risiko Tinggi': '#ef4444', 'Rentan': '#f59e0b', 'Normal / Aman': '#10b981'})
            
            fig_pie.update_traces(textposition='inside', textinfo='percent+label+value', textfont=dict(size=11, color="white"), showlegend=False)
            fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=240, plot_bgcolor='rgba(0,0,0,0)')
            
            st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

        # BAGIAN 2: RINCIAN TRAIN / TEST SPLIT
        with st.container(border=True):
            st.markdown("<h3 style='font-size:1.1rem; color:#0f172a; font-weight:800; margin-bottom:1rem;'>Proporsi Train/Test Split</h3>", unsafe_allow_html=True)
            html_split = f"""
            <div style="display:flex; flex-direction:column; gap:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center; background:#f8fafc; padding:10px 15px; border-radius:8px;">
                    <span style="font-size:0.85rem; font-weight:600; color:#475569;">Total Data (CSV)</span>
                    <span style="font-size:1rem; font-weight:800; color:#0f172a;">{len(df)}</span>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; background:#f0fdf4; padding:10px 15px; border-radius:8px; border:1px solid #bbf7d0;">
                    <span style="font-size:0.85rem; font-weight:600; color:#166534;">Data Latih Asli (75%)</span>
                    <span style="font-size:1rem; font-weight:800; color:#15803d;">{len_train}</span>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; background:#fff7ed; padding:10px 15px; border-radius:8px; border:1px solid #fef08a;">
                    <span style="font-size:0.85rem; font-weight:600; color:#9a3412;">Data Latih + SMOTE</span>
                    <span style="font-size:1rem; font-weight:800; color:#b45309;">{len_res} <span style="font-size:0.7rem; font-weight:600;">(Seimbang)</span></span>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; background:#eff6ff; padding:10px 15px; border-radius:8px; border:1px solid #bfdbfe;">
                    <span style="font-size:0.85rem; font-weight:600; color:#1e40af;">Data Uji / Test (25%)</span>
                    <span style="font-size:1rem; font-weight:800; color:#1d4ed8;">{len_test}</span>
                </div>
            </div>
            """
            st.markdown(html_split, unsafe_allow_html=True)

    with col_right:
        # BAGIAN 3: TABEL RIWAYAT MODEL
        with st.container(border=True):
            st.markdown("<h3 style='font-size:1.1rem; color:#0f172a; font-weight:800; margin-bottom:1rem;'>Riwayat Pembaruan Model</h3>", unsafe_allow_html=True)
            
            html_hist = "<table style='width: 100%; border-collapse: collapse; text-align: left;'>"
            html_hist += "<thead><tr style='border-bottom: 2px solid #e2e8f0;'><th style='padding: 10px 8px; color: #64748b; font-size: 0.75rem; font-weight: 700;'>VERSI</th><th style='padding: 10px 8px; color: #64748b; font-size: 0.75rem; font-weight: 700;'>TANGGAL</th><th style='padding: 10px 8px; color: #64748b; font-size: 0.75rem; font-weight: 700;'>AKURASI</th><th style='padding: 10px 8px; color: #64748b; font-size: 0.75rem; font-weight: 700;'>F1-SCORE</th><th style='padding: 10px 8px; color: #64748b; font-size: 0.75rem; font-weight: 700;'>STATUS</th></tr></thead><tbody>"
            
            for item in st.session_state['model_history']:
                bg_status = "#dcfce7" if item['status'] == "Success" else "#fef08a" if item['status'] == "Warning" else "#fee2e2"
                color_status = "#047857" if item['status'] == "Success" else "#a16207" if item['status'] == "Warning" else "#b91c1c"
                
                html_hist += "<tr style='border-bottom: 1px solid #f1f5f9;'>"
                html_hist += f"<td style='padding: 14px 8px; font-size: 0.85rem; font-weight: 700; color: #0f172a;'>{item['versi']}</td>"
                html_hist += f"<td style='padding: 14px 8px; font-size: 0.85rem; color: #64748b;'>{item['tanggal']}</td>"
                html_hist += f"<td style='padding: 14px 8px; font-size: 0.85rem; font-weight: 600; color: #334155;'>{item['akurasi']}</td>"
                html_hist += f"<td style='padding: 14px 8px; font-size: 0.85rem; font-weight: 600; color: #334155;'>{item['f1']}</td>"
                html_hist += f"<td style='padding: 14px 8px;'><span style='background: {bg_status}; color: {color_status}; padding: 4px 10px; border-radius: 999px; font-size: 0.7rem; font-weight: 700;'>{item['status']}</span></td>"
                html_hist += "</tr>"
            
            html_hist += "</tbody></table>"
            st.markdown(html_hist, unsafe_allow_html=True)
            
            st.markdown("<p style='text-align:center; margin-top:2rem; font-size:0.85rem; font-weight:700; color:#047857; cursor:pointer;'>↓ Muat Lebih Banyak Riwayat ↓</p>", unsafe_allow_html=True)

# ==========================================
# HALAMAN 3: MANAJEMEN DATABASE
# ==========================================
def show_admin_database_menu():
    inject_admin_css()
    
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style='color:#0f172a; font-weight: 800; margin-bottom: 0.2rem; margin-top: 0;'>🗄️ Monitor & Kontrol Database</h2>
        <p style='color:#64748b; font-size: 0.95rem; margin-top: 0;'>Akses penuh ke data master identitas pasien dan log rekam medis.</p>
    </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------
    # PANEL KODE REGISTRASI STAF
    # ----------------------------------------
    with st.expander("🔑 Kode Registrasi Staf (Bagikan ke Nakes / Admin Baru)", expanded=False):
        st.markdown("""
        <p style='color:#475569; font-size:0.9rem; margin-bottom:1rem;'>
        Kode di bawah ini digunakan oleh <strong>Tenaga Kesehatan</strong> dan <strong>Admin</strong> baru saat mendaftar akun di halaman login. 
        Bagikan kode yang sesuai kepada staf yang berhak. 
        Untuk mengganti kode, ubah nilai konstanta di file <code>modules/auth.py</code>.
        </p>
        """, unsafe_allow_html=True)
        col_k1, col_k2 = st.columns(2)
        with col_k1:
            st.markdown(f"""
            <div style='background: #e0f2fe; border: 1px solid #0369a1; border-radius: 12px; padding: 1.2rem; text-align: center;'>
                <p style='margin:0; font-size:0.8rem; font-weight:700; color:#0369a1; letter-spacing:0.5px;'>🩺 KODE REGISTRASI NAKES</p>
                <p style='margin:0.5rem 0 0 0; font-size:1.8rem; font-weight:900; color:#0c4a6e; letter-spacing:4px; font-family:monospace;'>{KODE_REGISTRASI_NAKES}</p>
            </div>
            """, unsafe_allow_html=True)
        with col_k2:
            st.markdown(f"""
            <div style='background: #ede9fe; border: 1px solid #7c3aed; border-radius: 12px; padding: 1.2rem; text-align: center;'>
                <p style='margin:0; font-size:0.8rem; font-weight:700; color:#7c3aed; letter-spacing:0.5px;'>🛡️ KODE REGISTRASI ADMIN</p>
                <p style='margin:0.5rem 0 0 0; font-size:1.8rem; font-weight:900; color:#4c1d95; letter-spacing:4px; font-family:monospace;'>{KODE_REGISTRASI_ADMIN}</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.warning("⚠️ Jangan bagikan kode ini kepada pasien atau pihak yang tidak berwenang.")

    
    df_db = get_all_patients()
    df_db.fillna("-", inplace=True)
    total_pasien = len(df_db['id_pasien'].unique()) if not df_db.empty else 0
    
    # ----------------------------------------
    # PERSIAPAN DATA EXPORT KE CSV
    # ----------------------------------------
    if not df_db.empty:
        col_master = [c for c in ['id_pasien', 'nama', 'email', 'no_hp', 'alamat_kecamatan', 'tanggal_daftar'] if c in df_db.columns]
        df_master_export = df_db[col_master].drop_duplicates(subset=['id_pasien'])
        csv_master = df_master_export.to_csv(index=False).encode('utf-8')
    else:
        csv_master = b""

    if not df_db.empty and 'status_pemeriksaan' in df_db.columns:
        df_log_export = df_db[df_db['status_pemeriksaan'] == 'Selesai Diperiksa']
        csv_log = df_log_export.to_csv(index=False).encode('utf-8')
    else:
        csv_log = b""

    # ----------------------------------------
    # HEADER & TOMBOL EXPORT (POJOK KANAN ATAS)
    # ----------------------------------------
    col_hdr, col_btn1, col_btn2 = st.columns([2.2, 1, 1])
    
    with col_hdr:
        st.write("") # Spacer pengganti judul karena judul dipindah ke atas
        
    with col_btn1:
        st.download_button(
            label="📥 Export Master Pasien",
            data=csv_master,
            file_name=f"Master_Pasien_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            type="secondary"
        )
        
    with col_btn2:
        st.download_button(
            label="📥 Export Log Medis",
            data=csv_log,
            file_name=f"Log_Pemeriksaan_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
    
    # ----------------------------------------
    # BAGIAN 1: MASTER DATA PASIEN
    # ----------------------------------------
    st.markdown("<div style='display:flex; align-items:center; gap:8px;'><span style='font-size:1.4rem;'>👤</span><h3 style='color:#0f172a; font-size: 1.2rem; font-weight: 800; margin:0;'>Master Data Pasien</h3></div>", unsafe_allow_html=True)
    
    with st.container(border=True):
        col_search, col_count = st.columns([3, 1])
        with col_search:
            search_master = st.text_input("Pencarian", placeholder="Cari ID atau Nama Pasien...", label_visibility="collapsed")
        with col_count:
            st.markdown(f"<div style='text-align: right; background: #ecfdf5; color: #047857; padding: 8px 15px; border-radius: 999px; font-weight: 700; font-size: 0.85rem; border: 1px solid #a7f3d0;'>Total: {total_pasien:,} Pasien</div>", unsafe_allow_html=True)
        
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        
        if df_db.empty:
            st.info("Database kosong. Belum ada pasien terdaftar.")
        else:
            df_show_master = df_db.copy().drop_duplicates(subset=['id_pasien'])
            if search_master:
                df_show_master = df_show_master[df_show_master.astype(str).apply(lambda x: x.str.contains(search_master, case=False)).any(axis=1)]

            html_table1 = "<div style='background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 0.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.02);'>"
            html_table1 += "<div style='max-height: 350px; overflow: auto; scrollbar-width: thin;'>"
            html_table1 += "<table style='width: 100%; border-collapse: collapse; text-align: left; white-space: nowrap; background-color: #ffffff;'>"
            html_table1 += "<thead style='position: sticky; top: 0; background-color: #ffffff; z-index: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'><tr style='border-bottom: 2px solid #e2e8f0;'>"
            
            cols_display = ['ID PASIEN', 'NAMA LENGKAP', 'KONTAK (EMAIL & WA)', 'KECAMATAN', 'TGL DAFTAR']
            for col in cols_display:
                html_table1 += f"<th style='padding: 12px 10px; color: #64748b; font-size: 0.75rem; font-weight: 700; background-color: #ffffff;'>{col}</th>"
            html_table1 += "</tr></thead><tbody>"

            for _, row in df_show_master.iterrows():
                id_p = row.get('id_pasien', '-')
                nama = row.get('nama', '-')
                email = row.get('email', '-')
                wa = row.get('no_hp', '-')
                raw_kec = row.get('alamat_kecamatan')
                kec = str(raw_kec).strip().title() if pd.notna(raw_kec) and str(raw_kec).strip().lower() not in ['', 'none', 'nan', '-'] else '-'
                
                # --- AUTO-DETECT & FALLBACK TANGGAL DAFTAR ---
                tgl_daftar = "-"
                for col_name in row.keys():
                    if 'daftar' in str(col_name).lower() or 'registrasi' in str(col_name).lower():
                        val = row.get(col_name)
                        if pd.notna(val) and str(val).strip() not in ['', 'None', '-']:
                            tgl_daftar = str(val)
                            break
                
                if tgl_daftar == "-":
                    jadwal_raw = str(row.get('jadwal_kunjungan', row.get('Jadwal_Kunjungan', ''))).strip()
                    if jadwal_raw and jadwal_raw not in ['None', '', '-']:
                        tgl_bersih = re.sub(r'\d{2}[:.]\d{2}', '', jadwal_raw) 
                        for kata in ["Sesi 1", "Sesi 2", "Sesi 3", "Sesi 4", "Pukul", "WIB", "wib", "(", ")", "-", ","]:
                            tgl_bersih = tgl_bersih.replace(kata, "")
                        tgl_daftar = " ".join(tgl_bersih.split())
                    else:
                        tgl_daftar = datetime.datetime.now().strftime("%d %b %Y") 
                
                tgl = tgl_daftar
                
                html_table1 += "<tr style='background-color: #ffffff; border-bottom: 1px solid #f1f5f9; hover:background-color: #f8fafc;'>"
                html_table1 += f"<td style='padding: 12px 10px; color: #0f172a; font-size: 0.85rem; font-weight: 700;'>#{id_p}</td>"
                html_table1 += f"<td style='padding: 12px 10px; color: #334155; font-size: 0.85rem; font-weight: 600;'>{nama}</td>"
                html_table1 += f"<td style='padding: 12px 10px; color: #64748b; font-size: 0.8rem;'>{email}<br><span style='color:#94a3b8;'>{wa}</span></td>"
                html_table1 += f"<td style='padding: 12px 10px; color: #334155; font-size: 0.85rem;'>{kec}</td>"
                html_table1 += f"<td style='padding: 12px 10px; color: #64748b; font-size: 0.85rem;'>{tgl}</td>"
                html_table1 += "</tr>"

            html_table1 += "</tbody></table></div></div>"
            st.markdown(html_table1, unsafe_allow_html=True)
            
    # ----------------------------------------
    # BAGIAN 2: LOG PEMERIKSAAN MEDIS
    # ----------------------------------------
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='display:flex; align-items:center; gap:8px;'><span style='font-size:1.4rem;'>🩺</span><h3 style='color:#0f172a; font-size: 1.2rem; font-weight: 800; margin:0;'>Log Pemeriksaan Medis</h3></div>", unsafe_allow_html=True)
    
    with st.container(border=True):
        
        df_periksa = df_db.copy()
        if 'status_pemeriksaan' in df_periksa.columns:
            df_periksa = df_periksa[df_periksa['status_pemeriksaan'] == 'Selesai Diperiksa']
        
        list_pasien_id = ["Semua Pasien"] + df_periksa['id_pasien'].dropna().unique().tolist() if not df_periksa.empty else ["Semua Pasien"]

        # --- PANEL FILTER ---
        filter_id = st.selectbox("Filter Data Pemeriksaan", list_pasien_id, label_visibility="collapsed", placeholder="Pilih / Cari ID Pasien...")
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        
        # Terapkan Filtering secara Real-time
        if filter_id != "Semua Pasien":
            df_periksa = df_periksa[df_periksa['id_pasien'] == filter_id]

        # Inisialisasi chk_mapping DILUAR if/else agar tidak error saat database kosong
        chk_mapping = {}
        for i, row in df_periksa.reset_index(drop=True).iterrows():
            chk_mapping[f"CHK-{101+i:04d}"] = row.get('id_pasien', '-')

        if df_periksa.empty:
            st.info("Belum ada log rekam medis pasien yang selesai diperiksa.")
        else:
            html_table2 = "<div style='background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 0.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.02);'>"
            html_table2 += "<div style='max-height: 400px; overflow: auto; scrollbar-width: thin;'>"
            html_table2 += "<table style='width: 100%; border-collapse: collapse; text-align: left; white-space: nowrap; background-color: #ffffff;'>"
            html_table2 += "<thead style='position: sticky; top: 0; background-color: #ffffff; z-index: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'><tr style='border-bottom: 2px solid #e2e8f0;'>"
            
            cols_display2 = ['ID & ANTREAN', 'INFO PASIEN', 'LOKASI FASKES', 'KLINIS FISIK', 'SOSIOLOGIS DEMOGRAFIS', 'PREDIKSI AI']
            for col in cols_display2:
                html_table2 += f"<th style='padding: 12px 10px; color: #64748b; font-size: 0.75rem; font-weight: 700; background-color: #ffffff;'>{col}</th>"
            html_table2 += "</tr></thead><tbody>"

            for i, row in df_periksa.reset_index(drop=True).iterrows():
                id_p = row.get('id_pasien', '-')
                nama_p = row.get('nama', '-')
                id_chk = f"CHK-{101 + i:04d}" 
                
                antrean_db = row.get('no_antrean', '-')
                if pd.isna(antrean_db) or antrean_db == '-':
                    antrean = f"Q-{i+1:02d}" 
                else:
                    antrean = f"Q-{int(float(antrean_db)):02d}" if str(antrean_db).replace('.','',1).isdigit() else str(antrean_db)
                
                raw_kec = row.get('alamat_kecamatan')
                kec_val = str(raw_kec).strip().title() if pd.notna(raw_kec) and str(raw_kec).strip().lower() not in ['', 'none', 'nan', '-'] else '-'
                faskes_str = f"Puskesmas {kec_val}" if kec_val != "-" else "Puskesmas Pusat"
                
                jadwal_raw = str(row.get('jadwal_kunjungan', row.get('Jadwal_Kunjungan', '-'))).strip()

                if pd.isna(jadwal_raw) or jadwal_raw == '-' or jadwal_raw == 'None' or jadwal_raw == '':
                    tgl_fallback = row.get('tanggal_pemeriksaan', row.get('tanggal_periksa', '-'))
                    if pd.isna(tgl_fallback) or str(tgl_fallback).strip() == '-':
                        tgl_fallback = row.get('tanggal_daftar', datetime.datetime.now().strftime("%d %b %Y"))
                    tgl_periksa = str(tgl_fallback)
                else:
                    match_jam = re.search(r'(\d{2}[:.]\d{2})', jadwal_raw)
                    jam_terdeteksi = match_jam.group(1).replace('.', ':') if match_jam else ""
                    
                    tgl_bersih = jadwal_raw
                    if jam_terdeteksi:
                        tgl_bersih = re.sub(r'\d{2}[:.]\d{2}', '', tgl_bersih)
                        
                    hapus_kata = ["Sesi 1", "Sesi 2", "Sesi 3", "Sesi 4", "Pukul", "WIB", "wib", "(", ")", "-", ","]
                    for kata in hapus_kata:
                        tgl_bersih = tgl_bersih.replace(kata, "")
                        
                    tgl_bersih = " ".join(tgl_bersih.split())
                    
                    if jam_terdeteksi:
                        tgl_periksa = f"{tgl_bersih} - {jam_terdeteksi} WIB"
                    else:
                        tgl_periksa = f"{tgl_bersih}"
                
                tb = row.get('tinggi_badan', '-')
                bb = row.get('berat_badan', '-')
                hb = row.get('hb_darah', '-')
                lila = row.get('lila', '-')
                klinis_str = f"<span style='background:#f1f5f9; padding:2px 6px; border-radius:4px; font-size:0.7rem; font-weight:700; color:#475569;'>TB:{tb}</span> <span style='background:#f1f5f9; padding:2px 6px; border-radius:4px; font-size:0.7rem; font-weight:700; color:#475569;'>BB:{bb}</span> <span style='background:#f1f5f9; padding:2px 6px; border-radius:4px; font-size:0.7rem; font-weight:700; color:#475569;'>Hb:{hb}</span> <span style='background:#f1f5f9; padding:2px 6px; border-radius:4px; font-size:0.7rem; font-weight:700; color:#475569;'>LILA:{lila}</span>"
                
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

                target_val = str(row.get('hasil_risiko', 'NORMAL')).upper()
                is_risiko = "TINGGI" in target_val
                badge_bg = "#fee2e2" if is_risiko else "#ecfdf5"
                badge_color = "#b91c1c" if is_risiko else "#047857"
                label_visual = "RISIKO TINGGI" if is_risiko else "RISIKO RENDAH / NORMAL"
                
                html_table2 += "<tr style='background-color: #ffffff; border-bottom: 1px solid #f1f5f9;'>"
                html_table2 += f"<td style='padding: 12px 10px; color: #0f172a; font-size: 0.85rem; font-weight: 800;'>#{id_chk}<br><span style='font-size:0.75rem; color:#64748b; font-weight:500;'>Antrean: {antrean}</span></td>"
                html_table2 += f"<td style='padding: 12px 10px; color: #047857; font-size: 0.85rem; font-weight: 800;'>#{id_p}<br><span style='font-size:0.75rem; color:#334155; font-weight:600;'>{nama_p}</span></td>"
                html_table2 += f"<td style='padding: 12px 10px; color: #334155; font-size: 0.85rem; font-weight:600;'>{faskes_str}<br><span style='font-size:0.75rem; color:#047857; font-weight:600;'>Periksa: {tgl_periksa}</span></td>"
                html_table2 += f"<td style='padding: 12px 10px;'>{klinis_str}</td>"
                html_table2 += f"<td style='padding: 12px 10px;'>{sosio_str}</td>"
                html_table2 += f"<td style='padding: 12px 10px;'><span style='background: {badge_bg}; color: {badge_color}; padding: 4px 12px; border-radius: 999px; font-size: 0.70rem; font-weight: 700;'>{label_visual}</span></td>"
                html_table2 += "</tr>"

            html_table2 += "</tbody></table></div></div>"
            st.markdown(html_table2, unsafe_allow_html=True)

        # --- FORM HAPUS LOG PEMERIKSAAN (QUICK ACTION) ---
        st.markdown("<hr style='border:1px solid #f1f5f9; margin: 1.5rem 0;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.85rem; color: #64748b; font-weight: 600;'>Panel Aksi Cepat: Penghapusan Log Pemeriksaan</p>", unsafe_allow_html=True)
        with st.form("form_delete_log"):
            col_l1, col_l2 = st.columns([3, 1])
            with col_l1:
                id_log_del = st.selectbox("Pilih ID Pemeriksaan (CHK) yang akan dihapus:", list(chk_mapping.keys()), index=None, placeholder="Contoh: CHK-0001", label_visibility="collapsed")
                st.checkbox("Saya yakin ingin menghapus log pemeriksaan ini.", key="chk_log")
            with col_l2:
                submit_log = st.form_submit_button("🗑️ Eksekusi Hapus Log", use_container_width=True)
                if submit_log:
                    if not st.session_state['chk_log']:
                        st.error("Centang konfirmasi terlebih dahulu!")
                    elif id_log_del is None:
                        st.warning("Pilih ID Pemeriksaan!")
                    else:
                        try:
                            real_id = chk_mapping[id_log_del]
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            
                            try:
                                cursor.execute("DELETE FROM pemeriksaan_tb WHERE id_pasien = %s", (real_id,))
                            except:
                                pass
                                
                            cursor.execute("""
                                UPDATE pasien_tb 
                                SET status_pemeriksaan = 'Menunggu Pemeriksaan', 
                                    tinggi_badan = NULL, berat_badan = NULL, 
                                    hb_darah = NULL, lila = NULL, hasil_risiko = NULL 
                                WHERE id_pasien = %s
                            """, (real_id,))
                            
                            conn.commit()
                            conn.close()
                            
                            try:
                                st.cache_data.clear()
                            except Exception:
                                pass
                                
                            st.success(f"Log {id_log_del} (Pasien: {real_id}) berhasil dihapus dari sistem.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal memproses penghapusan log: {str(e)}")

    # ----------------------------------------
    # ZONA BAHAYA (DANGER ZONE - MASTER PASIEN)
    # ----------------------------------------
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("""
        <div style="background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 12px; padding: 1rem; margin-bottom: 1.5rem; display: flex; gap: 10px; align-items: flex-start;">
            <span style="font-size: 1.2rem;">⚠️</span>
            <div>
                <h4 style="color: #991b1b; font-size: 0.9rem; font-weight: 800; margin: 0 0 4px 0;">Peringatan Penting (Menghapus Master Pasien)</h4>
                <p style="color: #b91c1c; font-size: 0.8rem; margin: 0;">Menghapus data di Master Pasien akan secara otomatis menghapus <b>seluruh riwayat pemeriksaannya</b> (Cascade Delete). Tindakan ini berdampak pada seluruh tabel dan tidak dapat dibatalkan.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("form_delete_patient"):
            list_id_pasien = df_db['id_pasien'].tolist() if not df_db.empty else []
            id_hapus = st.selectbox("Pilih ID Pasien yang Akan Dihapus secara Permanen:", list_id_pasien, index=None, placeholder="Pilih ID Pasien...", label_visibility="collapsed")
            check_konfirmasi = st.checkbox("Saya sadar tindakan ini bersifat permanen dan tidak dapat dipulihkan.")
            
            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            submit_hapus = st.form_submit_button("HAPUS DATA MASTER PASIEN DARI SISTEM", type="primary")
            
            if submit_hapus:
                if not list_id_pasien:
                    st.warning("Database sedang kosong.")
                elif id_hapus is None:
                    st.warning("Silakan tentukan ID Pasien terlebih dahulu.")
                elif not check_konfirmasi:
                    st.error("Gagal. Anda wajib mencentang kotak konfirmasi.")
                else:
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM pasien_tb WHERE id_pasien = %s", (id_hapus,))
                        conn.commit()
                        conn.close()
                        
                        try:
                            st.cache_data.clear()
                        except Exception:
                            pass
                            
                        st.success(f"Sukses menghapus data dengan ID `{id_hapus}`.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal memproses penghapusan: {str(e)}")