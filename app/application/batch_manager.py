import asyncio
import time
import logging
import numpy as np
from app.domain.ports import ObjectDetectionModel

logger = logging.getLogger("batch-manager")

class BatchInferenceManager:
    def __init__(self, model: ObjectDetectionModel, max_batch_size: int = 8, max_wait_time_s: float = 0.01):
        self.model = model
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time_s
        self.queue = asyncio.Queue()
        self.is_running = False
        # Iniciamos el worker en background
        asyncio.create_task(self.process_batches())

    async def predict(self, image: np.ndarray):
        # 1. Crear un "Future" (una promesa de respuesta)
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        
        # 2. Poner la imagen y su promesa en la cola
        await self.queue.put((image, future))
        
        # 3. Esperar a que el worker procese el lote y resuelva la promesa
        return await future

    async def process_batches(self):
        self.is_running = True
        logger.info(f"🔥 Adaptive Batching Iniciado (Size: {self.max_batch_size}, Wait: {self.max_wait_time}s)")
        
        while self.is_running:
            batch_images = []
            batch_futures = []
            
            # A. Recoger el primer elemento (bloqueante)
            # Si no hay nada, espera aquí y no gasta CPU
            img, fut = await self.queue.get()
            batch_images.append(img)
            batch_futures.append(fut)

            # B. Intentar llenar el resto del batch (con timeout)
            start_wait = time.time()
            while len(batch_images) < self.max_batch_size:
                # Calculamos cuánto tiempo nos queda de espera
                time_left = self.max_wait_time - (time.time() - start_wait)
                
                if time_left <= 0:
                    break # Se acabó el tiempo, procesamos lo que hay

                try:
                    # Intentamos sacar otro item de la cola sin bloquear eternamente
                    # wait_for lanza TimeoutError si se acaba el tiempo
                    img_next, fut_next = await asyncio.wait_for(self.queue.get(), timeout=time_left)
                    batch_images.append(img_next)
                    batch_futures.append(fut_next)
                except asyncio.TimeoutError:
                    break # Nadie más llegó a la fiesta
            
            # C. Procesar el Lote (Aquí ocurre la magia de eficiencia)
            if batch_images:
                try:
                    # NOTA: YOLO soporta inferencia por lista de imágenes
                    # Esto corre en C++ optimizado en la GPU
                    results = self.model.predict_batch(batch_images) 
                    
                    # D. Entregar resultados a cada dueño
                    for i, result_dict in enumerate(results):
                        if not batch_futures[i].done():
                            batch_futures[i].set_result(result_dict)
                            
                except Exception as e:
                    logger.error(f"Error en batch: {e}")
                    for fut in batch_futures:
                        if not fut.done():
                            fut.set_exception(e)