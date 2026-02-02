import streamlit as st
import pandas as pd
import os
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import time

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="DFT Calculations Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# LOAD CSS
# =====================================================
def load_css():
    with open("assets/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# =====================================================
# TITLE
# =====================================================
st.title("🧪 DFT Calculations Dashboard")
st.markdown(
    '<div class="subtitle">Structured database of Body-Centered Cubic (BCC) alloys</div>',
    unsafe_allow_html=True
)

# =====================================================
# LOAD DATA
# =====================================================
@st.cache_data
def load_data(path, last_modified):
    return pd.read_csv(path)

DATA_FILE = os.path.join("data", "FINAL_DASHBOARD.csv")
df = load_data(DATA_FILE, os.path.getmtime(DATA_FILE))

# =====================================================
# ELEMENT DEFINITIONS
# =====================================================
elements = [
    "W","Mo","Ta","Nb","V","Cr","Fe","Li","K","Rb","Cs","Ba","Ra","Ca","Sr",
    "Rh","Ir","Ni","Pd","Pt","Cu","Ag","Au","Al","Ne","Ar","Kr","Xe",
    "Be","Mg","Sc","Y","Ti","Zr","Hf","Tc","Re","Ru","Os","Co","Zn","Cd","He"
]
present_cols = [f"{el}_present" for el in elements]

# =====================================================
# ALLOY COMPLEXITY FUNCTION (MOVE THIS EARLIER)
# =====================================================
def classify_complexity(row):
    n = int(row[present_cols].fillna(0).sum())
    return ["Pure","Binary","Ternary","Quaternary","Quinary"][n-1] if 1 <= n <= 5 else ">5 elements"

# Create Complexity column for entire dataframe
df["Complexity"] = df.apply(classify_complexity, axis=1)

# Color map for alloy complexity (same as pie chart)
complexity_color_map = {
    "Pure": "#4CAF50",
    "Binary": "#2196F3",
    "Ternary": "#FFC107",
    "Quaternary": "#E4507D",
    "Quinary": "#67B651",
    ">5 elements": "#9C27B0"
}

# =====================================================
# ELASTIC COMPLETION
# =====================================================
elastic_cols = [
    "C_11 [GPa]", "C_12 [GPa]", "C_13 [GPa]", "C_23 [GPa]",
    "C_22 [GPa]", "C_33 [GPa]", "C_44 [GPa]", "C_55 [GPa]", "C_66 [GPa]",
    "G_V [GPa]", "G_R [GPa]", "G [GPa]", "B [GPa]",
    "E_100 [GPa]", "E_110 [GPa]", "E_111 [GPa]",
    "E_113 [GPa]", "E_331 [GPa]", "E_VRH [GPa]",
    "Poisson's ratio []", "Pugh_Ratio"
]

elastic_completed = df[elastic_cols].notna().all(axis=1)
completed_df = df[elastic_completed]
# Also apply complexity to completed_df
completed_df["Complexity"] = completed_df.apply(classify_complexity, axis=1)

# =====================================================
# METRICS (CUSTOM HTML + STREAMLIT NAV)
# =====================================================
st.markdown('<div class="metric-row">', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        f"""
        <div class="metric-card-wrapper">
            <div class="custom-metric">
                <div class="metric-label">🧮 Total calculations</div>
                <div class="metric-value">{len(df)}</div>
            </div>
            <div class="metric-button-container">
        """,
        unsafe_allow_html=True
    )
    st.page_link("pages/01_Total_Calculations.py", label="View details\u00A0\u00A0 →")
    st.markdown("</div></div>", unsafe_allow_html=True)

with c2:
    st.markdown(
        f"""
        <div class="metric-card-wrapper">
            <div class="custom-metric">
                <div class="metric-label">✅  Elastic Tensor & DOS </div>
                <div class="metric-value">{int(elastic_completed.sum())}</div>
            </div>
            <div class="metric-button-container">
        """,
        unsafe_allow_html=True
    )
    st.page_link("pages/02_Completed_Elastic.py", label="View details \u00A0\u00A0 →")
    st.markdown("</div></div>", unsafe_allow_html=True)

with c3:
    st.markdown(
        f"""
        <div class="metric-card-wrapper">
            <div class="custom-metric">
                <div class="metric-label">⚠️ Only DOS</div>
                <div class="metric-value">{int((~elastic_completed).sum())}</div>
            </div>
            <div class="metric-button-container">
        """,
        unsafe_allow_html=True
    )
    st.page_link("pages/03_Missing_Elastic.py", label="View details\u00A0\u00A0  →")
    st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# PLOTS
# =====================================================
col1, col2 = st.columns(2)

# ---------- ELEMENT OCCURRENCE ----------
with col1:
    # Card shell (HTML only — closed immediately)
    st.markdown(
        """
        <div class="chart-card">
            <h3>🧬 Element occurrence</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    total, elastic = {}, {}

    for col in present_cols:
        t = df[col].fillna(0).sum()
        e = completed_df[col].fillna(0).sum()
        if t > 0:
            el = col.replace("_present", "")
            total[el] = int(t)
            elastic[el] = int(e)

    element_df = pd.DataFrame({
        "Element": total.keys(),
        "Total": total.values(),
        "Elastic": elastic.values()
    }).sort_values("Total")

    fig = go.Figure()

    fig.add_bar(
        y=element_df["Element"],
        x=element_df["Total"],
        orientation="h",
        name="Total calculations",
        marker_color="#4273CE",
        # Add hover information
        hovertemplate="<span style='font-size:16px; color:#AAAAAA'><b>%{y}</b></span><br>" +
             "<span style='font-size:14px; color:#AAAAAA'>Total: <span style='color:#AAAAAA'>%{x}</span></span>" +
             "<extra></extra>"
    )

    fig.add_bar(
        y=element_df["Element"],
        x=element_df["Elastic"],
        orientation="h",
        name="Elastic tensor available",
        marker_color="#20BF65",
        # Add hover information
        hovertemplate="<span style='font-size:16px; color:#AAAAAA'><b>%{y}</b></span><br>" +
             "<span style='font-size:14px; color:#AAAAAA'>Total: <span style='color:#AAAAAA'>%{x}</span></span>" +
             "<extra></extra>"
    )

    fig.update_layout(
        barmode="overlay",
        template="plotly_dark",

        # IMPORTANT: transparent so card controls background
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",

        font=dict(size=14),
        xaxis=dict(
            title="Number of calculations",
            title_font=dict(size=16, color="#FFFFFF", weight=700),
            tickfont=dict(size=13),
            showgrid=True,
            gridcolor="#5f5f63",  # Very light vertical grid lines
            gridwidth=1,
            showline=True,  # Show axis line
            linecolor="#5f5f63",  # Axis line color
            linewidth=2,
            range=[-1, 340],
            tickmode="array",  # Use custom tick values
            tickvals=[0, 50, 100, 150, 200, 250, 300, 340],  # Custom tick positions
            ticktext=["0", "50", "100", "150", "200", "250", "300", "340"],
        ),
        yaxis=dict(
            title="Element",
            title_font=dict(size=16, color="#FFFFFF", weight=700),
            tickfont=dict(size=13)
        ),

        legend=dict(
            font=dict(size=16),
            bordercolor="#2a2f3a",
            borderwidth=0.5
        ),
        

        margin=dict(l=80, r=30, t=10, b=40),
        height=480,



        hoverlabel=dict(
            bgcolor="#1a1d29",  # Dark blue-gray background
            bordercolor="#5f5f63",  # Border color matching your axis lines
            font_size=14,
            font_color="white",
            font_family="Arial, sans-serif"
            
        ),
    )

    st.plotly_chart(fig, use_container_width=True)


# ---------- ALLOY COMPLEXITY ----------
with col2:
    st.markdown(
        """
        <div class="chart-card">
            <h3>🧩 Alloy complexity</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    counts = df["Complexity"].value_counts()

    fig = px.pie(
        names=counts.index,
        values=counts.values,
        hole=0.6,
        color=counts.index,
        color_discrete_map=complexity_color_map,
        template="plotly_dark"
    )

    fig.update_traces(
        textinfo="label+value",
        textfont_size=16,  # Increased from 14
        textfont_color="black",  # Added: set text color to white
        marker=dict(line=dict(color="white", width=1.5)),
        # Optional: improve hover text
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent:.1%}<extra></extra>"
    )

    # Update layout - remove legend and adjust fonts
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(
            size=16,  # Increased from 14
            color="Black",
            weight=700 
                # Added: set default font color to white
        ),
        # Remove legend completely
        showlegend=False,  # This is the key change
        # Keep the EXACT same height and margins
        height=480,
        margin=dict(l=40, r=40, t=10, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)



# =====================================================
# NEW ROW FOR PLOTS 3 & 4
# =====================================================
st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)
col3, col4 = st.columns(2)



