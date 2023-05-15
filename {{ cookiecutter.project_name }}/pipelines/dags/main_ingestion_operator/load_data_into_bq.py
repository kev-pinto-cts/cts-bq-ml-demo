"""Simple DAG to handle GCS object to BigQuery."""
import os
from datetime import date, datetime

from airflow.models.dag import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import \
    KubernetesPodOperator
from airflow.providers.google.cloud.operators.dataproc import \
    DataprocCreateBatchOperator
from airflow.providers.google.cloud.sensors.gcs import \
    GCSObjectsWithPrefixExistenceSensor
from airflow.providers.google.cloud.transfers.gcs_to_gcs import \
    GCSToGCSOperator
from kubernetes.client import models as k8s
from pipelines.dags.main_ingestion_operator.main_schema_definitions import \
    MainIngestionDag
from pipelines.shared.dag_loaders import generate_dags

project_id = os.getenv("GCP_PROJECT")
local = os.getenv("LOCAL")


def create_dag(dag_config: MainIngestionDag) -> DAG:
    """Create a dag from the given configuration.

    Args:
        dag_config (MainIngestionDag): The configuration for the DAG.

    Returns:
        DAG: The DAG to be created.
    """
    default_args = {
        "start_date": dag_config.airflow_variables.start_date,
        "owner": dag_config.airflow_variables.owner,
        "retries": dag_config.airflow_variables.retries,
        "catchup": dag_config.airflow_variables.catchup,
        "schedule_interval": dag_config.airflow_variables.schedule,
    }

    with DAG(
        dag_id=dag_config.dag_id,
        default_args=default_args,
        tags=dag_config.tags,
        max_active_runs=dag_config.airflow_variables.max_active_runs,
    ) as dag:
        batch_id = (
            f"{dag_config.dataset.replace('_', '-')}"
            f"-{dag_config.series_name.replace('_', '-')}"
            f"-{date.today().strftime('%Y-%m-%d')}"
            f"-{datetime.now().time().strftime('%H%M%S%f')}"
        )
        insert_into_bq = DataprocCreateBatchOperator(
            task_id="create_batch",
            project_id=dag_config.project,
            region=dag_config.airflow_variables.bigquery_location,
            batch={
                "pyspark_batch": {
                    "main_python_file_uri": f"gs://{dag_config.code_bucket}/dist/main.py",
                    "jar_file_uris": [
                        "gs://spark-lib/bigquery/spark-bigquery-with-dependencies_2.12-0.23.2.jar"
                    ],
                    "python_file_uris": [
                        f"gs://{dag_config.code_bucket}/dist/load_data_into_bq.zip"
                    ],
                    "args": [
                        f"--files={dag_config.table_name}",
                        f"--temp_bq_bucket={dag_config.temp_bucket}",
                        "--delimiter=,",
                        f"--schema={dag_config.schema_string}",
                        "--app_name=main_dag_ingest",
                        f"--data_bucket={dag_config.source_bucket}",
                        f"--dataset_name={dag_config.dataset}",
                        f"--table_name={dag_config.table_name}",
                    ],
                },
                "environment_config": {
                    "execution_config": {"subnetwork_uri": "default"}
                },
            },
            timeout=300,
            batch_id=batch_id,
        )
        target = "airflow-local" if local else "composer"

        command = (
            f"dbt run --profiles-dir /home/airflow/gcs/dags/dbt/profiles "
            f"--profile default -m {dag_config.dbt_model.name} "
            f"-t {target} --project-dir /home/airflow/gcs/dags/dbt".split()
        )

        volume_mounts = (
            [
                k8s.V1VolumeMount(
                    mount_path="/home/airflow/gcs/dags", name="dags-folder"
                ),
                k8s.V1VolumeMount(
                    mount_path="/root/.config/gcloud/", name="credentials"
                ),
            ]
            if local
            else []
        )
        volumes = (
            [
                k8s.V1Volume(name="dags-folder", host_path={"path": "/tmp/dags"}),  # nosec
                k8s.V1Volume(
                    name="credentials", host_path={"path": "/tmp/credentials"}  # nosec
                ),
            ]
            if local
            else []
        )

        image = "dbt_local" if local else ""
        image_pull_policy = "Never" if local else "IfNotPresent"

        run_dbt = KubernetesPodOperator(
            task_id="run_models",
            name="run_models",
            namespace="airflow",
            # TODO: Variablise the version
            image=image,
            cmds=command,
            is_delete_operator_pod=False,
            image_pull_policy=image_pull_policy,
            volume_mounts=volume_mounts,
            volumes=volumes,
            env_vars={"GCP_PROJECT": os.environ.get("GCP_PROJECT")},
        )

        move_to_archive = GCSToGCSOperator(
            task_id="move_to_archive",
            source_bucket=dag_config.source_bucket,
            source_objects=[f"{dag_config.series_name}/*"],
            destination_bucket=dag_config.archive_bucket,
            destination_object="census_archived.csv",
            move_object=True,
        )

        move_to_unprocessed = GCSToGCSOperator(
            task_id="move_to_unprocessed",
            source_bucket=dag_config.source_bucket,
            source_objects=[f"{dag_config.series_name}/*"],
            destination_bucket=dag_config.unprocessed_bucket,
            destination_object="census_unprocessed.csv",
            trigger_rule="all_failed",
            move_object=True,
        )
        if dag_config.airflow_variables.enable_sensors:
            wait_for_files = GCSObjectsWithPrefixExistenceSensor(
                task_id="wait_for_files",
                bucket=dag_config.source_bucket,
                prefix=dag_config.series_name,
            )
            wait_for_files.set_downstream(insert_into_bq)

        insert_into_bq >> run_dbt >> [move_to_archive, move_to_unprocessed]
    return dag


dags = generate_dags(directory="main_dags")
for dag_config in dags:
    globals()[dag_config.dag_id] = create_dag(dag_config)
