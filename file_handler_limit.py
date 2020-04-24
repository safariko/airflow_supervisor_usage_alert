# load the dependencies
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import date, timedelta, datetime

# default_args are the default arguments applied to the Dag's tasks
DAG_DEFAULT_ARGS = {
        'owner': 'airflow',
        'depends_on_past': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=1)
}

with DAG('File_Handler_Limit_Check', start_date=datetime(2019, 9, 29), schedule_interval='0 1/6 * * *', default_args=DAG_DEFAULT_ARGS, catchup=False) as dag:
	task1 = BashOperator(task_id="limit_check", bash_command='python3 /home/ubuntu/airflow/input_files_for_dags/safar/file_descriptor/file_handler_limit.py ')




