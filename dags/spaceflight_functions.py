import requests
import json
from airflow.models import Variable


def extract_spaceflight_data(ti):
    # Get the current offset from Airflow Variable (default to 0)
    offset = int(Variable.get("spaceflight_api_offset", default_var=0))

    # Build URL dynamically based on offset
    base_url = "https://api.spaceflightnewsapi.net/v4/articles"
    if offset == 0:
        url = base_url  # Case base: no offset param
    else:
        url = f"{base_url}/?offset={offset}"  # Subsequent triggers with offset

    print(f"Fetching data from URL: {url}")

    # Make API request
    response = requests.get(url)
    data = response.json()

    # Push raw API data to XCom
    ti.xcom_push(key='raw_spaceflight_data', value=data)

    # Check if there are results to avoid incrementing offset unnecessarily
    if data.get('results'):
        next_offset = offset + 10
        Variable.set("spaceflight_api_offset", next_offset)
        print(f"Next offset set to: {next_offset}")
    else:
        print("No more results returned from API. Offset will not be incremented.")


def transform_spaceflight_data(ti):
    # Pull raw data from XCom
    raw_data = ti.xcom_pull(task_ids='extract', key='raw_spaceflight_data')

    transformed_data = []
    for item in raw_data.get('results', []):  # Safely access 'results'
        transformed_item = {
            'id': item.get('id'),
            'title': item.get('title'),
            'url': item.get('url'),
            'image_url': item.get('image_url'),
            'news_site': item.get('news_site'),
            'summary': item.get('summary'),
            'published_at': item.get('published_at'),
            'updated_at': item.get('updated_at')
        }
        transformed_data.append(transformed_item)

    # Push transformed data to XCom
    ti.xcom_push(key='transformed_spaceflight_data', value=transformed_data)


def load_spaceflight_data(ti):
    from pymongo import MongoClient

    # MongoDB connection URI
    mongo_uri = "mongodb://root:example@mongo:27017/admin"
    client = MongoClient(mongo_uri)
    db = client.big_data_project
    collection = db.spaceflight_news

    # Pull transformed data from XCom
    transformed_data = ti.xcom_pull(task_ids='transform', key='transformed_spaceflight_data')

    if transformed_data:
        # Insert data into MongoDB
        collection.insert_many(transformed_data)
        print(f"Inserted {len(transformed_data)} documents into MongoDB.")
    else:
        print("No transformed data to insert into MongoDB.")

