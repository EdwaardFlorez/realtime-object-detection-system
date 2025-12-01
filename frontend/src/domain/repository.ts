import type { PredictionResponse } from "./models";

export interface InferenceRepository {
    predict(imageBlob: Blob): Promise<PredictionResponse>;
}