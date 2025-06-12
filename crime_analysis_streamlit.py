# crime_analysis_streamlit.py
import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")

# Load data
df = pd.read_csv("crime.csv")
df = df.dropna(subset=["Latitude", "Longitude"])

# Convert date for weekday use if necessary
if 'WEEKDAY' not in df.columns:
    if 'YEAR' in df.columns and 'MONTH' in df.columns and 'DAY' in df.columns:
        df['DATE_COMBINED'] = pd.to_datetime(df[['YEAR', 'MONTH', 'DAY']])
        df['WEEKDAY'] = df['DATE_COMBINED'].dt.dayofweek

# Sidebar - Multi-select for years and crime types
years = sorted(df['YEAR'].dropna().unique())
types = sorted(df['TYPE'].dropna().unique())

selected_years = st.sidebar.multiselect("Select Year(s)", years)
selected_types = st.sidebar.multiselect("Select Crime Type(s)", types)

# Header
st.title("Vancouver Crime Pattern Analysis (2003-2016)")
st.markdown("---")

# Section 1: Data Overview
st.header("1. Data Overview")
st.write(df.head())
st.markdown("---")

# Section 2: Crime Type by Year Heatmap
st.header("2. Crime Type Yearly Distribution")

# 构建透视表
pivot_table = df.pivot_table(index='TYPE', columns='YEAR', values='HOUR', aggfunc='count').fillna(0)

# 绘图
fig, ax = plt.subplots(figsize=(16, 8))
sns.heatmap(pivot_table, cmap='Blues', annot=True, fmt=".0f", linewidths=.5, cbar_kws={'label': 'Crime Count'})
ax.set_title("Crime Type by Year (2003–2016)")
ax.set_xlabel("Year")
ax.set_ylabel("Crime Type")
st.pyplot(fig)
st.markdown("---")

# Section 3: Crime Time and Type Distribution
filtered_df = df[df['YEAR'].isin(selected_years)]
st.header("3. Crime Time and Type Distributions")
fig, ax = plt.subplots(2, 2, figsize=(18, 10))

# Monthly distribution (line plot)
monthly_counts = filtered_df['MONTH'].value_counts().sort_index()
ax[0, 0].plot(monthly_counts.index, monthly_counts.values, marker='o')
ax[0, 0].set_title("Monthly Crime Trend")
ax[0, 0].set_xlabel("Month")
ax[0, 0].set_ylabel("Count")

# Hour of day (line plot)
hourly_counts = filtered_df['HOUR'].value_counts().sort_index()
ax[0, 1].plot(hourly_counts.index, hourly_counts.values, marker='o', color='orange')
ax[0, 1].set_title("Hourly Crime Distribution")
ax[0, 1].set_xlabel("Hour")
ax[0, 1].set_ylabel("Count")

# Day of week (bar chart)
day_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
filtered_df['WEEKDAY_NAME'] = filtered_df['WEEKDAY'].map(day_map)
weekday_counts = filtered_df['WEEKDAY_NAME'].value_counts().reindex(['Mon','Tue','Wed','Thu','Fri','Sat','Sun'])
ax[1, 0].plot(weekday_counts.index, weekday_counts.values, color='green')
ax[1, 0].set_title("Day of Week Distribution")
ax[1, 0].set_xlabel("Day")
ax[1, 0].set_ylabel("Count")

# Top 10 crime types (horizontal bar)
top_types = filtered_df['TYPE'].value_counts().nlargest(10)
ax[1, 1].barh(top_types.index[::-1], top_types.values[::-1], color='steelblue')
ax[1, 1].set_title("Top 10 Crime Types")
ax[1, 1].set_xlabel("Count")

plt.tight_layout()
st.pyplot(fig)
st.markdown("---")

# Section 4: Crime Heatmap using Folium
st.header("4. Crime Density Heatmap (Folium)")
if selected_types:
    filtered_df = filtered_df[filtered_df['TYPE'].isin(selected_types)]

heat_data = [[row['Latitude'], row['Longitude']] for _, row in filtered_df.iterrows()]

m = folium.Map(location=[49.26, -123.12], zoom_start=12)
HeatMap(heat_data, radius=8, blur=5).add_to(m)
st_folium(m, width=1000, height=500)
st.markdown("---")

