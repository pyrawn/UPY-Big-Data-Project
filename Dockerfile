FROM apache/airflow:2.8.1

USER root
RUN apt-get update && apt-get install -y build-essential
USER airflow

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
