import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# --- Setup ---
st.set_page_config(page_title="CA Housing Dashboard", layout="wide")
COLOR = "#2E75B6"
sns.set_theme(style="whitegrid")

st.title("🏠 California Housing Prices — RQ2 Dashboard")
st.markdown("**Research Question:** Does household income, population density, and housing age influence median house values?")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("housing.csv")
    df['total_bedrooms'] = df['total_bedrooms'].fillna(df['total_bedrooms'].median())
    df['rooms_per_household'] = df['total_rooms'] / df['households']
    df['population_density'] = df['population'] / df['households']
    df['age_group'] = pd.cut(df['housing_median_age'],
                              bins=[0, 10, 20, 30, 40, 52],
                              labels=['0-10', '11-20', '21-30', '31-40', '41-52'])
    df['income_tier'] = pd.cut(df['median_income'],
                                bins=[0, 2.5, 4.5, 6.5, 15],
                                labels=['Low', 'Middle', 'Upper-Middle', 'High'])
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("Filters")

ocean_options = df['ocean_proximity'].unique().tolist()
selected_ocean = st.sidebar.multiselect("Ocean Proximity", ocean_options, default=ocean_options)

income_range = st.sidebar.slider("Median Income Range",
                                  float(df['median_income'].min()),
                                  float(df['median_income'].max()),
                                  (1.0, 10.0))

age_options = ['0-10', '11-20', '21-30', '31-40', '41-52']
selected_ages = st.sidebar.multiselect("Housing Age Group", age_options, default=age_options)

# --- Filter Data ---
filtered = df[
    (df['ocean_proximity'].isin(selected_ocean)) &
    (df['median_income'] >= income_range[0]) &
    (df['median_income'] <= income_range[1]) &
    (df['age_group'].isin(selected_ages))
]

st.sidebar.markdown(f"**{len(filtered):,} districts** match filters")

# --- Row 1: KPI Metrics ---
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg House Value", f"${filtered['median_house_value'].mean():,.0f}")
col2.metric("Avg Median Income", f"${filtered['median_income'].mean():,.2f}k")
col3.metric("Avg Housing Age", f"{filtered['housing_median_age'].mean():.1f} yrs")
col4.metric("Avg Population Density", f"{filtered['population_density'].mean():.1f}")

st.markdown("---")

# --- Row 2: Charts ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Income vs. House Value")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(filtered['median_income'], filtered['median_house_value'],
               alpha=0.2, color=COLOR, s=8)
    ax.set_xlabel("Median Income (tens of thousands $)")
    ax.set_ylabel("Median House Value ($)")
    st.pyplot(fig)
    plt.close()

with col2:
    st.subheader("Avg House Value by Age Group")
    avg_age = filtered.groupby('age_group', observed=True)['median_house_value'].mean()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(avg_age.index, avg_age.values, color=COLOR, edgecolor='white')
    ax.set_xlabel("Housing Age Group (years)")
    ax.set_ylabel("Avg House Value ($)")
    st.pyplot(fig)
    plt.close()

st.markdown("---")

# --- Row 3: Map ---
st.subheader("Geographic Distribution of House Values")
fig = px.scatter(filtered, x='longitude', y='latitude',
                 color='median_house_value',
                 color_continuous_scale='YlOrRd',
                 opacity=0.4, size_max=5,
                 labels={'median_house_value': 'House Value ($)'},
                 height=450)
st.plotly_chart(fig, use_container_width=True)