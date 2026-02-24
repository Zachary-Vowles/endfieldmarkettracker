# setup.ps1 - GPU Optimized Setup
Write-Host "Setting up Endfield Market Tracker with GPU Support..." -ForegroundColor Green

# Create virtual environment
if (Test-Path "venv") {
    Write-Host "Refreshing virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "venv"
}
python -m venv venv
.\venv\Scripts\Activate.ps1

Write-Host "Installing GPU-accelerated PyTorch (CUDA 12.1)..." -ForegroundColor Cyan
# This is the "secret sauce" for your 3070 Ti
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

Write-Host "Installing remaining dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host "Setup complete! Your RTX 3070 Ti is ready to hunt prices." -ForegroundColor Green