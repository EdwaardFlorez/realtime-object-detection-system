# Usamos PyTorch 2.4.0 con CUDA 12.4
FROM pytorch/pytorch:2.4.0-cuda12.4-cudnn9-runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Variable por defecto (se sobreescribe desde Terraform)
ENV WORKERS=1 

WORKDIR /workspace

# Instalar dependencias de sistema
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY . ./app

RUN pip install --no-cache-dir -r app/requirements.txt

RUN yolo export model=yolo11n.pt format=torchscript

EXPOSE 8000

# CAMBIO PROFESIONAL: Usamos la variable de entorno $WORKERS
# Nota: Usamos la forma 'Shell' (sin corchetes) para que expanda la variable
CMD uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers $WORKERS