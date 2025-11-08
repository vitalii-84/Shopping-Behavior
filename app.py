import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

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

# 🛒 Покупки по категоріях
st.subheader("🛒 Покупки по категоріях")
if "Category" in filtered_df.columns:
    category_counts = filtered_df["Category"].value_counts()
    st.bar_chart(category_counts)

# 👥 Розподіл статі
st.subheader("👥 Розподіл статі")
gender_counts = filtered_df["Gender"].value_counts()
fig1, ax1 = plt.subplots()
ax1.pie(gender_counts, labels=gender_counts.index, autopct="%1.1f%%", startangle=90)
ax1.axis("equal")
st.pyplot(fig1)

# 📊 Кореляція між числовими змінними
st.subheader("📊 Кореляція між числовими змінними")
numeric_cols = filtered_df.select_dtypes(include="number")
if not numeric_cols.empty:
    fig2, ax2 = plt.subplots()
    sns.heatmap(numeric_cols.corr(), annot=True, cmap="coolwarm", ax=ax2)
    st.pyplot(fig2)

# 🎨 Популярність кольорів
st.subheader("🎨 Популярність кольорів")
if "Color" in filtered_df.columns:
    color_counts = filtered_df["Color"].value_counts()
    st.bar_chart(color_counts)

# 🌤️ Сезонні покупки
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
    all_labels = pd.concat([sankey_df["Gender"], sankey_df["Category"], sankey_df["Season"]]).unique().tolist()
    label_to_index = {label: i for i, label in enumerate(all_labels)}
    source = sankey_df["Gender"].map(label_to_index)
    target = sankey_df["Category"].map(label_to_index)
    value = sankey_df["count"]
    source2 = sankey_df["Category"].map(label_to_index)
    target2 = sankey_df["Season"].map(label_to_index)
    value2 = sankey_df["count"]
    fig4 = go.Figure(data=[go.Sankey(
        node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=all_labels),
        link=dict(source=source.tolist() + source2.tolist(), target=target.tolist() + target2.tolist(), value=value.tolist() + value2.tolist())
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

# 🔷 Hexbin: Payment Method vs Frequency of Purchases
st.subheader("🔷 Hexbin: Payment Method vs Frequency of Purchases")
if "Payment Method" in filtered_df.columns and "Frequency of Purchases" in filtered_df.columns:
    payment_map = {v: i for i, v in enumerate(filtered_df["Payment Method"].unique())}
    freq_map = {v: i for i, v in enumerate(filtered_df["Frequency of Purchases"].unique())}
    filtered_df["Payment Index"] = filtered_df["Payment Method"].map(payment_map)
    filtered_df["Frequency Index"] = filtered_df["Frequency of Purchases"].map(freq_map)
    fig6, ax6 = plt.subplots()
    hb = ax6.hexbin(filtered_df["Payment Index"], filtered_df["Frequency Index"], gridsize=10, cmap="Blues", mincnt=1)
    ax6.set_xlabel("Payment Method")
    ax6.set_ylabel("Frequency of Purchases")
    ax6.set_xticks(list(payment_map.values()))
    ax6.set_xticklabels(list(payment_map.keys()), rotation=45)
    ax6.set_yticks(list(freq_map.values()))
    ax6.set_yticklabels(list(freq_map.keys()))
    cb = fig6.colorbar(hb, ax=ax6)
    cb.set_label("Кількість покупців")
    st.pyplot(fig6)

# 🗺️ Сума покупок по штатах США
st.subheader("🗺️ Сума покупок по штатах США")
if "Location" in filtered_df.columns and "Purchase Amount (USD)" in filtered_df.columns:
    # 🔹 Додай словник відповідності штатів
    state_name_to_code = {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
        "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
        "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
        "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
        "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
        "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
        "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
        "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
        "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
        "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
    }

    # 🔹 Групування суми покупок по штатах
    location_sum = filtered_df.groupby("Location")["Purchase Amount (USD)"].sum().reset_index()
    location_sum.columns = ["StateName", "Total Purchase"]

    # 🔹 Перетворення назв штатів у коди
    location_sum["State"] = location_sum["StateName"].map(state_name_to_code)

    # 🔹 Видалити рядки з невідомими штатами
    location_sum = location_sum.dropna(subset=["State"])

    # 🔹 Побудова карти
    fig_map = px.choropleth(
        location_sum,
        locations="State",
        locationmode="USA-states",
        color="Total Purchase",
        scope="usa",
        color_continuous_scale="YlOrRd",  # 🔥 світло-жовтий → червоний
        labels={"Total Purchase": "Сума покупок ($)"},
        title="Сума покупок по штатах США"
    )

    st.plotly_chart(fig_map, use_container_width=True)
