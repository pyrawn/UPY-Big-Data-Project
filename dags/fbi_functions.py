import requests
import json
from datetime import datetime
from pymongo import MongoClient
from airflow.models import Variable


def extract_fbi_data(ti):
    page = int(Variable.get("fbi_api_page", default_var=1))
    url = f"https://api.fbi.gov/wanted/v1/list?page={page}"
    print(f"Fetching data from URL: {url}")

    response = requests.get(url)
    data = response.json()
    ti.xcom_push(key='raw_fbi_data', value=data)

    if data.get('items'):
        next_page = page + 1
        Variable.set("fbi_api_page", next_page)
        print(f"Next page set to: {next_page}")
    else:
        print("No more results. Page will not be incremented.")

def transform_fbi_data(ti):
    from datetime import datetime

    raw_data = ti.xcom_pull(task_ids='extract', key='raw_fbi_data')
    transformed_data = []

    for item in raw_data.get('items', []):
        # Fix missing values
        field_offices = item.get('field_offices') or ["Not offices available"]
        nationality = item.get('nationality') or "Unknown"
        race = item.get('race') or "No information"
        reward_text = item.get('reward_text') or "Description not provided"
        aliases = item.get('aliases') or ["No aliases"]

        # Simplify sex to F/M/NS safely
        sex_raw = item.get('sex')
        if isinstance(sex_raw, str):
            sex_lower = sex_raw.lower()
            sex = 'F' if sex_lower == 'female' else 'M' if sex_lower == 'male' else 'NS'
        else:
            sex = 'NS'

        # Format dates safely
        publication = item.get('publication')
        if publication:
            try:
                publication_dt = datetime.fromisoformat(publication.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                publication_dt = None
        else:
            publication_dt = None

        modified = item.get('modified')
        if modified:
            try:
                modified_dt = datetime.fromisoformat(modified.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                modified_dt = None
        else:
            modified_dt = None

        # Get first image's large URL or fallback
        images = item.get('images')
        if images and isinstance(images, list) and len(images) > 0:
            first_image_url = images[0].get('large', "https://via.placeholder.com/400x400.png?text=No+Image+Available")
        else:
            first_image_url = "https://via.placeholder.com/400x400.png?text=No+Image+Available"

        transformed_item = {
            'uid': item.get('uid'),
            'title': item.get('title'),
            'description': item.get('description'),
            'field_offices': field_offices,
            'nationality': nationality,
            'race': race,
            'reward_text': reward_text,
            'sex': sex,
            'publication': publication_dt,
            'modified': modified_dt,
            'image_url': first_image_url  # Save only the large URL
        }
        transformed_data.append(transformed_item)

    ti.xcom_push(key='transformed_fbi_data', value=transformed_data)

def load_fbi_data(ti):
    mongo_uri = "mongodb://root:example@mongo:27017/admin"
    client = MongoClient(mongo_uri)
    db = client.big_data_project
    collection = db.fbi_wanted

    transformed_data = ti.xcom_pull(task_ids='transform', key='transformed_fbi_data')

    if transformed_data:
        collection.insert_many(transformed_data)
        print(f"Inserted {len(transformed_data)} documents into MongoDB.")
    else:
        print("No transformed data to insert.")
