import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Total Calculations",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def load_css():
    """Load CSS styles for the detail page"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(current_dir, "..", "assets", "detail_styles.css")
    css_path = os.path.normpath(css_path)
    
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Start detail page container
st.markdown('<div class="detail-page">', unsafe_allow_html=True)

# =====================================================
# DASHBOARD TITLE AND SUBTITLE
# =====================================================
st.markdown('<h1 class="dashboard-title">🧪 DFT Calculations Dashboard</h1>', unsafe_allow_html=True)
st.markdown(
    '<div class="dashboard-subtitle">Structured database of Body-Centered Cubic (BCC) alloys</div>',
    unsafe_allow_html=True
)

# =====================================================
# PAGE SPECIFIC TITLE
# =====================================================
st.markdown('<h2 class="custom-title">🧮 Total Calculations</h2>', unsafe_allow_html=True)

# =====================================================
# LOAD DATA
# =====================================================
DATA_FILE = os.path.join("data", "FINAL_DASHBOARD.csv")
df = pd.read_csv(DATA_FILE)
csv_data = df.to_csv(index=False).encode('utf-8')

# =====================================================
# BUTTONS
# =====================================================
col1, col2 = st.columns(2)

with col1:
    # Back to Dashboard button (will be blue)
    if st.button("← Back to Dashboard", key="back_button"):
        st.switch_page("app.py")

with col2:
    # Download CSV button (will be green via CSS override)
    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name="total_calculations.csv",
        mime="text/csv",
        key="download_csv"
    )

# =====================================================
# DATA DISPLAY
# =====================================================
st.dataframe(
    df,
    use_container_width=True,
)

# End detail page container
st.markdown('</div>', unsafe_allow_html=True)