with col3:
    st.markdown(
        """
        <div class="chart-card">
            <h3>⚖️ Modulus vs Ductility</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------
    # DATA PREPARATION
    # --------------------------------------------------
    plot3_df = completed_df.copy()
    available_complexities = sorted(plot3_df["Complexity"].unique().tolist())
    ALL_TAG = "All"
    
    # Initialize session state for selection and widget key
    if "complexity_state_3" not in st.session_state:
        st.session_state.complexity_state_3 = available_complexities
    
    if "widget_key_3" not in st.session_state:
        st.session_state.widget_key_3 = 1000

    # --------------------------------------------------
    # CALLBACK LOGIC
    # --------------------------------------------------
    def sync_state_3():
        """Handles the logic when user interacts with the multiselect."""
        current_key = f"complexity_filter_multi_3_{st.session_state.widget_key_3}"
        ui_val = st.session_state[current_key]
        
        if ALL_TAG in ui_val:
            # User wants everything: Reset state and rotate key to refresh UI buttons
            st.session_state.complexity_state_3 = available_complexities
            st.session_state.widget_key_3 += 1
        elif not ui_val:
            # User cleared all: Keep it empty to allow selection from dropdown
            st.session_state.complexity_state_3 = []
        else:
            # Normal manual selection
            st.session_state.complexity_state_3 = [c for c in ui_val if c != ALL_TAG]

    # --------------------------------------------------
    # UI COMPONENTS (DROPDOWNS)
    # --------------------------------------------------
    dropdown_col1, dropdown_col2 = st.columns([1, 3])

    with dropdown_col1:
        st.markdown('<div class="dropdown-modulus">', unsafe_allow_html=True)
        modulus_options = {
            "Elastic": "E_VRH [GPa]",
            "Bulk": "B [GPa]",
            "Shear": "G [GPa]"
        }
        selected_modulus = st.selectbox(
            "Select Modulus Type:",
            options=list(modulus_options.keys()),
            key="modulus_selector_plot3_final"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with dropdown_col2:
        st.markdown('<div class="dropdown-complexity">', unsafe_allow_html=True)

        current_selection = st.session_state.complexity_state_3
        remaining = [c for c in available_complexities if c not in current_selection]
        
        # Determine dropdown list: Only show 'All' if 2 or more items are unselected
        if len(remaining) > 1:
            dropdown_options_list = [ALL_TAG] + remaining
        else:
            dropdown_options_list = remaining

        # Use the dynamic key to force a visual refresh when required
        dynamic_key = f"complexity_filter_multi_3_{st.session_state.widget_key_3}"

        st.multiselect(
            "Filter Complexity:",
            options=current_selection + dropdown_options_list,
            default=current_selection,
            key=dynamic_key,
            on_change=sync_state_3
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------
    # FINAL STATE & DATA FILTERING
    # --------------------------------------------------
    # Use the variable name expected by your downstream plotting code
    selected_complexities = [c for c in st.session_state.complexity_state_3 if c != ALL_TAG]

    y_col = modulus_options[selected_modulus]
    filtered_df = plot3_df[plot3_df["Complexity"].isin(selected_complexities)].copy()





    # --------------------------------------------------
    # PLOT
    # --------------------------------------------------
    fig3 = go.Figure()

    for complexity in selected_complexities:
        complexity_df = filtered_df[filtered_df["Complexity"] == complexity]

        if not complexity_df.empty and complexity in complexity_color_map:
            fig3.add_trace(go.Scatter(
                x=1 / complexity_df["Pugh_Ratio"].replace(0, np.nan),
                y=complexity_df[y_col],
                mode="markers",
                name=complexity,
                marker=dict(
                    size=10,
                    color=complexity_color_map[complexity],
                    line=dict(width=1, color="white")
                ),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    f"{selected_modulus.split()[0]}: %{{y:.1f}} GPa<br>"
                    "Pugh Ratio: %{x:.2f}<br>"
                    "Complexity: %{customdata[0]}<extra></extra>"
                ),
                text=complexity_df["Alloy"],
                customdata=complexity_df[["Complexity"]].values
            ))

    # --------------------------------------------------
    # CHART STYLING
    # --------------------------------------------------
    y_title_map = {
        "E_VRH [GPa]": "Elastic Modulus (Strength) [GPa]",
        "B [GPa]": "Bulk Modulus [GPa]",
        "G [GPa]": "Shear Modulus [GPa]"
    }

    fig3.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=14),
        xaxis=dict(
            title="1 / Pugh Ratio (Ductility)",
            title_font=dict(size=16, color="#FFFFFF", weight=700),
            tickfont=dict(size=13),
            showgrid=True,
            gridcolor="#5f5f63",
            gridwidth=1,
            showline=True,
            linecolor="#5f5f63",
            linewidth=2
        ),
        yaxis=dict(
            title=y_title_map[y_col],
            title_font=dict(size=16, color="#FFFFFF", weight=700),
            tickfont=dict(size=13),
            showgrid=True,
            gridcolor="#5f5f63",
            gridwidth=1,
            showline=True,
            linecolor="#5f5f63",
            linewidth=2
        ),
        legend=dict(
            font=dict(size=14),
            title=dict(text="Alloy Complexity", font=dict(size=14, color="#FFFFFF"))
        ),
        margin=dict(l=80, r=30, t=40, b=40),
        height=480
    )

    # --------------------------------------------------
    # SUBTITLE
    # --------------------------------------------------
    subtitle_text = (
        "Active Filters: All"
        if len(selected_complexities) == len(available_complexities)
        else f"Active Filters: {', '.join(selected_complexities)}"
    )

    fig3.add_annotation(
        text=subtitle_text,
        xref="paper",
        yref="paper",
        x=0,
        y=1.08,
        showarrow=False,
        font=dict(size=12, color="#888888")
    )

    st.plotly_chart(fig3, use_container_width=True)

# ---------- PLOT 4: MODULUS VS NEF ----------
with col4:
    st.markdown(
        """
        <div class="chart-card">
            <h3>🔬 Modulus vs Nef (DOS at Fermi Level)</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------
    # DATA PREPARATION
    # --------------------------------------------------
    plot4_df = completed_df.copy()
    available_complexities_4 = sorted(plot4_df["Complexity"].unique().tolist())
    ALL_TAG = "All"

    # Initialize session state for Plot 4
    if "complexity_state_4" not in st.session_state:
        st.session_state.complexity_state_4 = available_complexities_4
    
    if "widget_key_4" not in st.session_state:
        st.session_state.widget_key_4 = 4000  # Unique starting key for Plot 4

    # --------------------------------------------------
    # CALLBACK LOGIC
    # --------------------------------------------------
    def sync_state_4():
        """Handles logic for Plot 4 multiselect."""
        current_key = f"complexity_filter_multi_4_{st.session_state.widget_key_4}"
        ui_val = st.session_state[current_key]
        
        if ALL_TAG in ui_val:
            # Reset to all and rotate key to force buttons to reappear
            st.session_state.complexity_state_4 = available_complexities_4
            st.session_state.widget_key_4 += 1
        elif not ui_val:
            # Allow empty state
            st.session_state.complexity_state_4 = []
        else:
            # Sync selection, filtering out the 'All' tag
            st.session_state.complexity_state_4 = [c for c in ui_val if c != ALL_TAG]

    # --------------------------------------------------
    # DROPDOWNS (25% / 75%)
    # --------------------------------------------------
    dropdown_col1, dropdown_col2 = st.columns([1, 3])

    with dropdown_col1:
        st.markdown('<div class="dropdown-modulus">', unsafe_allow_html=True)
        # Assuming modulus_options dictionary is defined globally as in Plot 3
        selected_modulus_2 = st.selectbox(
            "Select Modulus Type:",
            options=list(modulus_options.keys()),
            index=0,
            key="modulus_selector_plot4_final"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with dropdown_col2:
        st.markdown('<div class="dropdown-complexity">', unsafe_allow_html=True)
        
        current_selection_4 = st.session_state.complexity_state_4
        remaining_4 = [c for c in available_complexities_4 if c not in current_selection_4]

        # Dropdown list logic: Show 'All' if 2 or more are unselected
        if len(remaining_4) > 1:
            dropdown_options_list_4 = [ALL_TAG] + remaining_4
        else:
            dropdown_options_list_4 = remaining_4

        # Dynamic key to force visual refresh
        dynamic_key_4 = f"complexity_filter_multi_4_{st.session_state.widget_key_4}"

        st.multiselect(
            "Filter Complexity:",
            options=current_selection_4 + dropdown_options_list_4,
            default=current_selection_4,
            key=dynamic_key_4,
            on_change=sync_state_4
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------
    # FINAL STATE & DATA FILTERING
    # --------------------------------------------------
    # Extract the actual list for filtering (stripping ALL_TAG if present)
    selected_complexities_4 = [c for c in st.session_state.complexity_state_4 if c != ALL_TAG]

    y_col_2 = modulus_options[selected_modulus_2]
    filtered_df_4 = plot4_df[
        plot4_df["Complexity"].isin(selected_complexities_4)
    ].copy()
    # --------------------------------------------------
    # PLOT
    # --------------------------------------------------
    fig4 = go.Figure()

    for complexity in selected_complexities_4:
        complexity_df = filtered_df_4[
            filtered_df_4["Complexity"] == complexity
        ]

        if not complexity_df.empty and complexity in complexity_color_map:
            fig4.add_trace(go.Scatter(
                x=complexity_df["Nef (states/eV/atom)"],
                y=complexity_df[y_col_2],
                mode="markers",
                name=complexity,
                marker=dict(
                    size=10,
                    color=complexity_color_map[complexity],
                    line=dict(width=1, color="white")
                ),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    f"{selected_modulus_2.split()[0]}: %{{y:.1f}} GPa<br>"
                    "N<sub>ef</sub>: %{x:.2f} states/eV/atom<br>"
                    "Complexity: %{customdata[0]}<extra></extra>"
                ),
                text=complexity_df["Alloy"],
                customdata=complexity_df[["Complexity"]].values
            ))

    # --------------------------------------------------
    # CHART STYLING
    # --------------------------------------------------
    y_title_map_2 = {
        "E_VRH [GPa]": "Elastic Modulus (Strength) [GPa]",
        "B [GPa]": "Bulk Modulus [GPa]",
        "G [GPa]": "Shear Modulus [GPa]"
    }

    fig4.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=14),
        xaxis=dict(
            title="N<sub>ef</sub> (states/eV/atom)",
            title_font=dict(size=16, color="#FFFFFF", weight=700),
            tickfont=dict(size=13),
            showgrid=True,
            gridcolor="#5f5f63",
            gridwidth=1,
            showline=True,
            linecolor="#5f5f63",
            linewidth=2
        ),
        yaxis=dict(
            title=y_title_map_2[y_col_2],
            title_font=dict(size=16, color="#FFFFFF", weight=700),
            tickfont=dict(size=13),
            showgrid=True,
            gridcolor="#5f5f63",
            gridwidth=1,
            showline=True,
            linecolor="#5f5f63",
            linewidth=2
        ),
        legend=dict(
            font=dict(size=14),
           
            title=dict(text="Alloy Complexity", font=dict(size=14, color="#FFFFFF"))
        ),
        margin=dict(l=80, r=30, t=40, b=40),
        height=480
    )

    # --------------------------------------------------
    # SUBTITLE
    # --------------------------------------------------
    subtitle_text_4 = (
        "Active Filters: All"
        if len(selected_complexities_4) == len(available_complexities_4)
        else f"Active Filters: {', '.join(selected_complexities_4)}"
    )

    fig4.add_annotation(
        text=subtitle_text_4,
        xref="paper",
        yref="paper",
        x=0,
        y=1.08,
        showarrow=False,
        font=dict(size=12, color="#888888")
    )

    st.plotly_chart(fig4, use_container_width=True)

























