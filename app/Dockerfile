# Usamos PyTorch 2.4.0 con CUDA 12.4
FROM pytorch/pytorch:2.4.0-cuda12.4-cudnn9-runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# CAMBIO 1: Trabajamos en una carpeta raíz neutra llamada '/workspace'
WORKDIR /workspace

# Instalar dependencias de sistema
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# CAMBIO 2: Copiamos el código DENTRO de una subcarpeta 'app'
# Esto recrea la estructura de paquete: /workspace/app/main.py
COPY . ./app

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r app/requirements.txt

# Descargar el modelo YOLO11n para evitar Cold Start de descarga
# Nota: El modelo se guardará dentro de /workspace (o donde yolo decida), pero está bien.
RUN yolo export model=yolo11n.pt format=torchscript

# Exponer puerto
EXPOSE 8000

# CAMBIO 3: Ejecutamos uvicorn apuntando al módulo 'app.main'
# Al estar en /workspace, Python ve 'app' como un paquete válido.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]