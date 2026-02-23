# run.ps1 - Run this to start the application

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Error "Virtual environment not found. Run setup.ps1 first."
    exit 1
}

# Activate and run
.\venv\Scripts\Activate.ps1
python src/main.py