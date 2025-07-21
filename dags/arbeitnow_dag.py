from __future__ import annotations

import pendulum
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from arbeitnow_functions import extract_arbeitnow_data
from arbeitnow_functions import transform_arbeitnow_data
from arbeitnow_functions import load_arbeitnow_data

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
