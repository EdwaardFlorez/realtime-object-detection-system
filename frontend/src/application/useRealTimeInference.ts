import { useState, useEffect, useRef, useCallback } from 'react';
import { apiRepository } from '../infrastructure/api-repository';
import type { PredictionResponse } from '../domain/models';
import { WebSocketRepository } from '../infrastructure/ws-repository';



const API_URL = import.meta.env.VITE_API_URL || "http://20.163.66.100:8000";

export const useRealTimeInference = () => {
    const [result, setResult] = useState<unknown>(null);
    const wsRepoRef = useRef<WebSocketRepository | null>(null);

    // Inicializar conexión WS una sola vez
    useEffect(() => {
        wsRepoRef.current = new WebSocketRepository(API_URL);
        return () => {
            // Lógica de limpieza si fuera necesaria
        };
    }, []);

    const processFrame = useCallback(async (imageBlob: Blob) => {
        if (!wsRepoRef.current) return;
        
        try {
            // Ahora esto viaja por el tubo abierto, no abre conexión nueva
            const data = await wsRepoRef.current.predict(imageBlob);
            setResult(data);
        } catch (err) {
            console.error("Error frame:", err);
        }
    }, []);

    return { result, processFrame };
};

export const useRealTimeInference2 = () => {
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