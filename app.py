import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.graph_objects as go

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

st.subheader("🎨 Популярність кольорів")
if "Color" in filtered_df.columns:
    color_counts = filtered_df["Color"].value_counts()
    st.bar_chart(color_counts)

st.subheader("🌤️ Сезонні покупки")
if "Season" in filtered_df.columns:
    season_counts = filtered_df["Season"].value_counts()
    fig3, ax3 = plt.subplots()
    ax3.pie(season_counts, labels=season_counts.index, autopct="%1.1f%%", startangle=90)
    ax3.axis("equal")
    st.pyplot(fig3)

# 🔀 Sankey Diagram: Gender → Category → Season
st.subheader("🔀 Потік покупок: Gender → Category → Season")
if all(col in filtered_df.columns for col in ["Gender", "Category", "Season"]):
    sankey_df = filtered_df.groupby(["Gender", "Category", "Season"]).size().reset_index(name="count")

    all_labels = pd.concat([
        sankey_df["Gender"],
        sankey_df["Category"],
        sankey_df["Season"]
    ]).unique().tolist()

    label_to_index = {label: i for i, label in enumerate(all_labels)}

    source = sankey_df["Gender"].map(label_to_index)
    target = sankey_df["Category"].map(label_to_index)
    value = sankey_df["count"]

    source2 = sankey_df["Category"].map(label_to_index)
    target2 = sankey_df["Season"].map(label_to_index)
    value2 = sankey_df["count"]

    fig4 = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_labels
        ),
        link=dict(
            source=source.tolist() + source2.tolist(),
            target=target.tolist() + target2.tolist(),
            value=value.tolist() + value2.tolist()
        )
    )])

    fig4.update_layout(title_text="Sankey Diagram: Gender → Category → Season", font_size=12)
    st.plotly_chart(fig4, use_container_width=True)

# 💸 Discount vs Purchase Amount
st.subheader("💸 Знижка vs Сума покупки")
if "Discount Applied" in filtered_df.columns and "Purchase Amount (USD)" in filtered_df.columns:
    discount_data = filtered_df.groupby("Discount Applied")["Purchase Amount (USD)"].mean().reset_index()
    fig5, ax5 = plt.subplots()
    sns.barplot(data=discount_data, x="Discount Applied", y="Purchase Amount (USD)", palette="viridis", ax=ax5)
    ax5.set_title("Середня сума покупки залежно від знижки")
    st.pyplot(fig5)
