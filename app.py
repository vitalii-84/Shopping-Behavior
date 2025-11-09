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


# 👥 Візуалізація розподілу статі з силуетами
st.subheader("👥 Розподіл статі")
st.markdown("""
Ця візуалізація показує співвідношення між чоловіками та жінками серед покупців 
у більш емоційній формі — через силуети. Це дозволяє краще сприймати дані 
і створює візуальний зв’язок із аудиторією.
""")

# 🔹 Підрахунок відсотків
gender_counts = filtered_df["Gender"].value_counts(normalize=True) * 100
female_pct = round(gender_counts.get("Female", 0), 1)
male_pct = round(gender_counts.get("Male", 0), 1)

# 🔹 HTML-блок з вирівнюванням і стилями
st.markdown(f"""
<div style="display: flex; justify-content: center; align-items: center; gap: 20mm;">
  
  <!-- Лівий підпис -->
  <div style="text-align: right;">
    <h2 style="color: red; margin-right: 10px;">{female_pct}%</h2>
  </div>

  <!-- Силует жінки -->
  <div>
    <img src="https://raw.githubusercontent.com/vitalii-84/Shopping-Behavior/main/woman3.jpg" width="200"/>
  </div>

  <!-- Силует чоловіка -->
  <div>
    <img src="https://raw.githubusercontent.com/vitalii-84/Shopping-Behavior/main/man3.jpg" width="200"/>
  </div>

  <!-- Правий підпис -->
  <div style="text-align: left;">
    <h2 style="color: blue; margin-left: 10px;">{male_pct}%</h2>
  </div>

</div>
""", unsafe_allow_html=True)




# 🔥 Теплова карта взаємозв’язків (підтримує і категоріальні, і числові змінні)
st.subheader("📊 Теплова карта взаємозв’язків між змінними")
st.markdown("""
Ця теплова карта показує силу взаємозв’язків між змінними, включно з категоріальними (наприклад, стать, категорія товару, спосіб оплати).
Для оцінки зв’язків використовується коефіцієнт **Cramér’s V**, який підходить для якісних ознак.
""")

from scipy.stats import chi2_contingency
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# 🔹 Вибір колонок для аналізу
cols = [
    "Age", "Gender", "Item Purchased", "Category", "Purchase Amount (USD)",
    "Location", "Size", "Color", "Season", "Review Rating",
    "Subscription Status", "Shipping Type", "Discount Applied",
    "Promo Code Used", "Previous Purchases", "Payment Method",
    "Frequency of Purchases"
]

df_corr = filtered_df[cols].dropna()

# 🔹 Функція для обчислення Cramér’s V (підтримує будь-які категоріальні змінні)
def cramers_v(x, y):
    confusion_matrix = pd.crosstab(x, y)
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2 / n
    r, k = confusion_matrix.shape
    phi2corr = max(0, phi2 - ((k-1)*(r-1))/(n-1))
    rcorr = r - ((r-1)**2)/(n-1)
    kcorr = k - ((k-1)**2)/(n-1)
    return np.sqrt(phi2corr / min((kcorr-1), (rcorr-1)))

# 🔹 Побудова кореляційної матриці
corr_matrix = pd.DataFrame(index=cols, columns=cols, dtype=float)

for c1 in cols:
    for c2 in cols:
        if c1 == c2:
            corr_matrix.loc[c1, c2] = 1.0
        else:
            corr_matrix.loc[c1, c2] = cramers_v(df_corr[c1].astype(str), df_corr[c2].astype(str))

# 🔹 Візуалізація теплової карти
fig, ax = plt.subplots(figsize=(12, 9))
sns.heatmap(
    corr_matrix.astype(float),
    annot=True,
    cmap="YlGnBu",
    linewidths=0.5,
    fmt=".2f",
    annot_kws={"size": 8}
)
plt.title("Взаємозв’язки між змінними (Cramér’s V)", fontsize=14)
plt.xticks(rotation=45, ha="right", fontsize=8)
plt.yticks(fontsize=8)
fig.tight_layout()
st.pyplot(fig)


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



