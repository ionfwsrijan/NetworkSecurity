from networksecurity.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException 
from networksecurity.logging.logger import logging 
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH
from scipy.stats import ks_2samp
import pandas as pd
import os,sys
from networksecurity.utils.main_utils.utils import read_yaml_file,write_yaml_file

class DataValidation:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,
                 data_validation_config:DataValidationConfig):
        
        try:
            self.data_ingestion_artifact=data_ingestion_artifact
            self.data_validation_config=data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
            self._expected_columns = self.get_schema_columns()
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def get_schema_columns(self)->list:
        try:
            schema_columns = self._schema_config.get("columns", [])
            expected_columns = [next(iter(column)) for column in schema_columns]
            if not expected_columns:
                raise ValueError("Schema columns are not available for validation.")
            return expected_columns
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    @staticmethod
    def read_data(file_path)->pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def validate_number_of_columns(self,dataframe:pd.DataFrame)->bool:
        try:
            expected_columns = self._expected_columns
            actual_columns = dataframe.columns.tolist()
            logging.info(f"Required number of columns:{len(expected_columns)}")
            logging.info(f"Data frame has columns:{len(actual_columns)}")
            if actual_columns == expected_columns:
                return True

            missing_columns = [column for column in expected_columns if column not in actual_columns]
            unexpected_columns = [column for column in actual_columns if column not in expected_columns]
            logging.error(
                "Column validation failed. Missing columns: %s. Unexpected columns: %s.",
                missing_columns,
                unexpected_columns,
            )
            return False
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def detect_dataset_drift(self,base_df,current_df,threshold=0.05)->bool:
        try:
            status=True
            report={}
            for column in base_df.columns:
                d1=base_df[column]
                d2=current_df[column]
                is_same_dist=ks_2samp(d1,d2)
                if threshold<=is_same_dist.pvalue:
                    is_found=False
                else:
                    is_found=True
                    status=False
                report.update({column:{
                    "p_value":float(is_same_dist.pvalue),
                    "drift_status":is_found
                    
                    }})
            drift_report_file_path = self.data_validation_config.drift_report_file_path

            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path,exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path,content=report)
            return status

        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    
    def initiate_data_validation(self)->DataValidationArtifact:
        try:
            train_file_path=self.data_ingestion_artifact.trained_file_path
            test_file_path=self.data_ingestion_artifact.test_file_path

            train_dataframe=DataValidation.read_data(train_file_path)
            test_dataframe=DataValidation.read_data(test_file_path)

            validation_errors = []
            if not self.validate_number_of_columns(dataframe=train_dataframe):
                validation_errors.append("Train dataframe columns do not match the schema.")
            if not self.validate_number_of_columns(dataframe=test_dataframe):
                validation_errors.append("Test dataframe columns do not match the schema.")
            if validation_errors:
                raise ValueError(" ".join(validation_errors))

            status=self.detect_dataset_drift(base_df=train_dataframe,current_df=test_dataframe)
            dir_path=os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path,exist_ok=True)

            train_dataframe.to_csv(
                self.data_validation_config.valid_train_file_path, index=False, header=True

            )

            test_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path, index=False, header=True
            )
            
            data_validation_artifact = DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path,
            )
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