# # ... (your periodic table data and grid creation code remains the same) ...
# # --------- FULL PERIODIC TABLE DATA ---------
# full_periodic_table = [
#     (1, "H", 1.008, 1, 1), (2, "He", 4.0026, 18, 1),
#     (3, "Li", 6.94, 1, 2), (4, "Be", 9.0122, 2, 2), (5, "B", 10.81, 13, 2),
#     (6, "C", 12.011, 14, 2), (7, "N", 14.007, 15, 2), (8, "O", 15.999, 16, 2),
#     (9, "F", 18.998, 17, 2), (10, "Ne", 20.18, 18, 2),
#     (11, "Na", 22.99, 1, 3), (12, "Mg", 24.305, 2, 3), (13, "Al", 26.982, 13, 3),
#     (14, "Si", 28.085, 14, 3), (15, "P", 30.974, 15, 3), (16, "S", 32.06, 16, 3),
#     (17, "Cl", 35.45, 17, 3), (18, "Ar", 39.948, 18, 3),
#     (19, "K", 39.098, 1, 4), (20, "Ca", 40.078, 2, 4),
#     (21, "Sc", 44.956, 3, 4), (22, "Ti", 47.867, 4, 4), (23, "V", 50.942, 5, 4),
#     (24, "Cr", 51.996, 6, 4), (25, "Mn", 54.938, 7, 4), (26, "Fe", 55.845, 8, 4),
#     (27, "Co", 58.933, 9, 4), (28, "Ni", 58.693, 10, 4), (29, "Cu", 63.546, 11, 4),
#     (30, "Zn", 65.38, 12, 4),
#     (31, "Ga", 69.723, 13, 4), (32, "Ge", 72.63, 14, 4), (33, "As", 74.922, 15, 4),
#     (34, "Se", 78.971, 16, 4), (35, "Br", 79.904, 17, 4), (36, "Kr", 83.798, 18, 4),
#     (37, "Rb", 85.468, 1, 5), (38, "Sr", 87.62, 2, 5), (39, "Y", 88.906, 3, 5),
#     (40, "Zr", 91.224, 4, 5), (41, "Nb", 92.906, 5, 5), (42, "Mo", 95.95, 6, 5),
#     (43, "Tc", 98, 7, 5), (44, "Ru", 101.07, 8, 5), (45, "Rh", 102.91, 9, 5),
#     (46, "Pd", 106.42, 10, 5), (47, "Ag", 107.868, 11, 5), (48, "Cd", 112.414, 12, 5),
#     (49, "In", 114.818, 13, 5), (50, "Sn", 118.71, 14, 5), (51, "Sb", 121.76, 15, 5),
#     (52, "Te", 127.6, 16, 5), (53, "I", 126.904, 17, 5), (54, "Xe", 131.293, 18, 5),
#     (55, "Cs", 132.905, 1, 6), (56, "Ba", 137.327, 2, 6), (57, "La", 138.905, 3, 6),
#     (58, "Ce", 140.116, 4, 8), (59, "Pr", 140.908, 5, 8), (60, "Nd", 144.242, 6, 8),
#     (61, "Pm", 145, 7, 8), (62, "Sm", 150.36, 8, 8), (63, "Eu", 151.964, 9, 8),
#     (64, "Gd", 157.25, 10, 8), (65, "Tb", 158.925, 11, 8), (66, "Dy", 162.5, 12, 8),
#     (67, "Ho", 164.93, 13, 8), (68, "Er", 167.259, 14, 8), (69, "Tm", 168.934, 15, 8),
#     (70, "Yb", 173.045, 16, 8), (71, "Lu", 174.967, 17, 8),
#     (72, "Hf", 178.49, 4, 6), (73, "Ta", 180.95, 5, 6), (74, "W", 183.84, 6, 6),
#     (75, "Re", 186.207, 7, 6), (76, "Os", 190.23, 8, 6), (77, "Ir", 192.217, 9, 6),
#     (78, "Pt", 195.084, 10, 6), (79, "Au", 196.967, 11, 6), (80, "Hg", 200.592, 12, 6),
#     (81, "Tl", 204.38, 13, 6), (82, "Pb", 207.2, 14, 6), (83, "Bi", 208.98, 15, 6),
#     (84, "Po", 209, 16, 6), (85, "At", 210, 17, 6), (86, "Rn", 222, 18, 6),
#     (87, "Fr", 223, 1, 7), (88, "Ra", 226, 2, 7), (89, "Ac", 227, 3, 7),
#     (90, "Th", 232.038, 4, 9), (91, "Pa", 231.036, 5, 9), (92, "U", 238.029, 6, 9),
#     (93, "Np", 237, 7, 9), (94, "Pu", 244, 8, 9), (95, "Am", 243, 9, 9),
#     (96, "Cm", 247, 10, 9), (97, "Bk", 247, 11, 9), (98, "Cf", 251, 12, 9),
#     (99, "Es", 252, 13, 9), (100, "Fm", 257, 14, 9), (101, "Md", 258, 15, 9),
#     (102, "No", 259, 16, 9), (103, "Lr", 262, 17, 9),
#     (104, "Rf", 267, 4, 7), (105, "Db", 268, 5, 7), (106, "Sg", 271, 6, 7),
#     (107, "Bh", 272, 7, 7), (108, "Hs", 277, 8, 7), (109, "Mt", 276, 9, 7),
#     (110, "Ds", 281, 10, 7), (111, "Rg", 282, 11, 7), (112, "Cn", 285, 12, 7),
#     (113, "Nh", 286, 13, 7), (114, "Fl", 289, 14, 7), (115, "Mc", 289, 15, 7),
#     (116, "Lv", 293, 16, 7), (117, "Ts", 294, 17, 7), (118, "Og", 294, 18, 7)
# ]

