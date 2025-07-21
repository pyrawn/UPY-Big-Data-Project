from __future__ import annotations

import pendulum
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from fbi_functions import extract_fbi_data
from fbi_functions import transform_fbi_data
from fbi_functions import load_fbi_data
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

    transform_task = PythonOperator(
        task_id="transform",
        python_callable=transform_fbi_data,
    )

    load_task = PythonOperator(
        task_id="load",
        python_callable=load_fbi_data,
    )

    extract_task >> transform_task >> load_task
