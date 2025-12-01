import os
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.adapters.yolo_adapter import YoloV11Adapter
from app.application.prediction_service import PredictionService
from app.adapters.api import controller
from app.application.batch_manager import BatchInferenceManager

# --- CONFIGURACIÓN ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("main")  # <--- ESTA LÍNEA FALTABA

# Variables de entorno
MODEL_NAME = os.getenv("YOLO_MODEL", "yolo11n.pt")
ENABLE_BATCHING = os.getenv("ENABLE_BATCHING", "false").lower() == "true"
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "8"))

# 1. Inicializar Adaptadores (Infraestructura)
logger.info(f"Cargando modelo YOLO: {MODEL_NAME}...")
yolo_adapter = YoloV11Adapter(MODEL_NAME)

# 2. Configurar Motor de Inferencia (Patrón 1 vs Patrón 2)
if ENABLE_BATCHING:
    logger.info(f"🚀 MODO: Adaptive Batching Activado (Size: {BATCH_SIZE})")
    # El manager envuelve al adaptador real para encolar peticiones
    inference_engine = BatchInferenceManager(yolo_adapter, max_batch_size=BATCH_SIZE)
else:
    logger.info("🏎️ MODO: Inferencia Síncrona Directa")
    inference_engine = yolo_adapter

# 3. Inicializar Casos de Uso (Aplicación)
# Inyectamos el motor de inferencia (sea directo o batching)
prediction_service = PredictionService(model=inference_engine)

# 4. Configurar Framework Web (Entrada)
app = FastAPI(title="YOLO11 Hexagonal API")

# CORS para que el Frontend (React) pueda hablar con el Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inyección de dependencia manual al controlador
controller.set_service(prediction_service)
app.include_router(controller.router)

if __name__ == "__main__":
    logger.info("Iniciando servidor Uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=8000)