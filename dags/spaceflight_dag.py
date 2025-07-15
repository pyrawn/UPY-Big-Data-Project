
from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator

import requests
import json



def extract_spaceflight_data():
    response = requests.get('https://api.spaceflightnewsapi.net/v4/articles')
    data = json.loads(response.content)
    with open('spaceflight_data.json', 'w') as f:
        json.dump(data, f)

with DAG(
    dag_id="spaceflight_data_pipeline",
    schedule=None,
    start_date=pendulum.datetime(2025, 7, 14, tz="UTC"),
    catchup=False,
    tags=["spaceflight", "api"],
) as dag:
    extract_task = PythonOperator(
        task_id="extract",
        python_callable=extract_spaceflight_data,
    )

    def transform_spaceflight_data():
        with open('spaceflight_data.json', 'r') as f:
            data = json.load(f)
        
        transformed_data = []
        for item in data['results']:
            transformed_item = {
                'id': item.get('id'),
                'title': item.get('title'),
                'url': item.get('url'),
                'image_url': item.get('image_url'),
                'news_site': item.get('news_site'),
                'summary': item.get('summary'),
                'published_at': item.get('published_at'),
                'updated_at': item.get('updated_at'),
                'featured': item.get('featured'),
                'launches': item.get('launches'),
                'events': item.get('events')
            }
            transformed_data.append(transformed_item)

        with open('spaceflight_data_transformed.json', 'w') as f:
            json.dump(transformed_data, f)

    transform_task = PythonOperator(
        task_id="transform",
        python_callable=transform_spaceflight_data,
    )

    def load_spaceflight_data():
        from pymongo import MongoClient
        import os
        from urllib.parse import quote_plus

        mongo_user = "root"
        mongo_pass = "example"
        mongo_host = "mongo"
        mongo_port = "27017"

        print("Mongo user:", mongo_user)
        print("Mongo pass:", mongo_pass)
        print("Mongo host:", mongo_host)
        print("Mongo port:", mongo_port)


        mongo_uri = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/admin"
        print(mongo_uri)
        client = MongoClient(mongo_uri)


        db = client.big_data_project
        collection = db.spaceflight_news
        print(db)
        print(collection)
        with open('spaceflight_data_transformed.json', 'r') as f:
            data = json.load(f)
        collection.insert_many(data)

    load_task = PythonOperator(
        task_id="load",
        python_callable=load_spaceflight_data,
    )

    extract_task >> transform_task >> load_task
