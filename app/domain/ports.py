from abc import ABC, abstractmethod
import numpy as np
from .entities import PredictionResult

class ObjectDetectionModel(ABC):
    @abstractmethod
    def predict(self, image: np.ndarray) -> dict:
        """
        Debe retornar:
        {
            "boxes": list, # Lista de detecciones
            "names": list, # Nombres de clases
            "inference_time": float # Tiempo puro de inferencia
        }
        """
        pass