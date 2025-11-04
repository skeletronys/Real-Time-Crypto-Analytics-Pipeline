FROM apache/airflow:2.8.1-python3.10

USER airflow
RUN pip install --no-cache-dir \
    dbt-core==1.7.0 \
    dbt-athena-community==1.7.2 \
    boto3 \
    botocore

RUN dbt --version