# 🗺️ Сума покупок по штатах США
st.subheader("🗺️ Сума покупок по штатах США")
st.markdown("""
Ця карта показує, в яких штатах США покупці витрачають найбільше. 
Скорочені назви штатів допомагають швидко зорієнтуватися на мапі.
""")

# 🔹 Словник скорочень штатів
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

# 🔹 Координати центрів штатів (спрощено)
state_coords = {
    "CA": [-119.4179, 36.7783], "TX": [-99.9018, 31.9686], "NY": [-75.4999, 43.0000],
    "FL": [-81.5158, 27.6648], "IL": [-89.3985, 40.6331], "PA": [-77.1945, 41.2033],
    "OH": [-82.9071, 40.4173], "GA": [-82.9071, 32.1656], "NC": [-79.0193, 35.7596],
    "MI": [-85.6024, 44.3148], "NJ": [-74.4057, 40.0583], "VA": [-78.6569, 37.4316],
    "WA": [-120.7401, 47.7511], "AZ": [-111.0937, 34.0489], "MA": [-71.3824, 42.4072],
    "TN": [-86.5804, 35.5175], "IN": [-86.1349, 40.2672], "MO": [-91.8318, 37.9643],
    "WI": [-89.6165, 43.7844], "CO": [-105.7821, 39.5501], "MN": [-94.6859, 46.7296],
    "SC": [-81.1637, 33.8361], "AL": [-86.9023, 32.3182], "LA": [-91.9623, 30.9843],
    "KY": [-84.2700, 37.8393], "OR": [-120.5542, 43.8041], "OK": [-97.0929, 35.0078],
    "CT": [-72.7554, 41.6032], "IA": [-93.0977, 41.8780], "MS": [-89.3985, 32.3547],
    "AR": [-92.3731, 35.2010], "KS": [-98.4842, 39.0119], "UT": [-111.0937, 39.3200],
    "NV": [-116.4194, 38.8026], "NM": [-105.8701, 34.5199], "NE": [-99.9018, 41.4925],
    "WV": [-80.4549, 38.5976], "ID": [-114.7420, 44.0682], "HI": [-155.5828, 19.8968],
    "NH": [-71.5724, 43.1939], "ME": [-69.4455, 45.2538], "RI": [-71.4774, 41.5801],
    "MT": [-110.3626, 46.8797], "DE": [-75.5277, 38.9108], "SD": [-99.9018, 43.9695],
    "ND": [-101.0020, 47.5515], "VT": [-72.5778, 44.5588], "AK": [-149.4937, 64.2008],
    "WY": [-107.2903, 43.0759]
}

# 🔹 Підготовка даних
location_sum = filtered_df.groupby("Location")["Purchase Amount (USD)"].sum().reset_index()
location_sum.columns = ["StateName", "Total Purchase"]
location_sum["State"] = location_sum["StateName"].map(state_name_to_code)
location_sum = location_sum.dropna(subset=["State"])

# 🔹 Побудова карти
fig_map = go.Figure()

# 🔸 Хлороплет
fig_map.add_trace(go.Choropleth(
    locations=location_sum["State"],
    z=location_sum["Total Purchase"],
    locationmode="USA-states",
    colorscale="YlOrRd",
    colorbar_title="Сума покупок ($)",
    marker_line_color="white"
))

# 🔸 Текстові підписи
for i, row in location_sum.iterrows():
    code = row["State"]
    if code in state_coords:
        lon, lat = state_coords[code]
        fig_map.add_trace(go.Scattergeo(
            locationmode="USA-states",
            lon=[lon],
            lat=[lat],
            text=code,
            mode="text",
            showlegend=False,
            textfont=dict(color="black", size=10)
        ))

# 🔹 Оформлення
fig_map.update_layout(
    title_text="Сума покупок по штатах США",
    geo=dict(scope="usa", projection=go.layout.geo.Projection(type="albers usa")),
    margin=dict(l=0, r=0, t=50, b=0)
)

# 🔹 Вивід у Streamlit
st.plotly_chart(fig_map, use_container_width=True)

