from dataclasses import dataclass
from typing import List, Optional

@dataclass
class PredictionResult:
    request_id: str
    inference_time_ms: float
    total_time_ms: float
    objects_detected: List[str]
    count: int
    annotated_image_base64: Optional[str] = None