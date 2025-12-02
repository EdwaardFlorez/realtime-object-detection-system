# run_test.ps1

# --- CONFIGURACION ---
$NUM_WORKERS = 4
$TARGET_HOST = "http://20.163.66.100:8000"
$ROOT_PATH = Get-Location

# 1. DETECTAR MODO DE FPS
# Si la variable no existe, asumimos 0 (Estres Maximo)
$FPS_MODE = if ($env:TARGET_FPS) { $env:TARGET_FPS } else { "0" }

Write-Host "==========================================" -ForegroundColor Cyan
if ($FPS_MODE -eq "0") {
    Write-Host "[MODO] ESTRES MAXIMO (Sin espera)" -ForegroundColor Red
} else {
    Write-Host "[MODO] SIMULACION $FPS_MODE FPS (Tiempo Real)" -ForegroundColor Yellow
}
Write-Host "==========================================" -ForegroundColor Cyan
Start-Sleep -Seconds 2

# 2. LIMPIEZA
Write-Host "[PASO 1] Limpiando procesos anteriores..." -ForegroundColor Yellow
Stop-Process -Name "locust" -ErrorAction SilentlyContinue
Stop-Process -Name "python" -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# 3. INICIAR MAESTRO
Write-Host "[PASO 2] Iniciando Maestro..." -ForegroundColor Cyan
# El backtick (`) antes del $env es importante para que la variable se pase al nuevo proceso
$MasterCommand = "cd '$ROOT_PATH'; `$env:TARGET_FPS='$FPS_MODE'; .\venv\Scripts\Activate.ps1; locust -f locustfile.py --master --host $TARGET_HOST"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$MasterCommand"

# Esperar a que arranque
Start-Sleep -Seconds 4

# 4. INICIAR WORKERS
Write-Host "[PASO 3] Desplegando $NUM_WORKERS trabajadores..." -ForegroundColor Green

# Inyectamos el modo FPS en cada trabajador
$WorkerCommand = "cd '$ROOT_PATH'; `$env:TARGET_FPS='$FPS_MODE'; .\venv\Scripts\Activate.ps1; locust -f locustfile.py --worker"

for ($i=1; $i -le $NUM_WORKERS; $i++) {
    Write-Host "   + Lanzando Worker $i ($FPS_MODE FPS)..."
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "$WorkerCommand"
    Start-Sleep -Milliseconds 500 
}

Write-Host "`n[FIN] SISTEMA DE PRUEBAS ACTIVO" -ForegroundColor Green
Write-Host "URL: http://localhost:8089" -ForegroundColor White