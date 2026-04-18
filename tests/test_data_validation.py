from pathlib import Path

import pandas as pd
import yaml

from networksecurity.components.data_validation import DataValidation
from networksecurity.entity.artifact_entity import DataIngestionArtifact
from networksecurity.entity.config_entity import DataValidationConfig, TrainingPipelineConfig


def _expected_columns() -> list[str]:
    schema_path = Path("data_schema/schema.yaml")
    schema = yaml.safe_load(schema_path.read_text())
    return [next(iter(column)) for column in schema["columns"]]


def _make_dataframe(row_count: int = 6) -> pd.DataFrame:
    columns = _expected_columns()
    rows = []
    for index in range(row_count):
        row = {}
        for column in columns[:-1]:
            row[column] = (index % 3) - 1
        row["Result"] = -1 if index % 2 == 0 else 1
        rows.append(row)
    return pd.DataFrame(rows, columns=columns)


def test_validate_number_of_columns_matches_schema():
    dataframe = _make_dataframe()
    config = DataValidationConfig(TrainingPipelineConfig())
    ingestion_artifact = DataIngestionArtifact("train.csv", "test.csv")
    validator = DataValidation(ingestion_artifact, config)

    assert validator.validate_number_of_columns(dataframe) is True
    assert validator.validate_number_of_columns(dataframe.drop(columns=["Result"])) is False


def test_initiate_data_validation_writes_validated_outputs(tmp_path):
    dataframe = _make_dataframe(row_count=10)
    train_path = tmp_path / "ingested_train.csv"
    test_path = tmp_path / "ingested_test.csv"
    dataframe.iloc[:8].to_csv(train_path, index=False)
    dataframe.iloc[8:].to_csv(test_path, index=False)

    config = DataValidationConfig(TrainingPipelineConfig())
    config.valid_train_file_path = str(tmp_path / "validated" / "train.csv")
    config.valid_test_file_path = str(tmp_path / "validated" / "test.csv")
    config.invalid_train_file_path = str(tmp_path / "invalid" / "train.csv")
    config.invalid_test_file_path = str(tmp_path / "invalid" / "test.csv")
    config.drift_report_file_path = str(tmp_path / "drift" / "report.yaml")

    ingestion_artifact = DataIngestionArtifact(str(train_path), str(test_path))
    artifact = DataValidation(ingestion_artifact, config).initiate_data_validation()

    assert artifact.validation_status is True
    assert artifact.valid_train_file_path == config.valid_train_file_path
    assert artifact.valid_test_file_path == config.valid_test_file_path
    assert Path(config.valid_train_file_path).exists()
    assert Path(config.valid_test_file_path).exists()
    assert Path(config.drift_report_file_path).exists()
