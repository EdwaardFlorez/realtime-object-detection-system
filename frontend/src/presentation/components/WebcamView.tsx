import { useRef, useEffect, useState } from 'react';
import { useRealTimeInference } from '../../application/useRealTimeInference';
import { Camera, Activity, Cpu } from 'lucide-react';

export const WebcamView = () => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const { result, processFrame, isProcessing } = useRealTimeInference();
    const [isStreamActive, setIsStreamActive] = useState(false);
    
    // --- NUEVO: Estado para FPS Reales ---
    const [realFps, setRealFps] = useState(0);
    const frameCountRef = useRef(0);

    // 1. Iniciar Cámara (Igual que antes)
    useEffect(() => {
        let stream: MediaStream | null = null;
        const startCamera = async () => {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { width: { ideal: 640 }, height: { ideal: 480 }, frameRate: { ideal: 30 } } 
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

    // --- NUEVO: Contador de FPS Reales ---
    // Cada vez que llega un resultado, sumamos 1 al contador
    useEffect(() => {
        if (result) {
            frameCountRef.current += 1;
        }
    }, [result]);

    // Cada 1 segundo, actualizamos el estado y reseteamos el contador
    useEffect(() => {
        const timer = setInterval(() => {
            setRealFps(frameCountRef.current);
            frameCountRef.current = 0;
        }, 1000);
        return () => clearInterval(timer);
    }, []);

    // 2. Bucle de Captura (MODIFICADO)
    useEffect(() => {
        const intervalId = setInterval(() => {
            // Si está procesando, NO mandamos otra (evita saturar la red)
            if (!isStreamActive || isProcessing || !videoRef.current || !canvasRef.current) return;
            
            const video = videoRef.current;
            const canvas = canvasRef.current;
            
            if (video.videoWidth > 0) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const ctx = canvas.getContext('2d');
                if (ctx) {
                    ctx.drawImage(video, 0, 0);
                    // Bajamos un poco la calidad del JPG para enviar menos datos (0.6) -> Más velocidad
                    canvas.toBlob(b => b && processFrame(b), 'image/jpeg', 0.6);
                }
            }
        }, 33); // <--- CAMBIO CLAVE: 33ms = ~30 FPS (Antes tenías 100ms = 10 FPS)
        
        return () => clearInterval(intervalId);
    }, [isStreamActive, isProcessing, processFrame]);

    // --- LAYOUT ---
    return (
        <div className="w-full h-full p-4 flex flex-col">
            <div className="flex flex-row gap-4 flex-1 min-h-0">
                
                {/* COLUMNA IZQUIERDA */}
                <div className="flex-1 flex flex-col min-w-0 bg-slate-800/50 rounded-xl border border-slate-700 p-2">
                    <h2 className="text-sm font-bold text-green-400 flex items-center gap-2 mb-2 uppercase tracking-wider">
                        <Camera className="w-4 h-4"/> Entrada: Tiempo Real
                    </h2>
                    <div className="relative flex-1 bg-black rounded-lg overflow-hidden w-full h-full">
                        <video ref={videoRef} autoPlay playsInline muted className="absolute inset-0 w-full h-full object-contain" />
                        <canvas ref={canvasRef} style={{ display: 'none' }} />
                        <div className="absolute top-3 left-3 flex items-center gap-2 bg-black/60 backdrop-blur px-2 py-1 rounded-md border border-green-500/30">
                            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse shadow-[0_0_10px_#22c55e]"></div>
                            <span className="text-[10px] font-bold text-green-100">LIVE</span>
                        </div>
                    </div>
                </div>

                {/* COLUMNA DERECHA */}
                <div className="flex-1 flex flex-col min-w-0 bg-slate-800/50 rounded-xl border border-slate-700 p-2">
                    <h2 className="text-sm font-bold text-blue-400 flex items-center gap-2 mb-2 uppercase tracking-wider">
                        <Activity className="w-4 h-4"/> Salida: Azure YOLOv11
                    </h2>
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
                                <p className="text-xs font-mono">Esperando Inferencia...</p>
                            </div>
                        )}

                        {result && (
                            <div className="absolute bottom-0 inset-x-0 bg-black/80 backdrop-blur-sm p-2 border-t border-blue-500/30 flex justify-around">
                                <div className="text-center">
                                    <p className="text-[10px] text-slate-400 uppercase">FPS REALES</p>
                                    {/* AQUI MOSTRAMOS LA VERDAD */}
                                    <p className="text-xl font-bold text-green-400">{realFps}</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-[10px] text-slate-400 uppercase">Latencia Total</p>
                                    <p className="text-sm font-bold text-yellow-400">{result.total_time_ms.toFixed(0)}ms</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-[10px] text-slate-400 uppercase">GPU Server</p>
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