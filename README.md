# Cost-Efficient Cloud Architecture for Deep Learning Inference

## Abstract
This project evaluates and implements a serverless architecture for real-time object detection using **YOLO11** and **Azure**. The goal is to optimize the trade-off between inference latency, cost, and accuracy in cloud environments.

## Tech Stack
* **Core Model:** YOLO11 (Ultralytics)
* **Runtime:** PyTorch 2.4 + CUDA 12.4
* **API:** FastAPI (Async/Await)
* **Cloud:** Azure Container Instances & Blob Storage
* **IaC:** Terraform

## Project Structure
```text
├── app/                 # Application code (YOLO + API)
├── infra/               # Infrastructure as Code (Terraform)
└── tests/               # Load testing scripts
```

## Setup
1. Install dependencies: `pip install -r app/requirements.txt`
2. Run locally: `uvicorn app.main:app --reload`

## Author
Systems Engineering Thesis - 2025
