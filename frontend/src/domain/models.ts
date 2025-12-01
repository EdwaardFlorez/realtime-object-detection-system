export interface PredictionResponse {
    request_id: string;
    count: number;
    inference_time_ms: number;
    total_time_ms: number;
    objects_detected: string[];
    annotated_image_base64: string; // Base64
}