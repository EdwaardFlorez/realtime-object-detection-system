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
    

@router.websocket("/ws/predict")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("🔌 Cliente WebSocket conectado")
    
    try:
        while True:
            # 1. Recibir el blob de la imagen (bytes)
            data = await websocket.receive_bytes()
            
            # 2. Decodificar imagen (CPU Bound - esto sigue siendo pesado)
            nparr = np.frombuffer(data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is not None:
                # 3. Inferencia (Tu servicio ya existente)
                # NOTA: execute_prediction es síncrono, podría bloquear el loop si no se maneja bien.
                # Para producción real se usaría run_in_executor, pero para tesis está bien así por ahora.
                result = service.execute_prediction(img)
                
                # 4. Enviar JSON de respuesta
                # Convertimos el objeto PredictionResult a dict para enviarlo
                response_dict = {
                    "inference_time_ms": result.inference_time_ms,
                    "total_time_ms": result.total_time_ms,
                    "count": result.count,
                    "annotated_image_base64": result.annotated_image_base64
                }
                await websocket.send_json(response_dict)
            else:
                await websocket.send_text("Error: Invalid Image")

    except WebSocketDisconnect:
        logger.info("🔌 Cliente desconectado")
    except Exception as e:
        logger.error(f"Error en WS: {e}")
        try:
            await websocket.close()
        except:
            pass