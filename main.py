import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import plotly.express as px
import plotly
import plotly.graph_objects as go

# ------------- CONFIG ----------------------------------

st.set_page_config(page_title='Corephoto', page_icon=None, layout="wide")

hide_table_row_index = """
    <style>
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """

st.markdown(hide_table_row_index, unsafe_allow_html=True)

st.sidebar.title("Select Input Files")

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Plotly settings
color_set = px.colors.qualitative.T10

# Required columns
cid = "HOLEID" #
csampid = "GS_SAMPLE_TAG_ID"
cfrom = "SAMPFROM" #
cto = "SAMPTO" #
cproj = "PROJECTCODE"
cstrat = "GS_STRAT_SAMP_D"
cstrand = "GS_STRAND_SAMP_D"
clith = "GS_LITHOLOGY_SAMP_D"
cweath = "GS_RK_WEATH_CLASS_SAMP_D"
cstr = "GS_RK_STR_CLASS_SAMP_D"
cbedang = "Bedding_Angle"
cbeddesc = "Bedding description"
cucs = "GS_UCS_MPA_LAB"
cfmode = "GS_FAILURE_MODE"

# Required columns
cols = [cid, csampid, cfrom, cto, cproj, cstrat, cstrand, clith, cweath, cstr,
    cbedang, cbeddesc, cucs, cfmode]

uploaded_file = st.sidebar.file_uploader("Upload File")

df = pd.DataFrame()
if uploaded_file is not None:
    # Can be used wherever a "file-like" object is accepted:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
        # sheets = ['Sheet1']

# Filter out uneccesary columns
df = df[cols]

# Filter out NaN values from column 'A'
df = df.dropna(subset=[cbedang])

# Filter sidebar
# ------------- FILTER FUNCTIONS ----------------------
def filter_with_all(df, col):
    container = st.sidebar.container()
    all_sel = st.sidebar.checkbox("Select all",
        key=f"{col.replace(' ','')}_all_select")
    myselect = sorted(set(df[df[col].notna()][col]))
    if all_sel:
        selected = container.multiselect(col, (myselect), (myselect))
        if selected: df = df[df[col].isin(selected)]
    else:
        selected = container.multiselect(col, (myselect))
        if selected: df = df[df[col].isin(selected)]
    st.sidebar.write(" ")
    return df

def filter_one_select(df, col):
    myselect = sorted(set(df[df[col].notna()][col]))
    selected = st.sidebar.multiselect(col, (myselect))
    if selected: df = df[df[col].isin(selected)]
    st.sidebar.write(" ")
    return df

if df is not None:
    st.title("UCS Anisotropy")

    # ----------------- Filter ------------------------
    st.sidebar.title('Filters')
    # STRAT
    if any(col.lower().strip()==cstrat.lower().strip() for col in df.columns):
        df = filter_one_select(df, cstrat)
    # STRAND
    if any(col.lower().strip()==cstrand.lower().strip() for col in df.columns):
        df = filter_one_select(df, cstrand)
    # Lith
    if any(col.lower().strip()==clith.lower().strip() for col in df.columns):
        df = filter_with_all(df, clith)
    # Strength
    if any(col.lower().strip()==cstr.lower().strip() for col in df.columns):
        df = filter_with_all(df, cstr)
    # Bedding description
    if any(col.lower().strip()==cbeddesc.lower().strip() for col in df.columns):
        df = filter_with_all(df, cbeddesc)
    # Failure mode
    if any(col.lower().strip()==cfmode.lower().strip() for col in df.columns):
        df = filter_with_all(df, cfmode)

# print(df.head())

col1, col2 = st.columns(2)
with col1:
    lowess_selection = ('Off', 'On')
    lowess_on = st.radio("Trendline", # Lowess Trendline
        lowess_selection, horizontal=True)
if lowess_on != lowess_selection[0]:
    with col2:
        input_frac = st.number_input('Smoothing Level',
            value=0., min_value=0., max_value=1., step=0.1,
            key='Smooth Val')

col_selections = [cstr, cbeddesc, cfmode]
col_sel = st.radio("Select Column", col_selections, horizontal=True)

if lowess_on != lowess_selection[0]:
    fig_line = px.scatter(df, x=cbedang, y=cucs,
        trendline="lowess", trendline_options=dict(frac=input_frac))
    fig_line.data = [t for t in fig_line.data if t.mode == "lines"]
    fig_line.update_traces(line_color='#000000', line_width=5)
    fig_indiv = px.scatter(df, x=cbedang, y=cucs, color=col_sel,
        color_discrete_sequence=color_set,
        trendline="lowess", trendline_options=dict(frac=input_frac),
        hover_name=col_sel, hover_data=[cid, csampid, cproj, cfrom, cucs, cbedang, cbeddesc, cfmode])
    for i in range(int(len(fig_indiv.data)/2)):
        fig_indiv.data[i*2+1].update(line_color=color_set[i], line_width=2)
    fig_indiv.update_traces(marker=dict(size=8))
    fig = go.Figure(data = fig_indiv.data + fig_line.data)

    textsize = 16
    fig.update_layout(
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        height=600,)

    fig.update_xaxes(gridcolor='lightgrey', tickfont=dict(size=textsize),
        zeroline=True, zerolinewidth=3, zerolinecolor='lightgrey',
        tickformat=",.0f")
    fig.update_yaxes(gridcolor='lightgrey', tickfont=dict(size=textsize),
        zeroline=True, zerolinewidth=3, zerolinecolor='lightgrey',
        tickformat=",.0f")
    fig.add_shape(
        type="rect", xref="paper", yref="paper",
        x0=0, y0=0, x1=1.0, y1=1.0,
        line=dict(color="black", width=2))
    fig.update_layout(
        # title_text="Double Y Axis Example",
        xaxis=dict(title_text='<b>Bedding Angle</b>', tickfont=dict(size=textsize)),
        yaxis=dict(title_text=f"<b>UCS (MPa)</b>", tickfont=dict(size=textsize)))

    st.plotly_chart(fig, use_container_width=True)
