import sys
import os

from dotenv import load_dotenv
load_dotenv()
mongo_db_url = os.getenv("MONGO_DB_URL") or os.getenv("MONGODB_URL_KEY")
app_port = int(os.getenv("PORT", "8000"))
train_api_key = os.getenv("TRAIN_API_KEY")
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile,Request, Header, HTTPException, status
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
import pandas as pd

from networksecurity.utils.main_utils.utils import load_object

from networksecurity.utils.ml_utils.model.estimator import NetworkModel

PREPROCESSOR_FILE_PATH = "final_models/preprocessor.pkl"
MODEL_FILE_PATH = "final_models/model.pkl"


def load_network_model() -> NetworkModel | None:
    try:
        if not os.path.exists(PREPROCESSOR_FILE_PATH) or not os.path.exists(MODEL_FILE_PATH):
            logging.warning("Prediction artifacts are not available yet.")
            return None

        preprocessor = load_object(PREPROCESSOR_FILE_PATH)
        final_model = load_object(MODEL_FILE_PATH)
        return NetworkModel(preprocessor=preprocessor, model=final_model)
    except Exception as e:
        raise NetworkSecurityException(e, sys)


def authorize_train_request(api_key: str | None) -> None:
    if train_api_key and api_key != train_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing training API key.",
        )


app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="./templates")

@app.on_event("startup")
async def startup_event():
    app.state.network_model = load_network_model()

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.post("/train")
async def train_route(x_api_key: str | None = Header(default=None, alias="x-api-key")):
    try:
        authorize_train_request(x_api_key)
        train_pipeline=TrainingPipeline()
        train_pipeline.run_pipeline()
        app.state.network_model = load_network_model()
        return Response("Training is successful")
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    
@app.post("/predict")
async def predict_route(request: Request,file: UploadFile = File(...)):
    try:
        df=pd.read_csv(file.file)
        network_model = getattr(app.state, "network_model", None)
        if network_model is None:
            raise FileNotFoundError("Prediction model is not loaded. Train the model or add artifacts to final_models.")
        print(df.iloc[0])
        y_pred = network_model.predict(df)
        print(y_pred)
        df['predicted_column'] = y_pred
        print(df['predicted_column'])
        df.to_csv('prediction_output/output.csv')
        table_html = df.to_html(classes='table table-striped')
        return templates.TemplateResponse(
        request,
        "table.html",
        {"request": request, "table": table_html}
        )
        
    except Exception as e:
            raise NetworkSecurityException(e,sys)

    
if __name__=="__main__":
    app_run(app,host="0.0.0.0",port=app_port)
