import streamlit as st
import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
import joblib

FEATURE_COLUMNS = [
    'Usia', 'Berat_Badan', 'Tinggi_Badan', 'Hb_Darah', 'IMT', 'LILA',
    'Pendapatan_Bulanan', 'Akses_Air_Bersih', 'Akses_Layanan_Kesehatan', 
    'Pendidikan_Terakhir', 'Skor_Pengetahuan_Gizi'
]

def init_ai_and_database():
    FEATURE_COLUMNS = [
        'Usia', 'Berat_Badan', 'Tinggi_Badan', 'Hb_Darah', 'IMT', 'LILA',
        'Pendapatan_Bulanan', 'Akses_Air_Bersih', 'Akses_Layanan_Kesehatan', 
        'Pendidikan_Terakhir', 'Skor_Pengetahuan_Gizi'
    ]
    
    # 1. OTOMATIS LOAD DATASET DARI HARDISK AGAR PERMANEN
    if 'training_data' not in st.session_state:
        file_path = 'dataset_digimind_420.csv'
        if os.path.exists(file_path):
            # Jika file CSV fisik ada di folder, langsung muat ke memori
            st.session_state['training_data'] = pd.read_csv(file_path)
        else:
            # Jika belum ada file, buat template kosong
            st.session_state['training_data'] = pd.DataFrame(columns=FEATURE_COLUMNS + ['Target_Risiko'])

    # 2. OTOMATIS LOAD MODEL AI (.PKL) JIKA SUDAH PERNAH RETRAIN
    if 'ai_model' not in st.session_state:
        model_path = 'model_digimind.pkl'
        if os.path.exists(model_path):
            # Jika otak AI fisik sudah ada, langsung muat tanpa perlu klik retrain lagi
            st.session_state['ai_model'] = joblib.load(model_path)

    # 3. Inisialisasi Database Pasien
    if 'patient_database' not in st.session_state:
        columns_db = ['ID_Pasien', 'Nama', 'Alamat_Kecamatan', 'Status_Pemeriksaan', 'Hasil_Risiko', 'Rekomendasi'] + FEATURE_COLUMNS
        st.session_state['patient_database'] = pd.DataFrame(columns=columns_db)

def train_model():
    df = st.session_state['training_data']
    if df.empty:
        st.error("Dataset latih kosong! Silakan upload file CSV terlebih dahulu di halaman Admin.")
        return

    X = df[FEATURE_COLUMNS]
    y = df['Target_Risiko'].astype(int)
    
    n_estimators = st.session_state.get('model_n_estimators', 100)
    max_depth = st.session_state.get('model_max_depth', None)
    
    try:
        # MENYELARASKAN KELAS SECARA OTOMATIS DENGAN SMOTE (UNTUK 3 LABEL)
        # Menghilangkan ketidakseimbangan kelas langsung sebelum masuk ke Random Forest
        smote = SMOTE(random_state=42, k_neighbors=2)
        X_resampled, y_resampled = smote.fit_resample(X, y)
    except Exception as e:
        # Jika data terlalu sedikit untuk disampling, gunakan data asli sebagai cadangan
        X_resampled, y_resampled = X, y
    
    # Inisialisasi Model Random Forest
    model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
    model.fit(X_resampled, y_resampled)
    
    # MENGEKSPOR OTAK AI MENJADI FILE FISIK .PKL
    # Model ini akan tersimpan permanen di folder proyek Anda
    joblib.dump(model, 'model_digimind.pkl')
    
    # Simpan juga di session state untuk kebutuhan real-time
    st.session_state['ai_model'] = model