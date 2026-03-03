import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import numpy as np
import os

st.set_page_config(
    page_title="Player Journey & Persona Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎮 Player Journey & Persona Analytics")
st.markdown("50,000 players • Funnel + Cohorts + Clustering")

# DATA LOADING & CACHING

@st.cache_resource
def get_duckdb_connection():
    con = duckdb.connect(':memory:')
    
    csv_path = "../data/raw/player_journey_50k.csv"
    
    if not os.path.exists(csv_path):
        st.error(f"CSV file not found: {csv_path}\nRun Phase 1 notebook first.")
        st.stop()
    
    con.execute(f"""
        CREATE OR REPLACE TABLE players AS
        SELECT * FROM read_csv_auto('{csv_path}',
                                    types={{'install_date': 'TIMESTAMP'}})
    """)
    
    return con

@st.cache_data
def load_players(_con):
    return _con.sql("SELECT * FROM players").df()

con = get_duckdb_connection()
df = load_players(con)

# SIDEBAR CONTROLS

with st.sidebar:
    st.header("Dashboard Controls")
    
    # use REAL min/max from data
    min_date = df['install_date'].min().date()
    max_date = df['install_date'].max().date()
    
    # full range
    date_range = st.date_input(
        "Install date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Your data only covers 2023-01-01 to 2023-02-04"
    )
    
    if len(date_range) == 2:
        start, end = [pd.to_datetime(d) for d in date_range]
        df_f = df[(df['install_date'] >= start) & (df['install_date'] <= end)]
    else:
        df_f = df.copy()
    
    # Clustering control
    k_clusters = st.slider("Number of player clusters", 3, 8, 5, key="k_slider")
    
# TABS
tab_funnel, tab_cohort, tab_personas = st.tabs(["📊 Funnel", "📈 Cohorts", "🧑‍🤝‍🧑 Personas"])

#  TAB 1: FUNNEL 

with tab_funnel:
    st.subheader("Player Journey Funnel")
    
    stages = [
        ('Install', len(df_f)),
        ('Registered', df_f['registered'].sum()),
        ('Tutorial Completed', df_f['tutorial_completed'].sum()),
        ('First Game Played', df_f['first_game_played'].sum()),
        ('First Purchase', df_f['first_purchase'].sum()),
        ('D1 Return', df_f['d1_return'].sum()),
        ('D7 Return', df_f['d7_return'].sum()),
        ('D30 Return', df_f['d30_return'].sum())
    ]
    
    funnel_df = pd.DataFrame(stages, columns=['Stage', 'Players'])
    funnel_df['Conversion %'] = (funnel_df['Players'] / len(df_f) * 100).round(1)
    funnel_df['Drop-off %'] = 100 - funnel_df['Conversion %'].shift(-1).fillna(0)
    
    fig_funnel = go.Figure(go.Funnel(
        y=funnel_df['Stage'],
        x=funnel_df['Players'],
        texttemplate="%{x:,}<br>%{customdata:.1f}%",
        customdata=funnel_df['Conversion %'],
        textposition="inside",
        marker={"color": px.colors.sequential.Blues_r}
    ))
    
    fig_funnel.update_layout(title="Player Journey Funnel", height=650, margin={"l": 180, "r": 50})
    st.plotly_chart(fig_funnel, use_container_width=True)
    
    st.dataframe(
        funnel_df.style.format({
            'Players': '{:,}',
            'Conversion %': '{:.1f}%',
            'Drop-off %': '{:.1f}%'
        }),
        use_container_width=True
    )

# TAB 2: COHORTS 

with tab_cohort:
    st.subheader("Retention Cohorts")
    
    cohort_table = df_f.groupby(df_f['install_date'].dt.to_period('M').astype(str)).agg({
        'd1_return': 'mean',
        'd7_return': 'mean',
        'd30_return': 'mean'
    }).reset_index()
    
    cohort_table.columns = ['cohort_month', 'D1 %', 'D7 %', 'D30 %']
    cohort_table[['D1 %', 'D7 %', 'D30 %']] *= 100
    cohort_table[['D1 %', 'D7 %', 'D30 %']] = cohort_table[['D1 %', 'D7 %', 'D30 %']].round(1)
    
    # Heatmap – D7
    pivot_d7 = cohort_table.pivot_table(index='cohort_month', values='D7 %').sort_index(ascending=False)
    fig_heat, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivot_d7, annot=True, fmt='.1f', cmap='YlGnBu', ax=ax)
    ax.set_title("D7 Retention by Cohort Month")
    st.pyplot(fig_heat)
    
    # Curves
    melt = cohort_table.melt(id_vars='cohort_month', var_name='Day', value_name='Retention %')
    fig_curves = px.line(
        melt,
        x='cohort_month',
        y='Retention %',
        color='Day',
        markers=True,
        title="Retention by Install Cohort Month"
    )
    fig_curves.update_layout(height=500)
    st.plotly_chart(fig_curves, use_container_width=True)

# TAB 3: PERSONAS 

with tab_personas:
    st.subheader("Player Personas (Clustering)")
    
    features = [
        'registered', 'tutorial_completed', 'first_game_played',
        'first_purchase', 'd1_return', 'd7_return', 'd30_return',
        'total_revenue', 'avg_session_length_min', 'total_sessions'
    ]
    
    X = df_f[features].fillna(0)
    X_scaled = StandardScaler().fit_transform(X)
    
    kmeans = KMeans(n_clusters=k_clusters, random_state=42, n_init=10)
    df_f['cluster'] = kmeans.fit_predict(X_scaled)
    
    profile = df_f.groupby('cluster')[features].mean().round(2)
    profile['Players'] = df_f.groupby('cluster').size()
    profile['Total Revenue'] = df_f.groupby('cluster')['total_revenue'].sum().round(0)
    
    st.dataframe(profile.style.format({
        'Players': '{:,}',
        'Total Revenue': '{:,.0f}'
    }))
    
    radar_cols = ['registered', 'tutorial_completed', 'first_game_played',
                  'first_purchase', 'd1_return', 'd7_return', 'd30_return',
                  'avg_session_length_min']
    radar_norm = (profile[radar_cols] - profile[radar_cols].min()) / \
                 (profile[radar_cols].max() - profile[radar_cols].min())
    radar_norm['cluster'] = profile.index
    
    fig_radar = go.Figure()
    for _, row in radar_norm.iterrows():
        fig_radar.add_trace(go.Scatterpolar(
            r=row[radar_cols],
            theta=radar_cols,
            fill='toself',
            name=f"Cluster {int(row['cluster'])} (n={profile.loc[row['cluster'], 'Players']:,})"
        ))
    
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,1])),
        showlegend=True,
        title="Player Personas – Radar Comparison",
        height=600
    )
    st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("---")
st.caption("Built by Aklilu Abera • Player Journey & Persona Dashboard")
