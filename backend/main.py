import os
import boto3
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import get_db, PredictionRecord

# --- 1. AWS S3 Configuration ---
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = "house-price-model-storage"
MODEL_FILE_KEY = "house_price_pipeline.pkl"
LOCAL_MODEL_PATH = "/tmp/house_price_pipeline.pkl" 

# --- 2. Download and Load Model ---
def load_model_from_s3():
    try:
        if not os.path.exists(LOCAL_MODEL_PATH):
            print(f"Downloading {MODEL_FILE_KEY} from S3...")
            s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
            s3_client.download_file(BUCKET_NAME, MODEL_FILE_KEY, LOCAL_MODEL_PATH)
            print("Download complete.")
        
        return joblib.load(LOCAL_MODEL_PATH)
    except Exception as e:
        print(f"Error loading model from S3: {e}")
        return None

pipeline = load_model_from_s3()

# --- 3. Initialize FastAPI ---
app = FastAPI(title="House Price Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. Input Validation ---
class HouseInput(BaseModel):
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float

# --- 5. Endpoints ---
@app.get("/")
def read_root():
    return {"message": "House Price Prediction API is running."}

@app.post("/predict")
def predict_price(house: HouseInput, db: Session = Depends(get_db)):
    if pipeline is None:
        raise HTTPException(status_code=503, detail="ML Model failed to load from S3.")
    
    try:
        # Format input exactly as the training script did
        input_data = pd.DataFrame([{
            "MedInc": house.MedInc,
            "HouseAge": house.HouseAge,
            "AveRooms": house.AveRooms,
            "AveBedrms": house.AveBedrms,
            "Population": house.Population,
            "AveOccup": house.AveOccup,
            "Latitude": house.Latitude,
            "Longitude": house.Longitude
        }])
        
        # Predict
        prediction_value = float(pipeline.predict(input_data)[0])
        
        # Save to Database
        db_record = PredictionRecord(
            med_inc=house.MedInc,
            house_age=house.HouseAge,
            ave_rooms=house.AveRooms,
            ave_bedrms=house.AveBedrms,
            population=house.Population,
            ave_occup=house.AveOccup,
            latitude=house.Latitude,
            longitude=house.Longitude,
            predicted_price=prediction_value
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        return {
            "predicted_price": round(prediction_value, 3),
            "message": "Prediction saved to database",
            "record_id": db_record.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Prediction error: {str(e)}")