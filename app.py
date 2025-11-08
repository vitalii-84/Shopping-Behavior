import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# 🔧 Налаштування сторінки Streamlit
st.set_page_config(page_title="🛍️ Shopping Behavior Dashboard", layout="wide")

# 📥 Завантаження даних
@st.cache_data
def load_data():
    return pd.read_csv("shopping_behavior_csv.csv")

df = load_data()

# 🏷️ Заголовок дашборду
st.title("🛍️ Shopping Behavior Dashboard")

# 📊 Панель фільтрів
st.sidebar.header("🔍 Фільтри")

# 🔘 Кнопка для очищення фільтрів
if "reset" not in st.session_state:
    st.session_state.reset = False

if st.sidebar.button("🔄 Очистити всі фільтри"):
    st.session_state.reset = True

# 📍 Слайдер для віку
age_min, age_max = int(df["Age"].min()), int(df["Age"].max())
age_range = (age_min, age_max) if st.session_state.reset else st.sidebar.slider("Вік", age_min, age_max, (age_min, age_max))

# 📍 Слайдер для рейтингу
rating_min, rating_max = float(df["Review Rating"].min()), float(df["Review Rating"].max())
rating_range = (rating_min, rating_max) if st.session_state.reset else st.sidebar.slider("Рейтинг відгуку", rating_min, rating_max, (rating_min, rating_max))

# 📍 Функція для мультивибору з опцією "вибрати все"
def multi_filter(label, column):
    options = df[column].dropna().unique().tolist()
    default = options if st.session_state.reset else options
    return st.sidebar.multiselect(label, options=options, default=default)

# 📍 Всі фільтри
gender = multi_filter("Стать", "Gender")
item = multi_filter("Придбаний товар", "Item Purchased")
category = multi_filter("Категорія", "Category")
location = multi_filter("Штат", "Location")
size = multi_filter("Розмір", "Size")
color = multi_filter("Колір", "Color")
season = multi_filter("Сезон", "Season")
subscription = multi_filter("Підписка", "Subscription Status")
shipping = multi_filter("Тип доставки", "Shipping Type")
discount = multi_filter("Знижка застосована", "Discount Applied")
promo = multi_filter("Промокод використано", "Promo Code Used")
payment = multi_filter("Спосіб оплати", "Payment Method")
frequency = multi_filter("Частота покупок", "Frequency of Purchases")

# 🔄 Застосування фільтрів до DataFrame
filtered_df = df.copy()
filtered_df = filtered_df[(filtered_df["Age"] >= age_range[0]) & (filtered_df["Age"] <= age_range[1])]
filtered_df = filtered_df[(filtered_df["Review Rating"] >= rating_range[0]) & (filtered_df["Review Rating"] <= rating_range[1])]
filtered_df = filtered_df[filtered_df["Gender"].isin(gender)]
filtered_df = filtered_df[filtered_df["Item Purchased"].isin(item)]
filtered_df = filtered_df[filtered_df["Category"].isin(category)]
filtered_df = filtered_df[filtered_df["Location"].isin(location)]
filtered_df = filtered_df[filtered_df["Size"].isin(size)]
filtered_df = filtered_df[filtered_df["Color"].isin(color)]
filtered_df = filtered_df[filtered_df["Season"].isin(season)]
filtered_df = filtered_df[filtered_df["Subscription Status"].isin(subscription)]
filtered_df = filtered_df[filtered_df["Shipping Type"].isin(shipping)]
filtered_df = filtered_df[filtered_df["Discount Applied"].isin(discount)]
filtered_df = filtered_df[filtered_df["Promo Code Used"].isin(promo)]
filtered_df = filtered_df[filtered_df["Payment Method"].isin(payment)]
filtered_df = filtered_df[filtered_df["Frequency of Purchases"].isin(frequency)]

# 📊 Бар-графік по категоріях

st.subheader("🛒 Покупки по категоріях")
st.markdown("""
Цей графік показує, які категорії товарів найчастіше купують користувачі. 
Найпопулярніші — одяг та аксесуари. Це може свідчити про сезонні тренди або переваги певних груп покупців.
""")
st.bar_chart(filtered_df["Category"].value_counts())