# periodic_df = pd.DataFrame(
#     full_periodic_table,
#     columns=["AtomicNumber", "Symbol", "AtomicMass", "Group", "Period"]
# )

# # ---------------- SESSION STATE ----------------
# if "selected_elements" not in st.session_state:
#     st.session_state.selected_elements = []

# # Create period grid
# period_grid = {}
# for period in range(1, 10):
#     for group in range(1, 19):
#         period_grid[(period, group)] = None

# for _, element in periodic_df.iterrows():
#     period = element["Period"]
#     group = element["Group"]

#     if pd.isna(group):
#         continue

#     group = int(group)
#     if 1 <= group <= 18 and 1 <= period <= 9:
#         period_grid[(period, group)] = element



























# =====================================================
# INTERACTIVE PERIODIC TABLE - FORM APPROACH
# =====================================================

# Initialize session state FIRST
if "selected_elements" not in st.session_state:
    st.session_state.selected_elements = []

if "periodic_last_click" not in st.session_state:
    st.session_state.periodic_last_click = None

st.markdown("<hr style='border:1px solid #444;'>", unsafe_allow_html=True)
st.markdown("<h2 style='color:white;'>🧪 Select Elements to Filter Alloys</h2>", unsafe_allow_html=True)




ELEMENT_CATEGORIES = {
    # Alkali metals
    "Li": "alkali", "Na": "alkali", "K": "alkali", "Rb": "alkali",
    "Cs": "alkali", "Fr": "alkali",

    # Alkaline earth metals
    "Be": "alkaline-earth", "Mg": "alkaline-earth", "Ca": "alkaline-earth",
    "Sr": "alkaline-earth", "Ba": "alkaline-earth", "Ra": "alkaline-earth",

    # Transition metals
    "Sc": "transition", "Ti": "transition", "V": "transition", "Cr": "transition",
    "Mn": "transition", "Fe": "transition", "Co": "transition", "Ni": "transition",
    "Cu": "transition", "Zn": "transition",
    "Y": "transition", "Zr": "transition", "Nb": "transition", "Mo": "transition",
    "Tc": "transition", "Ru": "transition", "Rh": "transition", "Pd": "transition",
    "Ag": "transition", "Cd": "transition",
    "Hf": "transition", "Ta": "transition", "W": "transition", "Re": "transition",
    "Os": "transition", "Ir": "transition", "Pt": "transition", "Au": "transition",
    "Hg": "transition",
    "Rf": "transition", "Db": "transition", "Sg": "transition", "Bh": "transition",
    "Hs": "transition", "Mt": "transition", "Ds": "transition", "Rg": "transition",

    # Post-transition metals
    "Al": "post-transition", "Ga": "post-transition", "In": "post-transition",
    "Sn": "post-transition", "Tl": "post-transition", "Pb": "post-transition",
    "Bi": "post-transition", "Nh": "post-transition", "Fl": "post-transition",
    "Mc": "post-transition", "Lv": "post-transition",

    # Metalloids
    "B": "metalloid", "Si": "metalloid", "Ge": "metalloid",
    "As": "metalloid", "Sb": "metalloid", "Te": "metalloid",

    # Reactive nonmetals
    "H": "nonmetal", "C": "nonmetal", "N": "nonmetal",
    "O": "nonmetal", "P": "nonmetal", "S": "nonmetal",
    "Se": "nonmetal", "F": "nonmetal", "Cl": "nonmetal",
    "Br": "nonmetal", "I": "nonmetal", "At": "nonmetal",

    # Noble gases
    "He": "noble", "Ne": "noble", "Ar": "noble",
    "Kr": "noble", "Xe": "noble", "Rn": "noble", "Og": "noble",

    # Lanthanides
    "La": "lanthanide", "Ce": "lanthanide", "Pr": "lanthanide", "Nd": "lanthanide",
    "Pm": "lanthanide", "Sm": "lanthanide", "Eu": "lanthanide", "Gd": "lanthanide",
    "Tb": "lanthanide", "Dy": "lanthanide", "Ho": "lanthanide", "Er": "lanthanide",
    "Tm": "lanthanide", "Yb": "lanthanide", "Lu": "lanthanide",

    # Actinides
    "Ac": "actinide", "Th": "actinide", "Pa": "actinide", "U": "actinide",
    "Np": "actinide", "Pu": "actinide", "Am": "actinide", "Cm": "actinide",
    "Bk": "actinide", "Cf": "actinide", "Es": "actinide", "Fm": "actinide",
    "Md": "actinide", "No": "actinide", "Lr": "actinide",
}




