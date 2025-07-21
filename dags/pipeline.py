import requests
import json
from airflow.models import Variable
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient


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
    raw_data = ti.xcom_pull(task_ids='extract_spaceflight', key='raw_spaceflight_data')
    if not raw_data:
        print("No raw data found in XCom for transform_spaceflight_data")
        return

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

    ti.xcom_push(key='transformed_spaceflight_data', value=transformed_data)



def extract_arbeitnow_data(ti):
    # Get current page from Airflow Variable (default to 1)
    page = int(Variable.get("arbeitnow_api_page", default_var=1))

    base_url = "https://www.arbeitnow.com/api/job-board-api"
    url = f"{base_url}?search=&tags=&sort_by=newest&page={page}"

    print(f"Fetching data from URL: {url}")

    # Make API request
    response = requests.get(url)
    data = response.json()

    # Push raw API data to XCom
    ti.xcom_push(key='raw_arbeitnow_data', value=data)

    # Check if there are results and increment page
    if data.get('data'):
        next_page = page + 1
        Variable.set("arbeitnow_api_page", next_page)
        print(f"Next page set to: {next_page}")
    else:
        print("No more results returned from API. Page will not be incremented.")

def transform_arbeitnow_data(ti):
    raw_data = ti.xcom_pull(task_ids='extract_arbeitnow', key='raw_arbeitnow_data')
    if not raw_data:
        print("No raw data found in XCom for transform_arbeitnow_data")
        return

    transformed_data = []
    for item in raw_data.get('data', []):  # Safely access 'data'
        clean_description = BeautifulSoup(item.get('description', ''), "html.parser").get_text()
        tags = item.get('tags') or ['no tags']
        raw_location = item.get('location', '').strip()
        city = raw_location.split(',')[0].strip() if raw_location else 'Unknown'
        raw_created_at = item.get('created_at')
        created_at_dt = datetime.utcfromtimestamp(raw_created_at).strftime('%Y-%m-%d %H:%M:%S') if raw_created_at else None

        transformed_item = {
            'slug': item.get('slug'),
            'company_name': item.get('company_name'),
            'title': item.get('title'),
            'description': clean_description,
            'remote': item.get('remote'),
            'url': item.get('url'),
            'tags': tags,
            'job_types': item.get('job_types'),
            'location': city,
            'created_at': created_at_dt
        }
        transformed_data.append(transformed_item)

    ti.xcom_push(key='transformed_arbeitnow_data', value=transformed_data)


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
    raw_data = ti.xcom_pull(task_ids='extract_fbi', key='raw_fbi_data')
    if not raw_data:
        print("⚠️ No raw data found in XCom for transform_fbi_data")
        return

    transformed_data = []
    for item in raw_data.get('items', []):
        field_offices = item.get('field_offices') or ["Not offices available"]
        nationality = item.get('nationality') or "Unknown"
        race = item.get('race') or "No information"
        reward_text = item.get('reward_text') or "Description not provided"
        aliases = item.get('aliases') or ["No aliases"]

        sex_raw = item.get('sex')
        if isinstance(sex_raw, str):
            sex_lower = sex_raw.lower()
            sex = 'F' if sex_lower == 'female' else 'M' if sex_lower == 'male' else 'NS'
        else:
            sex = 'NS'

        publication = item.get('publication')
        publication_dt = None
        if publication:
            try:
                publication_dt = datetime.fromisoformat(publication.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass

        modified = item.get('modified')
        modified_dt = None
        if modified:
            try:
                modified_dt = datetime.fromisoformat(modified.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass

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
            'image_url': first_image_url
        }
        transformed_data.append(transformed_item)

    ti.xcom_push(key='transformed_fbi_data', value=transformed_data)


def load_data(ti):
    # MongoDB connection URI
    mongo_uri = "mongodb://root:example@mongo:27017/admin"
    client = MongoClient(mongo_uri)
    db = client.big_data_project

    # Try loading data for each API
    api_sources = {
        'transformed_spaceflight_data': 'spaceflight_news',
        'transformed_arbeitnow_data': 'arbeitnow_jobs',
        'transformed_fbi_data': 'fbi_wanted'
    }

    loaded_any = False

    for xcom_key, collection_name in api_sources.items():
        transformed_data = ti.xcom_pull(task_ids='transform', key=xcom_key)

        if transformed_data:
            collection = db[collection_name]
            collection.insert_many(transformed_data)
            print(f"Inserted {len(transformed_data)} documents into MongoDB collection: {collection_name}")
            loaded_any = True

    if not loaded_any:
        print("No transformed data found in XCom for any API.")
