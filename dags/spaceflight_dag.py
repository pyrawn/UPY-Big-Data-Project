from __future__ import annotations

import pendulum
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from spaceflight_functions import extract_spaceflight_data
from spaceflight_functions import transform_spaceflight_data
from spaceflight_functions import load_spaceflight_data


# Define DAG
with DAG(
    dag_id="spaceflight_data_pipeline",
    schedule=None,
    start_date=pendulum.datetime(2025, 7, 14, tz="UTC"),
    catchup=False,
    tags=["spaceflight", "api"],
) as dag:

    # Task: Extract data from API
    extract_task = PythonOperator(
        task_id="extract",
        python_callable=extract_spaceflight_data,
    )

    # Task: Transform raw API data
    transform_task = PythonOperator(
        task_id="transform",
        python_callable=transform_spaceflight_data,
    )

    # Task: Load transformed data into MongoDB
    load_task = PythonOperator(
        task_id="load",
        python_callable=load_spaceflight_data,
    )

    # Define task dependencies
    extract_task >> transform_task >> load_task
