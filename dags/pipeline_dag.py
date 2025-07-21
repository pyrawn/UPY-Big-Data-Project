from __future__ import annotations

import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from pipeline import (
    extract_spaceflight_data,
    transform_spaceflight_data,
    extract_arbeitnow_data,
    transform_arbeitnow_data,
    extract_fbi_data,
    transform_fbi_data,
    load_data
)

# Define DAG
with DAG(
    dag_id="unified_data_pipeline",
    schedule=None,
    start_date=pendulum.datetime(2025, 7, 20, tz="UTC"),
    catchup=False,
    tags=["unified", "api", "pipeline"],
) as dag:

    # Spaceflight tasks
    extract_spaceflight = PythonOperator(
        task_id="extract_spaceflight",
        python_callable=extract_spaceflight_data
    )

    transform_spaceflight = PythonOperator(
        task_id="transform_spaceflight",
        python_callable=transform_spaceflight_data
    )

    # Arbeitnow tasks
    extract_arbeitnow = PythonOperator(
        task_id="extract_arbeitnow",
        python_callable=extract_arbeitnow_data
    )

    transform_arbeitnow = PythonOperator(
        task_id="transform_arbeitnow",
        python_callable=transform_arbeitnow_data
    )

    # FBI tasks
    extract_fbi = PythonOperator(
        task_id="extract_fbi",
        python_callable=extract_fbi_data
    )

    transform_fbi = PythonOperator(
        task_id="transform_fbi",
        python_callable=transform_fbi_data
    )

    # Load data (runs after all transformations)
    load_all = PythonOperator(
        task_id="load_data",
        python_callable=load_data
    )

    # Define dependencies
    extract_spaceflight >> transform_spaceflight >> load_all
    extract_arbeitnow >> transform_arbeitnow >> load_all
    extract_fbi >> transform_fbi >> load_all
