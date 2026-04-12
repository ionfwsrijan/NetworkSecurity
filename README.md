# Network Security ML Project

An end-to-end machine learning project for detecting and classifying network threats using structured data pipelines and supervised learning workflows. The project is organized around modular components for data ingestion, validation, transformation, model training, batch prediction, and deployment.

## Overview

This repository implements a production-style ML pipeline for cybersecurity use cases. It is designed to process network security data, validate schema and input quality, transform features, train predictive models, and serve results through an application layer.

The codebase follows a modular architecture to improve maintainability, reproducibility, and deployment readiness.

## Core Capabilities

- Data ingestion from source files and MongoDB
- Schema-based data validation
- Data transformation and preprocessing
- Model training and artifact generation
- Batch prediction pipeline
- Model and preprocessor persistence
- Application interface for inference
- Containerization support with Docker

## Project Structure

```text
NETWORKSECURITY/
├── .github/workflows/
│   └── main.yml
├── Artifacts/
│   ├── <timestamp>/
│   │   ├── data_ingestion/
│   │   ├── data_validation/
│   │   ├── data_transformation/
│   │   └── model_trainer/
├── data_schema/
│   └── schema.yaml
├── final_models/
│   ├── model.pkl
│   └── preprocessor.pkl
├── logs/
├── Network_Data/
│   └── pishingData.csv
├── networksecurity/
│   ├── cloud/
│   │   └── s3_syncer.py
│   ├── components/
│   │   ├── data_ingestion.py
│   │   ├── data_validation.py
│   │   ├── data_transformation.py
│   │   └── model_trainer.py
│   ├── constant/
│   ├── entity/
│   │   ├── artifact_entity.py
│   │   └── config_entity.py
│   ├── exception/
│   │   └── exception.py
│   ├── logging/
│   │   └── logger.py
│   ├── pipeline/
│   │   ├── batch_prediction.py
│   │   └── training_pipeline.py
│   └── utils/
├── notebooks/
├── prediction_output/
│   └── output.csv
├── templates/
│   └── table.html
├── valid_data/
│   └── test.csv
├── app.py
├── Dockerfile
├── main.py
├── push_data.py
├── README.md
├── requirements.txt
├── setup.py
└── test_mongodb.py
```

## Architecture

The project is divided into the following layers:

### 1. Components
The `components` package contains the core stages of the ML workflow:
- `data_ingestion.py` handles loading data into the pipeline
- `data_validation.py` validates schema and dataset consistency
- `data_transformation.py` applies preprocessing and feature preparation
- `model_trainer.py` trains and evaluates the selected models

### 2. Entity and Configuration
The `entity` package defines configuration and artifact classes used to standardize communication between pipeline stages.

### 3. Pipeline
The `pipeline` package orchestrates execution:
- `training_pipeline.py` runs the end-to-end training workflow
- `batch_prediction.py` handles inference on new input data

### 4. Deployment and Integration
- `app.py` exposes the model through an application layer
- `Dockerfile` supports containerized deployment
- `cloud/s3_syncer.py` provides cloud synchronization support

## Data Flow

The project follows this sequence:

1. Raw network security data is loaded into the system
2. Schema and structural checks are performed
3. Features are transformed for training compatibility
4. Models are trained and evaluated
5. Serialized artifacts are saved for reuse
6. New data is passed through the saved preprocessor and model for prediction

## Technology Stack

- **Language:** Python
- **Libraries:** Pandas, NumPy, Scikit-learn
- **Database:** MongoDB
- **Deployment:** Flask/FastAPI-style app interface, Docker
- **Version Control:** Git and GitHub

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/network-security-ml-project.git
cd network-security-ml-project
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Project

### Run the training pipeline

```bash
python main.py
```

### Run the application

```bash
python app.py
```

### Run the MongoDB data push script

```bash
python push_data.py
```

## Outputs

During execution, the project generates:

- Timestamped pipeline artifacts under `Artifacts/`
- Trained model and preprocessor files under `final_models/`
- Log files under `logs/`
- Prediction results under `prediction_output/output.csv`

## Use Cases

This project can be extended for:

- Network intrusion detection
- Malicious traffic classification
- Security event analysis
- Cybersecurity-focused ML experimentation

## Future Improvements

- Real-time streaming inference
- Model versioning and experiment tracking
- CI/CD based deployment pipeline
- Improved monitoring and alerting
- Cloud-native deployment support

## Author

**Srijan Jaiswal**

- GitHub: https://github.com/ionfwsrijan
- LinkedIn: https://www.linkedin.com/in/srijan-jaiswal-ds
