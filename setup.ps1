# setup.ps1 - GPU Optimized Setup (Idempotent)
Write-Host "Setting up Endfield Market Tracker with GPU Support..." -ForegroundColor Green

# Create virtual environment only if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating new virtual environment..." -ForegroundColor Yellow
    python -m venv venv
} else {
    Write-Host "Using existing virtual environment..." -ForegroundColor Green
}

.\venv\Scripts\Activate.ps1

# Check if PyTorch with CUDA is already installed
$torchCheck = python -c "import torch; print(torch.cuda.is_available())" 2>$null
if ($LASTEXITCODE -ne 0 -or $torchCheck -ne "True") {
    Write-Host "Installing/Updating GPU-accelerated PyTorch (CUDA 12.1)..." -ForegroundColor Cyan
    pip install --upgrade torch torchvision --index-url https://download.pytorch.org/whl/cu121
} else {
    Write-Host "GPU-accelerated PyTorch already installed." -ForegroundColor Green
}

Write-Host "Installing/updating dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host "Setup complete! Your RTX 3070 Ti is ready to hunt prices." -ForegroundColor Green