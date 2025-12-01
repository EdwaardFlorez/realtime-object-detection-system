import axios from 'axios';
import type { PredictionResponse } from '../domain/models';
import type { InferenceRepository } from '../domain/repository';

const API_URL = import.meta.env.VITE_API_URL || "http://20.163.66.100:8000";
console.log("🔗 Conectando a API:", API_URL);

export const apiRepository: InferenceRepository = {
    predict: async (imageBlob: Blob): Promise<PredictionResponse> => {
        const formData = new FormData();
        formData.append('file', imageBlob, "frame.jpg");

        const response = await axios.post<PredictionResponse>(
            `${API_URL}/predict`, 
            formData,
            { headers: { 'Content-Type': 'multipart/form-data' } }
        );

        return response.data;
    }
};