# --------- FULL PERIODIC TABLE DATA ---------
full_periodic_table = [
    (1, "H", 1.008, 1, 1), (2, "He", 4.0026, 18, 1),
    (3, "Li", 6.94, 1, 2), (4, "Be", 9.0122, 2, 2), (5, "B", 10.81, 13, 2),
    (6, "C", 12.011, 14, 2), (7, "N", 14.007, 15, 2), (8, "O", 15.999, 16, 2),
    (9, "F", 18.998, 17, 2), (10, "Ne", 20.18, 18, 2),
    (11, "Na", 22.99, 1, 3), (12, "Mg", 24.305, 2, 3), (13, "Al", 26.982, 13, 3),
    (14, "Si", 28.085, 14, 3), (15, "P", 30.974, 15, 3), (16, "S", 32.06, 16, 3),
    (17, "Cl", 35.45, 17, 3), (18, "Ar", 39.948, 18, 3),
    (19, "K", 39.098, 1, 4), (20, "Ca", 40.078, 2, 4),
    (21, "Sc", 44.956, 3, 4), (22, "Ti", 47.867, 4, 4), (23, "V", 50.942, 5, 4),
    (24, "Cr", 51.996, 6, 4), (25, "Mn", 54.938, 7, 4), (26, "Fe", 55.845, 8, 4),
    (27, "Co", 58.933, 9, 4), (28, "Ni", 58.693, 10, 4), (29, "Cu", 63.546, 11, 4),
    (30, "Zn", 65.38, 12, 4),
    (31, "Ga", 69.723, 13, 4), (32, "Ge", 72.63, 14, 4), (33, "As", 74.922, 15, 4),
    (34, "Se", 78.971, 16, 4), (35, "Br", 79.904, 17, 4), (36, "Kr", 83.798, 18, 4),
    (37, "Rb", 85.468, 1, 5), (38, "Sr", 87.62, 2, 5), (39, "Y", 88.906, 3, 5),
    (40, "Zr", 91.224, 4, 5), (41, "Nb", 92.906, 5, 5), (42, "Mo", 95.95, 6, 5),
    (43, "Tc", 98, 7, 5), (44, "Ru", 101.07, 8, 5), (45, "Rh", 102.91, 9, 5),
    (46, "Pd", 106.42, 10, 5), (47, "Ag", 107.868, 11, 5), (48, "Cd", 112.414, 12, 5),
    (49, "In", 114.818, 13, 5), (50, "Sn", 118.71, 14, 5), (51, "Sb", 121.76, 15, 5),
    (52, "Te", 127.6, 16, 5), (53, "I", 126.904, 17, 5), (54, "Xe", 131.293, 18, 5),
    (55, "Cs", 132.905, 1, 6), (56, "Ba", 137.327, 2, 6), (57, "La", 138.905, 3, 6),
    (58, "Ce", 140.116, 4, 8), (59, "Pr", 140.908, 5, 8), (60, "Nd", 144.242, 6, 8),
    (61, "Pm", 145, 7, 8), (62, "Sm", 150.36, 8, 8), (63, "Eu", 151.964, 9, 8),
    (64, "Gd", 157.25, 10, 8), (65, "Tb", 158.925, 11, 8), (66, "Dy", 162.5, 12, 8),
    (67, "Ho", 164.93, 13, 8), (68, "Er", 167.259, 14, 8), (69, "Tm", 168.934, 15, 8),
    (70, "Yb", 173.045, 16, 8), (71, "Lu", 174.967, 17, 8),
    (72, "Hf", 178.49, 4, 6), (73, "Ta", 180.95, 5, 6), (74, "W", 183.84, 6, 6),
    (75, "Re", 186.207, 7, 6), (76, "Os", 190.23, 8, 6), (77, "Ir", 192.217, 9, 6),
    (78, "Pt", 195.084, 10, 6), (79, "Au", 196.967, 11, 6), (80, "Hg", 200.592, 12, 6),
    (81, "Tl", 204.38, 13, 6), (82, "Pb", 207.2, 14, 6), (83, "Bi", 208.98, 15, 6),
    (84, "Po", 209, 16, 6), (85, "At", 210, 17, 6), (86, "Rn", 222, 18, 6),
    (87, "Fr", 223, 1, 7), (88, "Ra", 226, 2, 7), (89, "Ac", 227, 3, 7),
    (90, "Th", 232.038, 4, 9), (91, "Pa", 231.036, 5, 9), (92, "U", 238.029, 6, 9),
    (93, "Np", 237, 7, 9), (94, "Pu", 244, 8, 9), (95, "Am", 243, 9, 9),
    (96, "Cm", 247, 10, 9), (97, "Bk", 247, 11, 9), (98, "Cf", 251, 12, 9),
    (99, "Es", 252, 13, 9), (100, "Fm", 257, 14, 9), (101, "Md", 258, 15, 9),
    (102, "No", 259, 16, 9), (103, "Lr", 262, 17, 9),
    (104, "Rf", 267, 4, 7), (105, "Db", 268, 5, 7), (106, "Sg", 271, 6, 7),
    (107, "Bh", 272, 7, 7), (108, "Hs", 277, 8, 7), (109, "Mt", 276, 9, 7),
    (110, "Ds", 281, 10, 7), (111, "Rg", 282, 11, 7), (112, "Cn", 285, 12, 7),
    (113, "Nh", 286, 13, 7), (114, "Fl", 289, 14, 7), (115, "Mc", 289, 15, 7),
    (116, "Lv", 293, 16, 7), (117, "Ts", 294, 17, 7), (118, "Og", 294, 18, 7)
]

