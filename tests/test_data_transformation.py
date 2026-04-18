from pathlib import Path
import pickle

import numpy as np
import pandas as pd
import yaml

from networksecurity.components.data_transformation import DataTransformation
from networksecurity.entity.artifact_entity import DataValidationArtifact
from networksecurity.entity.config_entity import DataTransformationConfig, TrainingPipelineConfig


def _expected_columns() -> list[str]:
    schema = yaml.safe_load(Path("data_schema/schema.yaml").read_text())
    return [next(iter(column)) for column in schema["columns"]]


def _make_dataframe(row_count: int = 8) -> pd.DataFrame:
    columns = _expected_columns()
    rows = []
    for index in range(row_count):
        row = {}
        for feature_index, column in enumerate(columns[:-1]):
            row[column] = ((index + feature_index) % 3) - 1
        row["Result"] = -1 if index % 2 == 0 else 1
        rows.append(row)
    return pd.DataFrame(rows, columns=columns)


def test_initiate_data_transformation_saves_arrays_and_preprocessor(tmp_path, monkeypatch):
    dataframe = _make_dataframe()
    train_path = tmp_path / "validated_train.csv"
    test_path = tmp_path / "validated_test.csv"
    dataframe.iloc[:6].to_csv(train_path, index=False)
    dataframe.iloc[6:].to_csv(test_path, index=False)

    monkeypatch.chdir(tmp_path)

    config = DataTransformationConfig(TrainingPipelineConfig())
    config.transformed_train_file_path = str(tmp_path / "transformed" / "train.npy")
    config.transformed_test_file_path = str(tmp_path / "transformed" / "test.npy")
    config.transformed_object_file_path = str(tmp_path / "transformed_object" / "preprocessor.pkl")

    validation_artifact = DataValidationArtifact(
        validation_status=True,
        valid_train_file_path=str(train_path),
        valid_test_file_path=str(test_path),
        invalid_train_file_path=None,
        invalid_test_file_path=None,
        drift_report_file_path=str(tmp_path / "drift.yaml"),
    )

    artifact = DataTransformation(validation_artifact, config).initiate_data_transformation()

    train_array = np.load(config.transformed_train_file_path)
    test_array = np.load(config.transformed_test_file_path)
    cached_preprocessor_path = tmp_path / "final_models" / "preprocessor.pkl"

    assert artifact.transformed_train_file_path == config.transformed_train_file_path
    assert artifact.transformed_test_file_path == config.transformed_test_file_path
    assert Path(config.transformed_object_file_path).exists()
    assert cached_preprocessor_path.exists()
    assert train_array.shape[1] == len(dataframe.columns)
    assert test_array.shape[1] == len(dataframe.columns)
    assert set(np.unique(train_array[:, -1])).issubset({0, 1})
    assert set(np.unique(test_array[:, -1])).issubset({0, 1})

    with open(config.transformed_object_file_path, "rb") as file_obj:
        preprocessor = pickle.load(file_obj)
    assert hasattr(preprocessor, "transform")
