import streamlit as st
from pymongo import MongoClient
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image
from PIL import UnidentifiedImageError
import requests
from io import BytesIO

# ---- Configuración de la página ----
st.set_page_config(page_title="FBI Wanted Dashboard", page_icon="🕵️‍♂️")
st.title("🕵️‍♂️ FBI Wanted Dashboard")

# ---- Conexión a MongoDB ----
@st.cache_data
def get_data():
    client = MongoClient("mongodb://root:example@mongo:27017/")
    db = client.big_data_project
    collection = db.fbi_wanted
    data = list(collection.find())
    return pd.DataFrame(data)

if st.button("🔄 Refresh Data"):
    get_data.clear()
    st.rerun()

df = get_data()

# ---- KPI Section ----
st.header("📊 Key Performance Indicators")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Profiles", len(df))
with col2:
    st.metric("Unique Nationalities", df['nationality'].nunique())
with col3:
    st.metric("Field Offices", df['field_offices'].explode().nunique())

# ---- Word Cloud ----
st.header("☁️ Most Common Words in Titles")
if 'title' in df.columns and not df['title'].dropna().empty:
    text = " ".join(df['title'].dropna())
    wordcloud = WordCloud(width=800, height=400, background_color='white', min_word_length=3).generate(text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)
else:
    st.write("No title data available for word cloud.")

# ---- Pie Charts ----
st.header("📈 Distributions")
col4, col5 = st.columns(2)
with col4:
    sex_counts = df['sex'].value_counts()
    st.subheader("Sex Distribution")
    st.bar_chart(sex_counts)
with col5:
    race_counts = df['race'].value_counts()
    st.subheader("Race Distribution")
    st.bar_chart(race_counts)

# ---- Time Series ----
st.header("📅 Cases Over Time")
df['publication'] = pd.to_datetime(df['publication'], errors='coerce')
if not df['publication'].isna().all():
    time_series = df.groupby(df['publication'].dt.date).size()
    st.line_chart(time_series)
else:
    st.write("No publication date data available.")

st.header("👤 Wanted Profiles")
if len(df) > 0:
    current_index = st.number_input("Browse profiles", min_value=0, max_value=1000, value=0, step=1)
    selected_profile = df.iloc[current_index]

    # Get image URL directly
    image_url = selected_profile.get('image_url', "https://placehold.co/400x400?text=No+Image")

    # Display image directly from URL with max height
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="{image_url}" alt="Wanted Person Image" style="max-height: 400px; width: auto; border-radius: 10px;">
            <p><em>Reference image of the wanted person</em></p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Display profile details
    st.subheader(selected_profile['title'])
    st.text(f"Nationality: {selected_profile['nationality']}")
    st.text(f"Sex: {selected_profile['sex']}")
    st.text(f"Race: {selected_profile['race']}")
    st.text(f"Reward: {selected_profile['reward_text']}")
    st.text(f"Publication Date: {selected_profile['publication']}")
else:
    st.write("No profiles available.")