periodic_df = pd.DataFrame(
    full_periodic_table,
    columns=["AtomicNumber", "Symbol", "AtomicMass", "Group", "Period"]
)

periodic_df["Category"] = periodic_df["Symbol"].map(ELEMENT_CATEGORIES).fillna("unknown")


# Create period grid
period_grid = {}
for period in range(1, 10):
    for group in range(1, 19):
        period_grid[(period, group)] = None

for _, element in periodic_df.iterrows():
    period = element["Period"]
    group = element["Group"]

    if pd.isna(group):
        continue

    group = int(group)
    if 1 <= group <= 18 and 1 <= period <= 9:
        period_grid[(period, group)] = element

# =====================================================
# PERIODIC TABLE FORM WITH CSS CLASSES
# =====================================================

left_pad, center_col, right_pad = st.columns([15, 70, 15])




# REAL container that actually wraps columns
with center_col:

    # =====================================================
    # PERIODIC TABLE FORM WITH CSS CLASSES
    # =====================================================

    with st.container():
        with st.form(key="periodic_table_form", clear_on_submit=True):

            for period in range(1, 10):
                cols = st.columns(18)
                for group in range(1, 19):
                    with cols[group - 1]:
                        element = period_grid.get((period, group))
                        if element is not None:
                            sym = element["Symbol"]
                            category = element["Category"]   
                            is_selected = sym in st.session_state.selected_elements
                            btn_key = f"pt_btn_{category}_{period}_{group}"

                        

                            if st.form_submit_button(
                                sym,
                                key=btn_key,
                                use_container_width=True,
                                type="primary" if is_selected else "secondary"
                            ):
                                st.session_state.periodic_last_click = sym
                        else:
                            st.markdown('<div class="blank-cell"></div>', unsafe_allow_html=True)


    st.markdown('</div>', unsafe_allow_html=True)
    