# 🧁 Кругова діаграма по статі
st.subheader("👥 Розподіл статі")
st.markdown("""
Ця діаграма демонструє співвідношення між чоловіками та жінками серед покупців. 
Це дозволяє краще таргетувати маркетингові кампанії.
""")
fig1, ax1 = plt.subplots(figsize=(8, 4))  # 👈 ширина екрана
ax1.pie(filtered_df["Gender"].value_counts(), labels=filtered_df["Gender"].value_counts().index, autopct="%1.1f%%", startangle=90)
ax1.axis("equal")
fig1.tight_layout()  # 👈 адаптація до контейнера
st.pyplot(fig1)

# 🔥 Теплова карта кореляцій
st.subheader("📊 Кореляція між числовими змінними")
st.markdown("""
Теплова карта показує, як різні числові змінні пов’язані між собою. 
Наприклад, частота покупок може корелювати з сумою витрат.
""")
numeric_cols = filtered_df.select_dtypes(include="number")
if not numeric_cols.empty:
    fig2, ax2 = plt.subplots(figsize=(5, 5))  # 🔧 Розмір графіка
    sns.heatmap(numeric_cols.corr(), annot=True, cmap="coolwarm", ax=ax2)
    fig2.tight_layout()
    st.pyplot(fig2)


# 🔀 Sankey Diagram: Gender → Category → Season
st.subheader("🔀 Потік покупок: Gender → Category → Season")
st.markdown("""
Ця діаграма показує, як стать покупця впливає на вибір категорії товару, 
а потім — на сезон покупки. Це допомагає виявити поведінкові патерни.
""")

import plotly.graph_objects as go
import colorsys
import pandas as pd

if all(col in filtered_df.columns for col in ["Gender", "Category", "Season"]):
    # 🔹 Групування даних
    sankey_df = filtered_df.groupby(["Gender", "Category", "Season"]).size().reset_index(name="count")

    # 🔹 Унікальні мітки для вузлів
    all_labels = pd.concat([sankey_df["Gender"], sankey_df["Category"], sankey_df["Season"]]).unique().tolist()
    label_to_index = {label: i for i, label in enumerate(all_labels)}

    # 🔹 Потоки: Gender → Category
    source = sankey_df["Gender"].map(label_to_index)
    target = sankey_df["Category"].map(label_to_index)
    value = sankey_df["count"]

    # 🔹 Потоки: Category → Season
    source2 = sankey_df["Category"].map(label_to_index)
    target2 = sankey_df["Season"].map(label_to_index)
    value2 = sankey_df["count"]

    # 🔹 Генерація яскравих кольорів (пастельна палітра)
    def generate_colors(n):
        hues = [i / n for i in range(n)]
        return [
            f"rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, 0.9)"
            for h in hues
            for r, g, b in [colorsys.hsv_to_rgb(h, 0.5, 0.9)]
        ][:n]

    node_colors = generate_colors(len(all_labels))

    # 🔹 Побудова Sankey Diagram із покращеною візуалізацією
    fig3 = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color="black", width=0.8),
            label=all_labels,
            color=node_colors,
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_color="black"
            )
        ),
        link=dict(
            source=source.tolist() + source2.tolist(),
            target=target.tolist() + target2.tolist(),
            value=value.tolist() + value2.tolist(),
            color="rgba(150,150,150,0.3)"  # напівпрозорі лінії
        )
    )])

    # 🔹 Покращений стиль діаграми
    fig3.update_layout(
        title=dict(
            text="Sankey Diagram: Gender → Category → Season",
            font=dict(size=18, color="black"),
            x=0.5
        ),
        font=dict(color="black", size=15),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    # 🔹 Вивід у Streamlit
    st.plotly_chart(fig3, use_container_width=True)



# 🗺️ Інтерактивна карта суми покупок по штатах
st.subheader("🗺️ Сума покупок по штатах США")
st.markdown("""
Ця карта показує, в яких штатах США покупці витрачають найбільше. 
Це корисно для геотаргетингу та логістичного планування.
""")
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
