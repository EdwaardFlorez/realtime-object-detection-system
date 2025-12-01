# run_test.ps1

# --- CONFIGURACION ---
$NUM_WORKERS = 4
$TARGET_HOST = "http://20.163.66.100:8000"
# Captura la ruta absoluta actual para que las nuevas ventanas sepan donde ir
$ROOT_PATH = Get-Location

# 1. LIMPIEZA
Write-Host "[PASO 1] Limpiando procesos anteriores..." -ForegroundColor Yellow
Stop-Process -Name "locust" -ErrorAction SilentlyContinue
Stop-Process -Name "python" -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# 2. INICIAR MAESTRO
# Nota: Al estar dentro de 'tests', llamamos a 'locustfile.py' directamente
Write-Host "[PASO 2] Iniciando Maestro..." -ForegroundColor Cyan
$MasterCommand = "cd '$ROOT_PATH'; .\venv\Scripts\Activate.ps1; locust -f locustfile.py --master --host $TARGET_HOST"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$MasterCommand"

# Esperar a que arranque para que los workers no fallen al conectar
Start-Sleep -Seconds 4

# 3. INICIAR WORKERS (TRABAJADORES)
Write-Host "[PASO 3] Desplegando $NUM_WORKERS trabajadores..." -ForegroundColor Green

$WorkerCommand = "cd '$ROOT_PATH'; .\venv\Scripts\Activate.ps1; locust -f locustfile.py --worker"

for ($i=1; $i -le $NUM_WORKERS; $i++) {
    Write-Host "   + Lanzando Worker $i..."
    # Abrimos una ventana nueva para cada trabajador
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "$WorkerCommand"
    Start-Sleep -Milliseconds 500 
}

Write-Host "`n[FIN] SISTEMA DE PRUEBAS PARALELAS ACTIVO" -ForegroundColor Green
Write-Host "URL del Panel: http://localhost:8089" -ForegroundColor White
Write-Host "(Deberias ver 'Workers: 4' arriba a la derecha en la web)"