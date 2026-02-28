# PMIR Brain Spectral Universality - Repository Setup Script
# Run this from within brain-spectral-universality folder
# Right-click > "Run with PowerShell" OR open PowerShell and run: .\SETUP_REPO_STRUCTURE.ps1

$repo = "C:\Users\veilbreaker\Downloads\brain-spectral-universality"
$paper01src = "C:\Users\veilbreaker\Downloads\PMIR_neurology\PMIR_EEG_Paper"
$paper02src = "C:\Users\veilbreaker\PMIR_Research\paper1_brain_universality"

Write-Host "Starting PMIR repository restructure..." -ForegroundColor Cyan

# ============================================================
# PAPER 01 - EEG Spectral Universality
# ============================================================
Write-Host "`n[Paper 01] Copying manuscript files..." -ForegroundColor Yellow
Copy-Item "$paper01src\08_Final_Submission\*" "$repo\paper01_eeg\manuscript\" -Recurse -Force

Write-Host "[Paper 01] Copying analysis scripts..." -ForegroundColor Yellow
Copy-Item "$paper01src\02_Analysis_Scripts\*" "$repo\paper01_eeg\code\" -Recurse -Force

Write-Host "[Paper 01] Copying raw EDF data..." -ForegroundColor Yellow
Copy-Item "$paper01src\01_RawData\*" "$repo\paper01_eeg\data\raw\" -Recurse -Force

Write-Host "[Paper 01] Copying results..." -ForegroundColor Yellow
Copy-Item "$paper01src\03_Results\*" "$repo\paper01_eeg\data\results\" -Recurse -Force

Write-Host "[Paper 01] Copying figures..." -ForegroundColor Yellow
Copy-Item "$paper01src\04_Figures\*" "$repo\paper01_eeg\figures\" -Recurse -Force

Write-Host "[Paper 01] Copying supplementary tables..." -ForegroundColor Yellow
Copy-Item "$paper01src\07_Supplementary_Tables\*" "$repo\paper01_eeg\tables\" -Recurse -Force

# ============================================================
# PAPER 02 - ABIDE Multi-Site Universality
# ============================================================
Write-Host "`n[Paper 02] Copying manuscript files..." -ForegroundColor Yellow
Copy-Item "$paper02src\manuscript\*" "$repo\paper02_abide\manuscript\" -Recurse -Force

Write-Host "[Paper 02] Copying pipeline code..." -ForegroundColor Yellow
Copy-Item "$paper02src\pipeline\*" "$repo\paper02_abide\code\" -Recurse -Force

Write-Host "[Paper 02] Copying data..." -ForegroundColor Yellow
Copy-Item "$paper02src\data\*" "$repo\paper02_abide\data\" -Recurse -Force

Write-Host "[Paper 02] Copying figures..." -ForegroundColor Yellow
Copy-Item "$paper02src\figures\*" "$repo\paper02_abide\figures\" -Recurse -Force

Write-Host "[Paper 02] Copying results..." -ForegroundColor Yellow
Copy-Item "$paper02src\results\*" "$repo\paper02_abide\results\" -Recurse -Force

Write-Host "`nAll files copied successfully!" -ForegroundColor Green
Write-Host "`nNext step: open a terminal in the repo folder and run:" -ForegroundColor Cyan
Write-Host "  git add ." -ForegroundColor White
Write-Host "  git commit -m 'Restructure repo: paper01_eeg + paper02_abide clean layout'" -ForegroundColor White
Write-Host "  git push" -ForegroundColor White