# Handle form submission
if st.session_state.periodic_last_click:
    element = st.session_state.periodic_last_click
    if element:
        if element in st.session_state.selected_elements:
            st.session_state.selected_elements.remove(element)
        else:
            st.session_state.selected_elements.append(element)
        st.session_state.periodic_last_click = None
        st.rerun()

# =====================================================
# DISPLAY SELECTED ELEMENTS (STREAMLIT-NATIVE, STYLEABLE)
# =====================================================


outer_left, outer_center, outer_right = st.columns([3, 4, 3])

with outer_center:
    if st.session_state.selected_elements:
        selected_text = ", ".join(st.session_state.selected_elements)
    else:
        selected_text = "<i>None</i>"

    html_content = f"""
    <div class="outer-center">
        <div class="inner-left">Selected Elements</div>
        <div class="inner-right">{selected_text}</div>
    </div>
    """
    
    st.markdown(html_content, unsafe_allow_html=True)




# Clear button
if st.button("Clear All Selections", key="clear_periodic", type="secondary"):
    st.session_state.selected_elements = []
    st.rerun()


# ============================================================
# FILTER ALLOYS (STRICT: MUST CONTAIN ALL SELECTED ELEMENTS)
# ============================================================

st.markdown(
    "<hr style='border:1px solid #444; margin: 40px 0 20px 0;'>",
    unsafe_allow_html=True
)

sel = st.session_state.selected_elements

# Only keep elements that actually have a _present column
valid_sel = [el for el in sel if f"{el}_present" in df.columns]

if valid_sel:
    # Start with full dataframe
    filtered_df = df.copy()

    # ALL selected elements must be present (AND condition)
    for el in valid_sel:
        filtered_df = filtered_df[filtered_df[f"{el}_present"] == 1]
else:
    # No valid selection → no alloys
    filtered_df = pd.DataFrame(columns=df.columns)


