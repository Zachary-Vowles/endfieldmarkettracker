# setup.ps1 - Run this to set up a clean environment

Write-Host "Setting up Endfield Market Tracker..." -ForegroundColor Green

# Check if Python 3.11 is installed
$pythonVersion = python --version 2>&1
if ($pythonVersion -notmatch "3.11") {
    Write-Error "Python 3.11 is required. Found: $pythonVersion"
    exit 1
}

# Create virtual environment
if (Test-Path "venv") {
    Write-Host "Removing old virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "venv"
}

Write-Host "Creating virtual environment..." -ForegroundColor Cyan
python -m venv venv

# Activate and install dependencies
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1

Write-Host "Installing dependencies (this may take a few minutes)..." -ForegroundColor Cyan

# Install NumPy 1.x first to avoid conflicts
pip install numpy==1.26.4

# Install PyTorch CPU version (smaller, no CUDA needed)
pip install torch==2.3.0+cpu torchvision==0.18.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Install remaining requirements
pip install PyQt6>=6.4.0
pip install mss>=9.0.0
pip install opencv-python>=4.8.0
pip install Pillow>=10.0.0
pip install easyocr>=1.7.0
pip install SQLAlchemy>=2.0.0
pip install pyqtgraph>=0.13.0
pip install python-dateutil>=2.8.0
pip install pydantic>=2.0.0
pip install loguru>=0.7.0
pip install appdirs>=1.4.4

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "To run the application:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python src/main.py" -ForegroundColor White