from locust import HttpUser, task, between, events
import os
import random
import time
import json

# --- 1. CONFIGURACIÓN Y CARGA DE DATOS ---
FRAMES_DIR = "frames_data"
VIDEO_FRAMES = []

# Verificación de seguridad
if not os.path.exists(FRAMES_DIR):
    print(f"ERROR CRÍTICO: No se encuentra la carpeta '{FRAMES_DIR}'.")
    print("Ejecuta primero el script 'extract_frames.py'.")
    exit(1)

# Cargar imágenes en memoria (Limitamos a 50 para no saturar RAM)
#print("--> Cargando frames en memoria RAM...")
#files = sorted([f for f in os.listdir(FRAMES_DIR) if f.endswith(".jpg")])

# CÁMBIALO POR ESTO (Cargar TODO):
print(f"--> Cargando {len(os.listdir(FRAMES_DIR))} frames en memoria (aprox 113MB)...")
files = sorted([f for f in os.listdir(FRAMES_DIR) if f.endswith(".jpg")])

# Tomamos una muestra si hay muchos, o todos si son pocos
#frames_to_load = files[:50] 

for filename in files:
    file_path = os.path.join(FRAMES_DIR, filename)
    with open(file_path, "rb") as f:
        VIDEO_FRAMES.append(f.read())

print(f"--> ¡Listo! {len(VIDEO_FRAMES)} frames cargados. Iniciando prueba de carga.")

# --- 2. CLASE DE USUARIO (CÁMARA SIMULADA) ---
class CameraUser(HttpUser):
    # Tiempo de espera entre peticiones (simula los FPS de la cámara)
    # between(0.1, 0.5) significa que envía entre 2 y 10 fotos por segundo por usuario
    #wait_time = between(0.1, 0.5) 
    wait_time = between(0.0, 0.01)
    
    def on_start(self):
        # Cada "usuario" empieza en un frame aleatorio del video
        self.frame_index = random.randint(0, len(VIDEO_FRAMES) - 1)

    @task
    def stream_video(self):
        # 1. Preparar la imagen
        image_data = VIDEO_FRAMES[self.frame_index]
        self.frame_index = (self.frame_index + 1) % len(VIDEO_FRAMES)
        
        files = {'file': ('frame.jpg', image_data, 'image/jpeg')}
        
        # 2. Enviar petición POST
        # Usamos catch_response=True para validar nosotros mismos el JSON
        with self.client.post("/predict", files=files, catch_response=True, name="Total_Network_Time") as response:
            
            if response.status_code == 200:
                try:
                    # Parsear respuesta del Backend
                    data = response.json()
                    
                    # --- PUNTO CRÍTICO PARA LA TESIS ---
                    # Extraemos el tiempo que la GPU reportó (sin latencia de red)
                    if "inference_time_ms" in data:
                        server_inference_time = data["inference_time_ms"]
                        
                        # Inyectamos este dato como una métrica separada en Locust
                        # Aparecerá en la tabla bajo el nombre "GPU_Inferencia_Pura"
                        events.request.fire(
                            request_type="Internal",
                            name="GPU_Inferencia_Pura",
                            response_time=server_inference_time,
                            response_length=len(response.content),
                        )
                        
                        # Marcamos la petición HTTP como exitosa
                        response.success()
                    else:
                        response.failure("JSON válido pero falta campo 'inference_time_ms'")
                        
                except json.JSONDecodeError:
                    response.failure("Respuesta no es un JSON válido")
                except Exception as e:
                    response.failure(f"Error procesando datos: {str(e)}")
            else:
                # Si el servidor da error (500, 502, 504), registramos el fallo
                response.failure(f"Error HTTP {response.status_code}: {response.text[:100]}")