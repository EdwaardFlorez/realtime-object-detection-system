import { useState, useRef, useCallback } from 'react';
import { apiRepository } from '../infrastructure/api-repository';
import type { PredictionResponse } from '../domain/models';

export const useRealTimeInference = () => {
    const [result, setResult] = useState<PredictionResponse | null>(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState<string | null>(null);
    
    // Usamos una referencia para evitar condiciones de carrera en el bucle
    const processingRef = useRef(false);

    const processFrame = useCallback(async (imageBlob: Blob) => {
        // Si ya hay una foto viajando a la API, no mandamos otra (Control de congestión)
        if (processingRef.current) return;

        try {
            processingRef.current = true;
            setIsProcessing(true);
            
            // Llamada a la infraestructura
            const data = await apiRepository.predict(imageBlob);
            
            setResult(data);
            setError(null);
        } catch (err) {
            console.error(err);
            setError("Error de conexión con el modelo");
        } finally {
            processingRef.current = false;
            setIsProcessing(false);
        }
    }, []);

    return { result, isProcessing, error, processFrame };
};