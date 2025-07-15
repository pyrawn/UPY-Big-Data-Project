
from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator

import requests
import json

def extract_arbeitnow_data():
    url = "https://www.arbeitnow.com/api/job-board-api"
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    data = json.loads(response.text)
    with open('arbeitnow_data.json', 'w') as f:
        json.dump(data, f)

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

    def transform_arbeitnow_data():
        with open('arbeitnow_data.json', 'r') as f:
            data = json.load(f)
        
        transformed_data = []
        for item in data['data']:
            transformed_item = {
                'slug': item.get('slug'),
                'company_name': item.get('company_name'),
                'title': item.get('title'),
                'description': item.get('description'),
                'remote': item.get('remote'),
                'url': item.get('url'),
                'tags': item.get('tags'),
                'job_types': item.get('job_types'),
                'location': item.get('location'),
                'created_at': item.get('created_at')
            }
            transformed_data.append(transformed_item)

        with open('arbeitnow_data_transformed.json', 'w') as f:
            json.dump(transformed_data, f)

    transform_task = PythonOperator(
        task_id="transform",
        python_callable=transform_arbeitnow_data,
    )

    def load_arbeitnow_data():
        from pymongo import MongoClient
        import os

        mongo_user = os.getenv("MONGO_USER")
        mongo_pass = os.getenv("MONGO_PASSWORD")
        mongo_host = os.getenv("MONGO_HOST")
        mongo_port = os.getenv("MONGO_PORT")

        mongo_uri = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/admin"
        client = MongoClient(mongo_uri)


        db = client.big_data_project
        collection = db.arbeitnow_jobs
        with open('arbeitnow_data_transformed.json', 'r') as f:
            data = json.load(f)
        collection.insert_many(data)

    load_task = PythonOperator(
        task_id="load",
        python_callable=load_arbeitnow_data,
    )

    extract_task >> transform_task >> load_task
