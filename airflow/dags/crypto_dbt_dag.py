"""
Crypto DBT DAG
Runs DBT models hourly to transform data
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# Default arguments
default_args = {
    'owner': 'crypto-analytics',
    'depends_on_past': False,
    'start_date': datetime(2025, 10, 30),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    'crypto_dbt_pipeline',
    default_args=default_args,
    description='Run DBT models for crypto analytics',
    schedule_interval='0 * * * *',  # Everyhour
    catchup=False,
    tags=['dbt', 'crypto', 'analytics'],
)

# Task 1: DBT run (run all models)
dbt_run = BashOperator(
    task_id='dbt_run',
    bash_command="""
    cd /opt/airflow/crypto_dbt && \
    export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID && \
    export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY && \
    export AWS_DEFAULT_REGION=eu-north-1 && \
    dbt run
    """,
    dag=dag,
)

# Task 2: DBT test (check data quality)
dbt_test = BashOperator(
    task_id='dbt_test',
    bash_command="""
    cd /opt/airflow/crypto_dbt && \
    export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID && \
    export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY && \
    export AWS_DEFAULT_REGION=eu-north-1 && \
    dbt test
    """,
    dag=dag,
)

# Dependencies: first run, then test
dbt_run >> dbt_test
