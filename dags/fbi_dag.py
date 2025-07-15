
from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator

import requests
import json

def extract_fbi_data():
    response = requests.get('https://api.fbi.gov/wanted/v1/list')
    data = json.loads(response.content)
    with open('fbi_data.json', 'w') as f:
        json.dump(data, f)

with DAG(
    dag_id="fbi_data_pipeline",
    schedule=None,
    start_date=pendulum.datetime(2025, 7, 14, tz="UTC"),
    catchup=False,
    tags=["fbi", "api"],
) as dag:
    extract_task = PythonOperator(
        task_id="extract",
        python_callable=extract_fbi_data,
    )

    def transform_fbi_data():
        with open('fbi_data.json', 'r') as f:
            data = json.load(f)
        
        transformed_data = []
        for item in data['items']:
            transformed_item = {
                'uid': item.get('uid'),
                'title': item.get('title'),
                'description': item.get('description'),
                'publication': item.get('publication'),
                'subjects': item.get('subjects'),
                'field_offices': item.get('field_offices'),
                'sex': item.get('sex'),
                'nationality': item.get('nationality'),
                'place_of_birth': item.get('place_of_birth'),
                'dates_of_birth_used': item.get('dates_of_birth_used'),
                'reward_text': item.get('reward_text'),
                'url': item.get('url'),
                'images': item.get('images')
            }
            transformed_data.append(transformed_item)

        with open('fbi_data_transformed.json', 'w') as f:
            json.dump(transformed_data, f)

    transform_task = PythonOperator(
        task_id="transform",
        python_callable=transform_fbi_data,
    )

    def load_fbi_data():
        from pymongo import MongoClient
        import os

        mongo_user = os.getenv("MONGO_USER")
        mongo_pass = os.getenv("MONGO_PASSWORD")
        mongo_host = os.getenv("MONGO_HOST")
        mongo_port = os.getenv("MONGO_PORT")

        mongo_uri = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/admin"
        client = MongoClient(mongo_uri)


        db = client.big_data_project
        collection = db.fbi_wanted
        with open('fbi_data_transformed.json', 'r') as f:
            data = json.load(f)
        collection.insert_many(data)

    load_task = PythonOperator(
        task_id="load",
        python_callable=load_fbi_data,
    )

    extract_task >> transform_task >> load_task
