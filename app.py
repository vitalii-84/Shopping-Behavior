import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.set_page_config(page_title="🛍️ Shopping Behavior Dashboard", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("shopping_behavior_csv.csv")

df = load_data()

st.title("🛍️ Shopping Behavior Dashboard")

# Sidebar filters
st.sidebar.header("🔍 Фільтри")
gender = st.sidebar.multiselect("Стать", options=df["Gender"].unique(), default=df["Gender"].unique())
age_range = st.sidebar.slider("Вік", int(df["Age"].min()), int(df["Age"].max()), (25, 45))

filtered_df = df[df["Gender"].isin(gender)]
filtered_df = filtered_df[(filtered_df["Age"] >= age_range[0]) & (filtered_df["Age"] <= age_range[1])]

# Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("🛒 Покупки по категоріях")
    if "Category" in filtered_df.columns:
        category_counts = filtered_df["Category"].value_counts()
        st.bar_chart(category_counts)

with col2:
    st.subheader("👥 Розподіл статі")
    gender_counts = filtered_df["Gender"].value_counts()
    fig1, ax1 = plt.subplots()
    ax1.pie(gender_counts, labels=gender_counts.index, autopct="%1.1f%%", startangle=90)
    ax1.axis("equal")
    st.pyplot(fig1)

st.subheader("📊 Кореляція між числовими змінними")
numeric_cols = filtered_df.select_dtypes(include="number")
if not numeric_cols.empty:
    fig2, ax2 = plt.subplots()
    sns.heatmap(numeric_cols.corr(), annot=True, cmap="coolwarm", ax=ax2)
    st.pyplot(fig2)

# 🎨 Color distribution
st.subheader("🎨 Популярність кольорів")
if "Color" in filtered_df.columns:
    color_counts = filtered_df["Color"].value_counts()
    st.bar_chart(color_counts)

# 🌤️ Season distribution
st.subheader("🌤️ Сезонні покупки")
if "Season" in filtered_df.columns:
    season_counts = filtered_df["Season"].value_counts()
    fig3, ax3 = plt.subplots()
    ax3.pie(season_counts, labels=season_counts.index, autopct="%1.1f%%", startangle=90)
    ax3.axis("equal")
    st.pyplot(fig3)

# 🧭 Radar Chart: середня сума покупки по категоріях для кожної статі
st.subheader("🧭 Порівняння покупок по категоріях (Radar Chart)")
if "Purchase Amount (USD)" in filtered_df.columns and "Category" in filtered_df.columns:
    radar_data = filtered_df.groupby(["Gender", "Category"])["Purchase Amount (USD)"].mean().unstack(fill_value=0)
    categories = radar_data.columns.tolist()
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]

    fig4, ax4 = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    for gender in radar_data.index:
        values = radar_data.loc[gender].tolist()
        values += values[:1]
        ax4.plot(angles, values, label=gender)
        ax4.fill(angles, values, alpha=0.1)

    ax4.set_xticks(angles[:-1])
    ax4.set_xticklabels(categories)
    ax4.set_title("Середня сума покупки по категоріях")
    ax4.legend(loc="upper right")
    st.pyplot(fig4)
