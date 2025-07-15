import streamlit as st
from pymongo import MongoClient
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image
import requests
from io import BytesIO

st.set_page_config(page_title="Spaceflight News Dashboard", page_icon="🚀")

st.title("🚀 Spaceflight News Dashboard")

@st.cache_data
def get_data():
    client = MongoClient("mongodb://root:example@mongo:27017/")
    db = client.big_data_project
    collection = db.spaceflight_news
    data = list(collection.find())
    return pd.DataFrame(data)

if st.button("🔄 Refresh Data"):
    get_data.clear()  # Clear cached data
    st.rerun()
  # Reload app

df = get_data()



# --- KPI Section ---
st.header("📊 Key Performance Indicators")
col1, col2 = st.columns(2)

# Total Articles
with col1:
    st.metric("Total Articles", len(df))

# Featured Articles
with col2:
    if 'news_site' in df.columns:
        site_count = df['news_site'].nunique()
    else:
        site_count = 0
    st.metric("News Sites", site_count)


# --- Word Cloud of Titles ---
st.header("☁️ Most Common Words in Titles")
if 'title' in df.columns and not df['title'].dropna().empty:
    text = " ".join(df['title'].dropna())
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)
else:
    st.write("No title data available for word cloud.")

# --- Collage of Images ---
st.header("🖼️ Article Image Collage")
if 'image_url' in df.columns and not df['image_url'].dropna().empty:
    images = []
    for url in df['image_url'].dropna().unique()[:12]:  # Limit to 12 images
        try:
            response = requests.get(url, timeout=5)
            img = Image.open(BytesIO(response.content))
            images.append(img)
        except Exception:
            continue

    if images:
        cols = st.columns(4)
        for idx, img in enumerate(images):
            with cols[idx % 4]:
                st.image(img, use_container_width =True)
    else:
        st.write("No images available.")
else:
    st.write("No image URLs in dataset.")

# --- Pie Chart of News Sites ---
st.header("📈 Articles by News Site")
if 'news_site' in df.columns and not df['news_site'].dropna().empty:
    site_counts = df['news_site'].value_counts()
    st.plotly_chart({
        "data": [{"values": site_counts.values, "labels": site_counts.index, "type": "pie"}],
        "layout": {"title": "Articles Distribution by News Site"}
    })
else:
    st.write("No news site data available.")

# --- Time Series Charts ---
st.header("📅 Articles Over Time")
if 'published_at' in df.columns and not df['published_at'].dropna().empty:
    df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')
    published_counts = df.groupby(df['published_at'].dt.date).size()
    st.line_chart(published_counts, use_container_width=True, height=300)

if 'updated_at' in df.columns and not df['updated_at'].dropna().empty:
    df['updated_at'] = pd.to_datetime(df['updated_at'], errors='coerce')
    updated_counts = df.groupby(df['updated_at'].dt.date).size()
    st.line_chart(updated_counts, use_container_width=True, height=300)

# --- Data Table ---
st.header("📖 Articles Summary")
if {'title', 'summary', 'url'}.issubset(df.columns):
    df_table = df[['title', 'summary', 'url']].dropna(subset=['title', 'summary', 'url'])
    df_table['title'] = df_table.apply(lambda row: f"[{row['title']}]({row['url']})", axis=1)
    st.markdown(df_table[['title', 'summary']].to_markdown(index=False), unsafe_allow_html=True)
else:
    st.write("Required columns (title, summary, url) are missing.")
