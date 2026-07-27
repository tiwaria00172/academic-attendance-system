# PowerShell Script to Launch the Attendance System Live Locally or in Docker
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Launching Academic Attendance System Live Service" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Check if Docker is installed and running
$dockerRunning = $false
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        $dockerRunning = $true
    }
} catch {
    $dockerRunning = $false
}

if ($dockerRunning) {
    Write-Host "[+] Docker detected! Starting complete containerized production stack..." -ForegroundColor Green
    Write-Host "    Building and launching PostgreSQL, Backend API, and Nginx Frontend..." -ForegroundColor Yellow
    docker compose up -d --build
    Write-Host "==========================================================" -ForegroundColor Green
    Write-Host "🎉 System is LIVE in Docker!" -ForegroundColor Green
    Write-Host " -> Web Application: http://localhost" -ForegroundColor Cyan
    Write-Host " -> API Endpoint:    http://localhost/api/" -ForegroundColor Cyan
    Write-Host " -> Database:        PostgreSQL 15 (Containerized)" -ForegroundColor Cyan
    Write-Host "==========================================================" -ForegroundColor Green
} else {
    Write-Host "[!] Docker not detected or not running. Launching Local Live Servers..." -ForegroundColor Yellow
    
    # Start Backend API in background job
    Write-Host "[+] Starting Python Flask API Server on http://0.0.0.0:5000..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python run.py"
    
    # Start Frontend dev server in background job
    Write-Host "[+] Starting React Frontend UI Server on http://localhost:5173..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev -- --host"
    
    Write-Host "==========================================================" -ForegroundColor Green
    Write-Host "🎉 System is LIVE locally on your network!" -ForegroundColor Green
    Write-Host " -> Frontend Web UI: http://localhost:5173" -ForegroundColor Cyan
    Write-Host " -> Backend API:     http://localhost:5000" -ForegroundColor Cyan
    Write-Host "==========================================================" -ForegroundColor Green
}
