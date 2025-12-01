from fastapi import APIRouter, UploadFile, File, HTTPException
from app.application.prediction_service import PredictionService
import cv2
import numpy as np

router = APIRouter()

# Inyección de dependencia manual (o podrías usar librerías como dependency_injector)
# Por simplicidad, lo pasaremos desde main.py
service: PredictionService = None 

def set_service(svc: PredictionService):
    global service
    service = svc

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/predict")
async def predict_endpoint(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image")

        result = service.execute_prediction(img)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))