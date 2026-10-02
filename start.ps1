Write-Host "Starting MedAssist AI..."
Write-Host "Starting Backend..."
Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd backend && pip install -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Normal

Write-Host "Starting Frontend..."
Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd frontend && npm run dev" -WindowStyle Normal

Write-Host "Both services are starting in separate windows. Close those windows to stop the servers."
