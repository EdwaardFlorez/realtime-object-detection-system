import type { PredictionResponse } from '../domain/models';

export class WebSocketRepository {
    private ws: WebSocket | null = null;
    private isConnected = false;
    private messageQueue: ((data: PredictionResponse) => void)[] = [];
    
    constructor(url: string) {
        // Convertir http/https a ws/wss
        const wsUrl = url.replace("http", "ws") + "/ws/predict";
        console.log("🔌 Conectando WS:", wsUrl);
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log("✅ WS Conectado");
            this.isConnected = true;
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data) as PredictionResponse;
            // Resolver la promesa pendiente más antigua
            const resolver = this.messageQueue.shift();
            if (resolver) resolver(data);
        };

        this.ws.onclose = () => {
            this.isConnected = false;
            console.log("❌ WS Desconectado");
        };
    }

    // Mantenemos la misma interfaz: enviar -> esperar respuesta
    async predict(imageBlob: Blob): Promise<PredictionResponse> {
        if (!this.ws || !this.isConnected) {
            throw new Error("WebSocket no conectado");
        }

        // Enviar bytes
        this.ws.send(imageBlob);

        // Crear una promesa que se resolverá cuando llegue el mensaje de vuelta (onmessage)
        return new Promise<PredictionResponse>((resolve) => {
            this.messageQueue.push(resolve);
        });
    }
}