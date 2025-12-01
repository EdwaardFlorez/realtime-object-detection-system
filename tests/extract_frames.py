import os
import random
import base64
import json
import time
from locust import HttpUser, task, between, events

# --- 1. CARGA PREVIA DE FRAMES ---
FRAMES_DIR = "frames_data"
VIDEO_FRAMES = []

if not os.path.exists(FRAMES_DIR):
    print("ERROR: No existe frames_data. Ejecuta extract_frames.py")
    exit(1)

# Cargamos solo 50 frames para no saturar memoria RAM si son muchos
files = sorted([f for f in os.listdir(FRAMES_DIR) if f.endswith(".jpg")])[:50]
for filename in files:
    with open(os.path.join(FRAMES_DIR, filename), "rb") as f:
        VIDEO_FRAMES.append(f.read())

print(f"--> {len(VIDEO_FRAMES)} frames cargados en RAM para la prueba.")

class CameraUser(HttpUser):
    # Simula una cámara enviando video (aprox 15-30 FPS si no hubiera latencia de red)
    # Ajustamos 'wait_time' para no ahogar tu propia red de subida
    wait_time = between(0.1, 0.5) 
    
    def on_start(self):
        self.frame_index = random.randint(0, len(VIDEO_FRAMES) - 1)

    @task
    def stream_video(self):
        image_data = VIDEO_FRAMES[self.frame_index]
        self.frame_index = (self.frame_index + 1) % len(VIDEO_FRAMES)

        files = {'file': ('live_feed.jpg', image_data, 'image/jpeg')}
        
        # Medimos tiempo total desde el cliente
        start_time = time.time()
        
        with self.client.post("/predict", files=files, catch_response=True, name="YOLO Inference") as response:
            total_time_ms = (time.time() - start_time) * 1000

            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # --- METRICA CLAVE PARA TU TESIS ---
                    # Extraemos el tiempo REAL de la GPU (Inferencia Pura)
                    if "inference_time_ms" in data:
                        server_inference_time = data["inference_time_ms"]
                        
                        # Reportamos a Locust el tiempo de GPU como una métrica personalizada
                        events.request.fire(
                            request_type="GPU_Core",
                            name="Inferencia Pura (Sin Red)",
                            response_time=server_inference_time,
                            response_length=len(response.content),
                        )
                        
                        # Validamos éxito
                        response.success()
                    else:
                        response.failure("JSON sin inference_time_ms")
                        
                except Exception as e:
                    response.failure(f"JSON Error: {e}")
            else:
                response.failure(f"Status {response.status_code}: {response.text}")