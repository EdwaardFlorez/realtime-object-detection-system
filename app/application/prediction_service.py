import time
import uuid
import numpy as np
from app.domain.ports import ObjectDetectionModel
from app.domain.entities import PredictionResult

class PredictionService:
    def __init__(self, model: ObjectDetectionModel):
        self.model = model

    def execute_prediction(self, image: np.ndarray) -> PredictionResult:
        req_start = time.time()
        req_id = str(uuid.uuid4())

        # Llama al puerto (interfaz), no sabe que es YOLO
        model_output = self.model.predict(image)
        
        total_time = (time.time() - req_start) * 1000
        
        # Mapeo de resultados
        detected_classes = [
            model_output["names"][int(c)] 
            for c in model_output["boxes"].cls
        ]

        return PredictionResult(
            request_id=req_id,
            inference_time_ms=round(model_output["inference_time"], 2),
            total_time_ms=round(total_time, 2),
            objects_detected=detected_classes,
            count=len(detected_classes),
            annotated_image_base64=model_output["annotated_image"] # Pasamos la imagen
        )