# Clinical Guideline Research Assistant - Quick Start Script

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Clinical Guideline Research Assistant" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-Not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Created .env - Please edit and add your API keys!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Opening .env file for editing..." -ForegroundColor Yellow
    Start-Process notepad.exe ".env"
    Read-Host "Press Enter after you've added your API keys to continue"
}

# Start Docker infrastructure
Write-Host "Starting infrastructure services..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "Waiting for services to be ready (60 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# Install Python dependencies
Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Initialize databases
Write-Host ""
Write-Host "Initializing databases..." -ForegroundColor Yellow
python scripts/init_db.py

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Open a new terminal and run: python scripts/start_worker.py" -ForegroundColor White
Write-Host "2. Open another terminal and run: uvicorn api.main:app --reload --port 8000" -ForegroundColor White
Write-Host "3. Visit http://localhost:8000/docs for API documentation" -ForegroundColor White
Write-Host ""
Write-Host "Monitoring URLs:" -ForegroundColor Cyan
Write-Host "- API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "- Temporal UI: http://localhost:8088" -ForegroundColor White
Write-Host "- Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host "- Jaeger: http://localhost:16686" -ForegroundColor White
Write-Host ""
