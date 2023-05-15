"""The Schema definitions for DAGS."""

from datetime import datetime
from os import getenv
from typing import List, Union

from attr import define, field, validators  # type: ignore
from pendulum import yesterday
from pipelines.dags.main_ingestion_operator.dbt_schema import (
    DbtTable, Model, PiiRedactionVars, Source, SourceTable)
from pipelines.shared.converters import (convert_to_dataset_name,
                                         split_keywords, version_to_int)
from pipelines.shared.validators import (check_for_duplicate_col_names,
                                         is_greater_than_one,
                                         validate_column_name)

VALID_TYPES = ["STRING", "INTEGER", "DECIMAL"]
VALID_CLASSIFICATIONS = ["RED", "ORANGE", "GREEN"]


@define(frozen=True)
class AirflowVariables:
    """Default Airflow variables."""

    owner: str = field(default="Data Engineering")
    enable_sensors: bool = field(default=True)
    bigquery_location: str = field(default="europe-west2")
    schedule: Union[str, None] = field(default=None)
    max_active_runs: int = field(default=1)
    catchup: bool = field(default=False)
    email_on_failure: bool = field(default=False)
    start_date: datetime = field(default=yesterday(), init=True)
    gcp_connection: str = field(default="google_cloud_default")
    retries: int = field(default=0)


@define()
class Schema:
    """Define the schema of a column."""

    column_name: str = field(
        validator=[validators.instance_of(str), validate_column_name]
    )
    column_data_type: str = field(validator=[validators.in_(VALID_TYPES)])
    column_description: str = field(default="")
    column_length: str = field(
        default=255, validator=validators.instance_of(int), converter=int
    )
    column_format: str = field(default="")
    column_is_pk: bool = field(default=False, converter=bool)
    column_is_fk: bool = field(default=False, converter=bool)
    column_nullable: bool = field(default=False, converter=bool)
    column_is_pii: bool = field(default=False)


@define
class MainIngestionDag:
    """Define the config of a main ingestion DAG."""

    dataset_asset_name: str
    dataset_supplier: str
    series_columns: List[Schema] = field(validator=[check_for_duplicate_col_names])
    dataset_domain: str
    series_name: str
    mou_dsa_reference: str
    series_security_classification: str = field(
        validator=validators.in_(VALID_CLASSIFICATIONS)
    )
    dataset_search_keywords: str = field(default="", converter=split_keywords)
    project: str = getenv("GCP_PROJECT", "TEST")
    expected_files: int = field(
        default=1,
        converter=int,
        validator=[validators.instance_of(int), is_greater_than_one],
    )
    schema_version: str = field(
        default=1,
        converter=version_to_int,
        validator=[validators.instance_of(int), is_greater_than_one],
    )
    airflow_variables: AirflowVariables = AirflowVariables()
    description: str = field(default="Description goes here!")
    paused: bool = field(default=False)
    dataset: str = field(default="", init=False)
    dag_id: str = field(default="", init=False)
    tags: list = field(default="", init=False)
    source_bucket: str = field(default="", init=False)
    unprocessed_bucket: str = field(default="", init=False)
    archive_bucket: str = field(default="", init=False)
    project_dataset_table: str = field(default="", init=False)
    code_bucket: str = field(default="", init=False)
    temp_bucket: str = field(default="", init=False)
    schema_string: str = field(default="", init=False)
    dataset_dash: str = field(default="", init=False)
    table_name: str = field(default="", init=False)
    dbt_image: str = field(default="", init=False)

    def __attrs_post_init__(self):
        """Define the variables post init."""
        self.dataset = convert_to_dataset_name(self.dataset_asset_name)
        self.dataset_dash = self.dataset.replace("_", "-")
        self.tags = [self.dataset, self.series_name] + self.dataset_search_keywords  # type: ignore
        self.project_dataset_table = (
            f"{self.project}.{self.dataset}.{self.series_name}_{self.schema_version}"
        )
        self.dag_id = f"{self.dataset}_{self.series_name}_v{self.schema_version}"
        self.source_bucket = f"{self.project}-{self.dataset_dash}-source"
        self.unprocessed_bucket = f"{self.project}-{self.dataset_dash}-unprocessed"
        self.archive_bucket = f"{self.project}-{self.dataset_dash}-archive"
        self.code_bucket = f"{self.project}-code"
        self.temp_bucket = f"{self.project}-temp"
        self.schema_string = ",".join(
            [f"{col.column_name} {col.column_data_type}" for col in self.series_columns]
        )
        self.table_name = f"{self.series_name}_v{self.schema_version}"
        self.dbt_image = f"eu.gcr.io/{self.project}/dbt"

    @property
    def dbt_model(self):
        """Define the dbt model related to this DAG."""
        return Model(
            name=self.dag_id,
            description=self.description,
            variables=PiiRedactionVars(
                not_pii_data=",\n".join(
                    [
                        f"\t{col.column_name}"
                        for col in self.series_columns
                        if not col.column_is_pii
                    ]
                ),
                table_source=f"source('{self.dataset}', '{self.table_name}')",
            ),
            sources=[
                Source(
                    name=self.dataset,
                    source_tables=[SourceTable(self.table_name)],
                    schema=self.dataset,
                )
            ],
            tables=[
                DbtTable(
                    name=f"{self.dag_id}_filter_pii_data",
                    schema=f"{self.dataset}_restricted",
                    sql="filter_pii_data.sql",
                    materialized="view",
                    alias=self.table_name,
                    description=f"{self.series_name} with PII redacted",
                    columns=[
                        {"name": col.column_name, "description": col.column_description}
                        for col in self.series_columns
                        if not col.column_is_pii
                    ],
                )
            ],
        )
