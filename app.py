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

# 📊 Sidebar filters
st.sidebar.header("🔍 Фільтри")

# Age
age_range = st.sidebar.slider("Вік", int(df["Age"].min()), int(df["Age"].max()), (25, 45))

# Gender
gender = st.sidebar.multiselect("Стать", df["Gender"].unique())

# Item Purchased
item = st.sidebar.multiselect("Придбаний товар", df["Item Purchased"].unique())

# Category
category = st.sidebar.multiselect("Категорія", df["Category"].unique())

# Location
location = st.sidebar.multiselect("Штат", df["Location"].unique())

# Size
size = st.sidebar.multiselect("Розмір", df["Size"].unique())

# Color
color = st.sidebar.multiselect("Колір", df["Color"].unique())

# Season
season = st.sidebar.multiselect("Сезон", df["Season"].unique())

# Review Rating
rating_range = st.sidebar.slider("Рейтинг відгуку", float(df["Review Rating"].min()), float(df["Review Rating"].max()), (3.0, 5.0))

# Subscription Status
subscription = st.sidebar.radio("Підписка", df["Subscription Status"].unique())

# Shipping Type
shipping = st.sidebar.multiselect("Тип доставки", df["Shipping Type"].unique())

# Discount Applied
discount = st.sidebar.radio("Знижка застосована", df["Discount Applied"].unique())

# Promo Code Used
promo = st.sidebar.radio("Промокод використано", df["Promo Code Used"].unique())

# Payment Method
payment = st.sidebar.multiselect("Спосіб оплати", df["Payment Method"].unique())

# Frequency of Purchases
frequency = st.sidebar.multiselect("Частота покупок", df["Frequency of Purchases"].unique())

# 🔄 Apply filters
filtered_df = df.copy()
filtered_df = filtered_df[(filtered_df["Age"] >= age_range[0]) & (filtered_df["Age"] <= age_range[1])]
if gender: filtered_df = filtered_df[filtered_df["Gender"].isin(gender)]
if item: filtered_df = filtered_df[filtered_df["Item Purchased"].isin(item)]
if category: filtered_df = filtered_df[filtered_df["Category"].isin(category)]
if location: filtered_df = filtered_df[filtered_df["Location"].isin(location)]
if size: filtered_df = filtered_df[filtered_df["Size"].isin(size)]
if color: filtered_df = filtered_df[filtered_df["Color"].isin(color)]
if season: filtered_df = filtered_df[filtered_df["Season"].isin(season)]
filtered_df = filtered_df[(filtered_df["Review Rating"] >= rating_range[0]) & (filtered_df["Review Rating"] <= rating_range[1])]
if subscription: filtered_df = filtered_df[filtered_df["Subscription Status"] == subscription]
if shipping: filtered_df = filtered_df[filtered_df["Shipping Type"].isin(shipping)]
if discount: filtered_df = filtered_df[filtered_df["Discount Applied"] == discount]
if promo: filtered_df = filtered_df[filtered_df["Promo Code Used"] == promo]
if payment: filtered_df = filtered_df[filtered_df["Payment Method"].isin(payment)]
if frequency: filtered_df = filtered_df[filtered_df["Frequency of Purchases"].isin(frequency)]

# 🛒 Покупки по категоріях
st.subheader("🛒 Покупки по категоріях")
if "Category" in filtered_df.columns:
    st.bar_chart(filtered_df["Category"].value_counts())

# 👥 Розподіл статі
st.subheader("👥 Розподіл статі")
fig1, ax1 = plt.subplots()
ax1.pie(filtered_df["Gender"].value_counts(), labels=filtered_df["Gender"].value_counts().index, autopct="%1.1f%%", startangle=90)
ax1.axis("equal")
st.pyplot(fig1)

# 📊 Кореляція між числовими змінними
st.subheader("📊 Кореляція між числовими змінними")
numeric_cols = filtered_df.select_dtypes(include="number")
if not numeric_cols.empty:
    fig2, ax2 = plt.subplots()
    sns.heatmap(numeric_cols.corr(), annot=True, cmap="coolwarm", ax=ax2)
    st.pyplot(fig2)

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
    fig3 = go.Figure(data=[go.Sankey(
        node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=all_labels),
        link=dict(source=source.tolist() + source2.tolist(), target=target.tolist() + target2.tolist(), value=value.tolist() + value2.tolist())
    )])
    fig3.update_layout(title_text="Sankey Diagram: Gender → Category → Season", font_size=12)
    st.plotly_chart(fig3, use_container_width=True)

# 🗺️ Сума покупок по штатах США
st.subheader("🗺️ Сума покупок по штатах США")
if "Location" in filtered_df.columns and "Purchase Amount (USD)" in filtered_df.columns:
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
    location_sum = filtered_df.groupby("Location")["Purchase Amount (USD)"].sum().reset_index()
    location_sum.columns = ["StateName", "Total Purchase"]
    location_sum["State"] = location_sum["StateName"].map(state_name_to_code)
    location_sum = location_sum.dropna(subset=["State"])
    fig_map = px.choropleth(
        location_sum,
        locations="State",
        locationmode="USA-states",
        color="Total Purchase",
        scope="usa",
        color_continuous_scale="YlOrRd",
        labels={"Total Purchase": "Сума покупок ($)"},
        title="Сума покупок по штатах США"
    )
    st.plotly_chart(fig_map, use_container_width=True)
