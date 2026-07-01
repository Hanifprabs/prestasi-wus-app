import streamlit as st

def render_login():
    left_spacer, center_column, right_spacer = st.columns([1, 2, 1])
    with center_column:
        st.markdown("<h1 style='text-align: center;'>Prediksi Risiko Stunting</h1>", unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("<h3 style='text-align: center;'>👤 Login ke Sistem</h3>", unsafe_allow_html=True)
            username = st.text_input("Email / Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("LOGIN", use_container_width=True)
            
            if submit:
                # Ganti dengan logika database Anda nanti
                if username == "admin" and password == "123":
                    st.session_state['logged_in'] = True
                    st.rerun()
                else:
                    st.error("Username atau password salah")