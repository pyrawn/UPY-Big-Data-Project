import streamlit as st
from pymongo import MongoClient
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.express as px
from wordcloud import STOPWORDS

st.set_page_config(page_title="ArbeitNow Job Dashboard", page_icon="💼")

st.title("💼 ArbeitNow Job Dashboard")

# --- Get Data from MongoDB ---
@st.cache_data
def get_data():
    client = MongoClient("mongodb://root:example@mongo:27017/")
    db = client.big_data_project
    collection = db.arbeitnow_jobs
    data = list(collection.find())
    return pd.DataFrame(data)

if st.button("🔄 Refresh Data"):
    get_data.clear()
    st.rerun()

df = get_data()

# --- KPIs ---
st.header("📊 Key Performance Indicators")
col1, col2, col3 = st.columns(3)

# Total Jobs
with col1:
    st.metric("Total Job Postings", len(df))

# Unique Companies
with col2:
    company_count = df['company_name'].nunique()
    st.metric("Hiring Companies", company_count)

# Remote Jobs
with col3:
    remote_jobs = df['remote'].sum() if 'remote' in df else 0
    st.metric("Remote Jobs", remote_jobs)


# --- Pie Chart: Job Types ---
st.header("📑 Job Types Distribution")
if 'job_types' in df.columns and not df['job_types'].dropna().empty:
    job_types_expanded = df['job_types'].explode().value_counts()
    fig = px.pie(names=job_types_expanded.index, values=job_types_expanded.values,
                 title="Distribution of Job Types")
    st.plotly_chart(fig)
else:
    st.write("No job types data available.")

# --- Location Distribution ---
st.header("🌍 Job Locations")
if 'location' in df.columns and not df['location'].dropna().empty:
    location_counts = df['location'].value_counts().nlargest(10)
    fig = px.bar(x=location_counts.values, y=location_counts.index, orientation='h',
                 labels={'x': 'Number of Jobs', 'y': 'City'}, title="Top 10 Job Locations")
    st.plotly_chart(fig)
else:
    st.write("No location data available.")

# Add custom stopwords (German gender notations + common fillers)
custom_stopwords = set(STOPWORDS)
custom_stopwords.update(['m', 'w', 'd', 'm/w/d', 'mwd', 'mit', 'für', 'und', 'der', 'die', 'das'])

st.header("☁️ Most Common Words in Job Titles")
if 'title' in df.columns and not df['title'].dropna().empty:
    text = " ".join(df['title'].dropna())

    # Keep only words with ≥3 letters and exclude stopwords
    filtered_words = " ".join([
        word for word in text.split()
        if len(word) >= 3 and word.lower() not in custom_stopwords
    ])

    # Generate word cloud
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        stopwords=custom_stopwords
    ).generate(filtered_words)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)
else:
    st.write("No job titles available for word cloud.")




# --- Bar Chart: Top Hiring Companies ---
st.header("🏢 Top Hiring Companies")
if 'company_name' in df.columns and not df['company_name'].dropna().empty:
    top_companies = df['company_name'].value_counts().nlargest(10)
    fig = px.bar(x=top_companies.values, y=top_companies.index, orientation='h',
                 labels={'x': 'Number of Jobs', 'y': 'Company'}, title="Top 10 Hiring Companies")
    st.plotly_chart(fig)
else:
    st.write("No company data available.")

# --- Time Series: Jobs Over Time ---
st.header("📅 Jobs Posted Over Time")
if 'created_at' in df.columns and not df['created_at'].dropna().empty:
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    jobs_over_time = df.groupby(df['created_at'].dt.date).size()
    st.line_chart(jobs_over_time, use_container_width=True, height=300)
else:
    st.write("No created_at data available for time series.")



# --- Data Table: 5 Most Recent Jobs ---
st.header("📖 5 Most Recent Job Listings")
if {'title', 'company_name', 'location', 'url', 'created_at'}.issubset(df.columns):
    # Sort by created_at descending and take the top 5
    df_sorted = df.sort_values(by='created_at', ascending=False).head(5)
    df_table = df_sorted[['title', 'company_name', 'location', 'url']].dropna()
    
    # Make job titles clickable
    df_table['title'] = df_table.apply(lambda row: f"[{row['title']}]({row['url']})", axis=1)
    
    # Display as Markdown
    st.markdown(df_table[['title', 'company_name', 'location']].to_markdown(index=False), unsafe_allow_html=True)
else:
    st.write("Required columns (title, company_name, location, url, created_at) are missing.")