# ============================================================
# FILTERED ALLOYS HEADER
# ============================================================
st.markdown(
    f"""
    <div class="filtered-alloys-container">
        <div class="filtered-alloys-title">
            Filtered Alloys:\u00A0\u00A0
            <span class="filtered-alloys-count">{len(filtered_df)} found</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)



# ============================================================
# DETAILED ANALYSIS BUTTON (ONLY WHEN DATA EXISTS)
# ============================================================
# if not filtered_df.empty:
#     st.markdown('<div style="margin-top: 12px;"></div>', unsafe_allow_html=True)
#     if st.button("Detailed Analysis", key="detailed_analysis", type="secondary"):
#         st.switch_page("pages/Alloy_page.py")


# ============================================================
# DATAFRAME OUTPUT
# ============================================================
# ============================================================
# DATAFRAME OUTPUT (STYLED, FIXED LAYOUT, SCROLLABLE)
# ============================================================
# ============================================================
# DATAFRAME OUTPUT (FIXED WIDTH, CORRECT S.NO)
# ============================================================
# ============================================================
# DATAFRAME OUTPUT (FINAL FIXED VERSION)
# ============================================================
# ============================================================
# DATAFRAME OUTPUT (FINAL, NO GHOST COLUMN)
# ============================================================
if filtered_df.empty:
    st.info("No alloys available for selected elements.")
else:
    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)

    # --------------------------------------------------
    # Select required columns (0-based indexing)
    # --------------------------------------------------
    cols_idx = [2, 3, 4, 5, 6, 12, 122, 123, 129, 130, 131]
    display_df = filtered_df.iloc[:, cols_idx].copy()


       # --------------------------------------------------
    # RESET INDEX (CRITICAL to kill ghost column)
    # --------------------------------------------------
    display_df = display_df.reset_index(drop=True)

    # --------------------------------------------------
    # Insert S. No. column
    # --------------------------------------------------
    display_df.insert(0, "S. No.", range(1, len(display_df) + 1))

 

    # --------------------------------------------------
    # HARD-CODE COLUMN TITLES (edit freely later)
    # --------------------------------------------------
    display_df.columns = [
        "S. No.",
        "Alloy",
        "Atom Count",
        "Structure (Ovito)",
        "POTCAR_used",
        "Lattice parameter",
        "Nef_DOS (eV)",
        "Bulk Modulus (GPa)",
        "Shear Modulus (GPa)",
        "Elastic Modulus (GPa)",
        "Poisson Ratio",
        "Pugh ratio (G/B)",
    ]


# --------------------------------------------------
# FORMAT NUMERIC COLUMNS (max 3 decimals, no trailing zeros)
# --------------------------------------------------
    def format_number(x):
        if isinstance(x, (int, float)):
            # format to 3 decimals, then strip trailing zeros and dot
            return f"{x:.3f}".rstrip("0").rstrip(".")
        return x

    numeric_cols = display_df.select_dtypes(include=["number"]).columns
    display_df[numeric_cols] = display_df[numeric_cols].applymap(format_number)






    # --------------------------------------------------
    # COLUMN WIDTHS (1-to-1 with columns above)
    # --------------------------------------------------
    column_widths = [
        "90px",    # S. No.
        "140px",   # Alloy
        "120px",   # Atom Count
        "110px",   # Structure (Ovito)
        "320px",   # POTCAR_used (wide)
        "130px",   # Crystal System
        "120px",   # Nef_DOS
        "150px",   # Bulk
        "150px",   # Shear
        "150px",   # Elastic
        "140px",   # Poisson
        "140px",   # Pugh ratio
    ]

    # --------------------------------------------------
    # Pandas Styler
    # --------------------------------------------------
    styled_df = (
        display_df.style
        .hide(axis="index")  # <-- KILLS GHOST COLUMN
        .set_table_styles(
            [
                {
                    "selector": "table",
                    "props": [
                        ("width", "100%"),
                        ("table-layout", "fixed"),
                        ("border-collapse", "collapse"),
                    ],
                },
                {
                    "selector": "th",
                    "props": [
                        ("background", "linear-gradient(145deg, #232735, #4c3a3a)"),
                        ("color", "white"),
                        ("font-size", "15px"),
                        ("font-weight", "700"),
                        ("text-align", "center"),
                        ("padding", "10px"),
                        ("border-bottom", "1px solid #4273CE"),
                        ("white-space", "normal"),
                        ("word-break", "break-word"),
                        ("position", "sticky"),
                        ("top", "0"),
                        ("z-index", "2"),
                    ],
                },
                {
                    "selector": "td",
                    "props": [
                        ("background-color", "#1f2430"),
                        ("color", "#e5e7eb"),
                        ("font-size", "14px"),
                        ("text-align", "center"),
                        ("font-family", "Inter, Arial, sans-serif"), 
                        ("padding", "8px"),
                        ("border-bottom", "1px solid rgba(255,255,255,0.08)"),
                        ("white-space", "normal"),
                        ("word-break", "break-word"),
                    ],
                },
                {
                    "selector": "tr:nth-child(even) td",
                    "props": [("background-color", "#252a38")],
                },
                {
                    "selector": "tr:hover td",
                    "props": [("background-color", "rgba(66,115,206,0.25)")],
                },
            ]
            +
            # -------- APPLY COLUMN WIDTHS --------
            [
                {
                    "selector": f"th:nth-child({i+1}), td:nth-child({i+1})",
                    "props": [("width", w)],
                }
                for i, w in enumerate(column_widths)
            ]
        )     
    )
    

    # --------------------------------------------------
    # Scroll container (vertical only)
    # --------------------------------------------------


    components.html(
        f"""
        <div style="
            max-height: 500px;
            overflow-y: auto;
            overflow-x: hidden;
            width: 100%;
            border-radius: 40px;
            margin-top: 20px;
        ">
            {styled_df.to_html()}
        </div>
        """,
        height=520,
        scrolling=False,
    )
