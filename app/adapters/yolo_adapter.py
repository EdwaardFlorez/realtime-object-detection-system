# --- IMPORTS CRÍTICOS ---
import cv2        # <--- ESTE ES EL QUE FALTA AHORA
import base64     # <--- Y ESTE PARA LA RESPUESTA
import time
import numpy as np
# ------------------------

from ultralytics import YOLO
from app.domain.ports import ObjectDetectionModel
import logging

logger = logging.getLogger("yolo-adapter")

class YoloV11Adapter(ObjectDetectionModel):
    def __init__(self, model_path: str):
        logger.info(f"Cargando modelo YOLO: {model_path}")
        self.model = YOLO(model_path)
        # Warm-up
        self.model(np.zeros((640, 640, 3), dtype=np.uint8), verbose=False)

    def predict(self, image: np.ndarray) -> dict:
        start = time.time()
        # Inferencia
        results = self.model.predict(image, conf=0.5, verbose=False)
        end = time.time()

        # 1. Pintar las cajas en la imagen
        annotated_frame = results[0].plot()

        # 2. Codificar a JPG y luego a Base64 string
        # AQUÍ ES DONDE ESTABA FALLANDO:
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "boxes": results[0].boxes,
            "names": results[0].names,
            "inference_time": (end - start) * 1000,
            "annotated_image": img_base64
        }
    
    def predict_batch(self, images: list[np.ndarray]) -> list[dict]:
        start = time.time()
        # YOLO de ultralytics acepta una lista de numpy arrays directamente
        results = self.model.predict(images, conf=0.5, verbose=False)
        end = time.time()
        inference_time_per_img = ((end - start) * 1000) / len(images)

        output_list = []
        for res in results:
            # Post-proceso (Plotting) individual
            annotated_frame = res.plot()
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')

            output_list.append({
                "boxes": res.boxes,
                "names": res.names,
                "inference_time": inference_time_per_img, # Tiempo promedio por img en el lote
                "annotated_image": img_base64
            })
        
        return output_list