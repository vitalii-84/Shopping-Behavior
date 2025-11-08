import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="🛍️ Shopping Behavior Dashboard", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("shopping_behavior.csv")

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

st.subheader("📍 Вік vs Сума покупки")
if "Purchase Amount" in filtered_df.columns:
    fig3, ax3 = plt.subplots()
    sns.scatterplot(data=filtered_df, x="Age", y="Purchase Amount", hue="Gender", ax=ax3)
    st.pyplot(fig3)
