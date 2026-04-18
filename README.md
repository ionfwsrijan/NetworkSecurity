# NetworkSecurity

End-to-end phishing website detection project built with Python, scikit-learn, MongoDB, FastAPI, and GitHub Actions.

The project trains a classifier on structured phishing features, saves a preprocessor and model to `final_models/`, exposes prediction through a FastAPI app, and stores timestamped pipeline outputs under `Artifacts/`.

## What This Repo Does

- Loads phishing data from MongoDB into the training pipeline
- Validates input schema and train/test drift
- Applies preprocessing with a saved scikit-learn pipeline
- Trains multiple classification models and selects the best one by F1 score
- Saves artifacts for reuse in inference
- Serves predictions through a FastAPI endpoint
- Syncs pipeline outputs and saved models to S3 during API-triggered training

## Project Layout

```text
NetworkSecurity/
|-- .github/workflows/main.yml
|-- Artifacts/
|-- data_schema/schema.yaml
|-- final_models/
|-- logs/
|-- Network_Data/phisingData.csv
|-- networksecurity/
|   |-- cloud/s3_syncer.py
|   |-- components/
|   |-- constant/
|   |-- entity/
|   |-- exception/
|   |-- logging/logger.py
|   |-- pipeline/
|   `-- utils/
|-- prediction_output/
|-- templates/table.html
|-- app.py
|-- Dockerfile
|-- main.py
|-- push_data.py
|-- requirements.txt
`-- setup.py
```

## Environment Variables

Set these in `.env` for local development or as secrets/env vars in deployment:

| Variable | Required | Purpose |
| --- | --- | --- |
| `MONGO_DB_URL` | Yes | Primary MongoDB connection string used by ingestion, training, and `push_data.py` |
| `MONGODB_URL_KEY` | Optional | Fallback MongoDB variable supported by `app.py` |
| `PORT` | Optional | FastAPI port, defaults to `8000` locally |
| `TRAIN_API_KEY` | Optional | If set, `/train` requires an `x-api-key` header |
| `AWS_ACCESS_KEY_ID` | For S3 sync/deploy | AWS credential used when training syncs artifacts to S3 |
| `AWS_SECRET_ACCESS_KEY` | For S3 sync/deploy | AWS credential used when training syncs artifacts to S3 |
| `AWS_REGION` | For S3 sync/deploy | AWS region for deployment and AWS CLI access |

## Local Setup

1. Create and activate a virtual environment.

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Add a `.env` file.

```env
MONGO_DB_URL="your-mongodb-connection-string"
PORT=8000
TRAIN_API_KEY=your-optional-train-key
```

## Load Data Into MongoDB

If your MongoDB collection is empty, push the local CSV dataset into MongoDB first:

```powershell
python push_data.py
```

This reads `Network_Data/phisingData.csv` and inserts it into:

- database: `NetworkSecurity`
- collection: `NetworkData`

## Training Options

### Option 1: Run the local training script

```powershell
python main.py
```

This runs the component flow directly:

1. Data ingestion
2. Data validation
3. Data transformation
4. Model training

Outputs are written under `Artifacts/<timestamp>/` and `final_models/`.

### Option 2: Trigger training through the API

Start the app:

```powershell
python app.py
```

Then call the training endpoint:

```powershell
Invoke-WebRequest `
  -Method Post `
  -Uri "http://127.0.0.1:8000/train" `
  -Headers @{ "x-api-key" = "your-optional-train-key" }
```

Notes:

- If `TRAIN_API_KEY` is not set, the `x-api-key` header is not required.
- API-triggered training uses `TrainingPipeline.run_pipeline()`, which also syncs:
  - `Artifacts/<timestamp>/` to `s3://netsecmlops/artifact/<timestamp>`
  - `final_models/` to `s3://netsecmlops/final_models/<timestamp>`

## Prediction Usage

Start the FastAPI app:

```powershell
python app.py
```

Open the docs UI:

- `http://127.0.0.1:8000/docs`

Or upload a CSV directly to `/predict`:

```powershell
curl -X POST "http://127.0.0.1:8000/predict" ^
  -H "accept: text/html" ^
  -H "Content-Type: multipart/form-data" ^
  -F "file=@valid_data/test.csv"
```

Behavior:

- The app loads `final_models/preprocessor.pkl` and `final_models/model.pkl` once at startup
- Predictions are rendered as an HTML table
- A CSV copy is saved to `prediction_output/output.csv`

## Training Flow

The pipeline works in this order:

1. `data_ingestion.py`
   Reads records from MongoDB, exports a feature-store CSV, and performs a stratified train/test split.
2. `data_validation.py`
   Validates expected columns from `data_schema/schema.yaml` and writes a drift report.
3. `data_transformation.py`
   Applies a `KNNImputer` preprocessing pipeline and saves transformed arrays plus the preprocessor.
4. `model_trainer.py`
   Trains several classifiers, selects the best one by F1 score, logs metrics to MLflow/DagsHub, and saves the final model.

## Outputs

Main generated outputs:

- `Artifacts/<timestamp>/...`
- `final_models/model.pkl`
- `final_models/preprocessor.pkl`
- `prediction_output/output.csv`
- `logs/<timestamp>.log`

## CI/CD

GitHub Actions currently handles:

- dependency installation
- Python syntax/compile checks
- `pytest` execution when a `tests/` directory exists
- Docker build and push to Amazon ECR
- container deployment on the self-hosted runner

Workflow file:

- `.github/workflows/main.yml`

## Current Notes

- The app expects `final_models/` artifacts to exist before prediction.
- `final_models/` is currently present in the repository and used directly by the app.
- The repository also contains historical artifact and cache files from previous local runs.

