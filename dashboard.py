import streamlit as st
import pandas as pd
import plotly.express as px

def render_dashboard():
    # Sidebar Navigasi
    with st.sidebar:
        st.markdown("### 👤 Prediksi Risiko Stunting")
        st.divider()
        st.button("📊 Dashboard", use_container_width=True, type="primary")
        st.button("📝 Input Risiko WUS", use_container_width=True)
        # Tombol Logout
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state['logged_in'] = False
            st.rerun()

    # Konten Utama
    st.title("DASHBOARD")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Data WUS", "120")
    col2.metric("Total Prediksi", "95")
    col3.metric("Total Rendah", "63")
    
    # Grafik
    df = pd.DataFrame({'Kategori': ['Tinggi', 'Sedang', 'Rendah'], 'Nilai': [20, 50, 30]})
    fig = px.bar(df, x='Kategori', y='Nilai', color_discrete_sequence=['#A0A0A0'])
    st.plotly_chart(fig, use_container_width=True)