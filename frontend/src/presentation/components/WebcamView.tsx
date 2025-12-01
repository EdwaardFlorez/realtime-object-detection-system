import { useRef, useEffect, useState } from 'react';
import { useRealTimeInference } from '../../application/useRealTimeInference';
import { Camera, Activity, Cpu } from 'lucide-react';

export const WebcamView = () => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const { result, processFrame, isProcessing } = useRealTimeInference();
    const [isStreamActive, setIsStreamActive] = useState(false);

    // 1. Iniciar Cámara
    useEffect(() => {
        let stream: MediaStream | null = null;
        const startCamera = async () => {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { width: { ideal: 640 }, height: { ideal: 480 } } 
                });
                
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                    videoRef.current.onloadedmetadata = () => {
                        videoRef.current?.play();
                        setIsStreamActive(true);
                    };
                }
            } catch (err) {
                console.error("Error cámara:", err);
            }
        };
        startCamera();
        return () => { if (stream) stream.getTracks().forEach(t => t.stop()); };
    }, []);

    // 2. Bucle de Captura
    useEffect(() => {
        const intervalId = setInterval(() => {
            if (!isStreamActive || isProcessing || !videoRef.current || !canvasRef.current) return;
            const video = videoRef.current;
            const canvas = canvasRef.current;
            if (video.videoWidth > 0) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const ctx = canvas.getContext('2d');
                if (ctx) {
                    ctx.drawImage(video, 0, 0);
                    canvas.toBlob(b => b && processFrame(b), 'image/jpeg', 0.7);
                }
            }
        }, 100); 
        return () => clearInterval(intervalId);
    }, [isStreamActive, isProcessing, processFrame]);

    // --- LAYOUT FORZADO HORIZONTAL ---
    return (
        // Contenedor principal que ocupa todo el espacio disponible
        <div className="w-full h-full p-4 flex flex-col">
            
            {/* Fila Flex: Forzamos dirección de fila (row) y gap */}
            <div className="flex flex-row gap-4 flex-1 min-h-0">
                
                {/* ========================== */}
                {/* COLUMNA IZQUIERDA (50%)    */}
                {/* ========================== */}
                <div className="flex-1 flex flex-col min-w-0 bg-slate-800/50 rounded-xl border border-slate-700 p-2">
                    <h2 className="text-sm font-bold text-green-400 flex items-center gap-2 mb-2 uppercase tracking-wider">
                        <Camera className="w-4 h-4"/> Entrada: Tiempo Real
                    </h2>
                    
                    {/* Contenedor relativo para el video absoluto */}
                    <div className="relative flex-1 bg-black rounded-lg overflow-hidden w-full h-full">
                        <video 
                            ref={videoRef} 
                            autoPlay playsInline muted 
                            className="absolute inset-0 w-full h-full object-contain" 
                        />
                        
                        {/* Canvas Oculto */}
                        <canvas ref={canvasRef} style={{ display: 'none' }} />

                        <div className="absolute top-3 left-3 flex items-center gap-2 bg-black/60 backdrop-blur px-2 py-1 rounded-md border border-green-500/30">
                            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse shadow-[0_0_10px_#22c55e]"></div>
                            <span className="text-[10px] font-bold text-green-100">LIVE</span>
                        </div>
                    </div>
                </div>

                {/* ========================== */}
                {/* COLUMNA DERECHA (50%)      */}
                {/* ========================== */}
                <div className="flex-1 flex flex-col min-w-0 bg-slate-800/50 rounded-xl border border-slate-700 p-2">
                    <h2 className="text-sm font-bold text-blue-400 flex items-center gap-2 mb-2 uppercase tracking-wider">
                        <Activity className="w-4 h-4"/> Salida: Azure YOLOv11
                    </h2>

                    {/* Contenedor relativo */}
                    <div className="relative flex-1 bg-black rounded-lg overflow-hidden w-full h-full flex items-center justify-center">
                        {result?.annotated_image_base64 ? (
                            <img 
                                src={`data:image/jpeg;base64,${result.annotated_image_base64}`} 
                                className="absolute inset-0 w-full h-full object-contain"
                                alt="Detección"
                            />
                        ) : (
                            <div className="flex flex-col items-center text-slate-600">
                                <Cpu className="w-10 h-10 mb-2 opacity-30 animate-bounce"/>
                                <p className="text-xs font-mono">Conectando a GPU...</p>
                            </div>
                        )}

                        {/* HUD Métricas */}
                        {result && (
                            <div className="absolute bottom-0 inset-x-0 bg-black/80 backdrop-blur-sm p-2 border-t border-blue-500/30 flex justify-around">
                                <div className="text-center">
                                    <p className="text-[10px] text-slate-400 uppercase">FPS</p>
                                    <p className="text-sm font-bold text-green-400">{(1000 / result.total_time_ms).toFixed(1)}</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-[10px] text-slate-400 uppercase">Latencia</p>
                                    <p className="text-sm font-bold text-yellow-400">{result.total_time_ms.toFixed(0)}ms</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-[10px] text-slate-400 uppercase">Inferencia</p>
                                    <p className="text-sm font-bold text-blue-400">{result.inference_time_ms.toFixed(0)}ms</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-[10px] text-slate-400 uppercase">Objetos</p>
                                    <p className="text-sm font-bold text-white">{result.count}</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
};