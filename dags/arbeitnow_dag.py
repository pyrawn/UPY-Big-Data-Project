from __future__ import annotations

import pendulum
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
import requests
import json
from bs4 import BeautifulSoup

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
    from bs4 import BeautifulSoup
    from datetime import datetime

    # Pull raw data from XCom
    raw_data = ti.xcom_pull(task_ids='extract', key='raw_arbeitnow_data')

    transformed_data = []
    for item in raw_data.get('data', []):  # Safely access 'data'
        # Clean description from HTML tags
        clean_description = BeautifulSoup(item.get('description', ''), "html.parser").get_text()

        # Process tags: add 'no tags' if empty
        tags = item.get('tags') or []
        if not tags:
            tags.append('no tags')

        # Simplify location: take only first word before first comma
        raw_location = item.get('location', '').strip()
        city = raw_location.split(',')[0].strip() if raw_location else 'Unknown'

        # Convert UNIX timestamp to readable datetime
        raw_created_at = item.get('created_at')
        created_at_dt = datetime.utcfromtimestamp(raw_created_at).strftime('%Y-%m-%d %H:%M:%S') \
            if raw_created_at else None

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

    # Push cleaned data to XCom
    ti.xcom_push(key='transformed_arbeitnow_data', value=transformed_data)



def load_arbeitnow_data(ti):
    from pymongo import MongoClient

    mongo_uri = "mongodb://root:example@mongo:27017/admin"
    client = MongoClient(mongo_uri)
    db = client.big_data_project
    collection = db.arbeitnow_jobs

    # Pull transformed data from XCom
    transformed_data = ti.xcom_pull(task_ids='transform', key='transformed_arbeitnow_data')

    if transformed_data:
        collection.insert_many(transformed_data)
        print(f"Inserted {len(transformed_data)} documents into MongoDB.")
    else:
        print("No transformed data to insert into MongoDB.")

# Define DAG
with DAG(
    dag_id="arbeitnow_data_pipeline",
    schedule=None,
    start_date=pendulum.datetime(2025, 7, 14, tz="UTC"),
    catchup=False,
    tags=["arbeitnow", "api"],
) as dag:

    extract_task = PythonOperator(
        task_id="extract",
        python_callable=extract_arbeitnow_data,
    )

    transform_task = PythonOperator(
        task_id="transform",
        python_callable=transform_arbeitnow_data,
    )

    load_task = PythonOperator(
        task_id="load",
        python_callable=load_arbeitnow_data,
    )

    extract_task >> transform_task >> load_task
