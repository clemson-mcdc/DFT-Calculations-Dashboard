import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Completed Elastic",
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

# =====================================================
# NUCLEAR CSS OVERRIDE FOR BUTTONS - ADD THIS SECTION
# =====================================================


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
st.markdown('<h2 class="custom-title">✅ Elastic Tensor & DOS Available</h2>', unsafe_allow_html=True)

# =====================================================
# BACK BUTTON
# =====================================================
# =====================================================
# DATA LOADING AND FILTERING
# =====================================================
DATA_FILE = os.path.join("data", "FINAL_DASHBOARD.csv")
df = pd.read_csv(DATA_FILE)

# Filter for completed elastic calculations
elastic_cols = [
    "C_11 [GPa]", "C_12 [GPa]", "C_13 [GPa]", "C_23 [GPa]",
    "C_22 [GPa]", "C_33 [GPa]", "C_44 [GPa]", "C_55 [GPa]", "C_66 [GPa]",
    "G_V [GPa]", "G_R [GPa]", "G [GPa]", "B [GPa]",
    "E_100 [GPa]", "E_110 [GPa]", "E_111 [GPa]",
    "E_113 [GPa]", "E_331 [GPa]", "E_VRH [GPa]",
    "Poisson's ratio []", "Pugh_Ratio"
]

# Check which rows have all elastic columns filled
completed_mask = df[elastic_cols].notna().all(axis=1)
filtered_data = df[completed_mask]
csv_data = df.to_csv(index=False).encode('utf-8')

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
        file_name="Elastic_tensor_Dos.csv",
        mime="text/csv",
        key="download_csv"
    )


# =====================================================
# DATA DISPLAY
# =====================================================
st.dataframe(
    filtered_data,
    use_container_width=True,
    hide_index=True
)

# End detail page container
st.markdown('</div>', unsafe_allow_html=True)