from locust import HttpUser, task, between, events, constant
import os
import random
import json
import time

# --- CONFIGURACIÓN DE FPS (NUEVO) ---
# Leemos la variable de entorno. Si no existe, es 0 (Modo Estrés)
TARGET_FPS = float(os.getenv("TARGET_FPS", "0"))

# --- 1. CARGA PREVIA DE FRAMES ---
FRAMES_DIR = "frames_data"
VIDEO_FRAMES = []

if not os.path.exists(FRAMES_DIR):
    print(f"ERROR: No existe frames_data.")
    exit(1)

print(f"--> Cargando {len(os.listdir(FRAMES_DIR))} frames en memoria...")
files = sorted([f for f in os.listdir(FRAMES_DIR) if f.endswith(".jpg")])
for filename in files:
    with open(os.path.join(FRAMES_DIR, filename), "rb") as f:
        VIDEO_FRAMES.append(f.read())
print(f"--> ¡Listo! {len(VIDEO_FRAMES)} frames cargados.")

# --- LOGICA DE TIEMPO DE ESPERA ---
def get_wait_time():
    if TARGET_FPS > 0:
        # Si queremos 30 FPS, esperamos 1/30 segundos entre envíos
        # (Menos un pequeño margen para compensar la latencia de red)
        return constant(1 / TARGET_FPS)
    else:
        # Modo Estrés (Máxima velocidad)
        return between(0.0, 0.01)

class CameraUser(HttpUser):
    # Asignamos la función dinámica
    wait_time = get_wait_time()
    
    def on_start(self):
        self.frame_index = random.randint(0, len(VIDEO_FRAMES) - 1)
        # Imprimir modo solo una vez
        if self.frame_index == 0: 
            mode = f"🎥 SIMULACIÓN {TARGET_FPS} FPS" if TARGET_FPS > 0 else "🔥 ESTRÉS MÁXIMO"
            print(f"--- INICIANDO USUARIO EN MODO: {mode} ---")

    @task
    def stream_video(self):
        # ... (EL RESTO DEL CÓDIGO DE LA TAREA QUEDA IGUAL) ...
        image_data = VIDEO_FRAMES[self.frame_index]
        self.frame_index = (self.frame_index + 1) % len(VIDEO_FRAMES)
        files = {'file': ('frame.jpg', image_data, 'image/jpeg')}
        
        with self.client.post("/predict", files=files, catch_response=True, name="Inference") as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "inference_time_ms" in data:
                        events.request.fire(
                            request_type="Internal",
                            name="GPU_Inferencia_Pura",
                            response_time=data["inference_time_ms"],
                            response_length=len(response.content),
                        )
                        response.success()
                    else:
                        response.failure("JSON incompleto")
                except Exception as e:
                    response.failure(f"JSON Error: {e}")
            else:
                response.failure(f"HTTP {response.status_code}")