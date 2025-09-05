# Lucky Kangaroo - Script de tests
# Exécute tous les tests de l'application

param(
    [string]$TestType = "all",
    [string]$Coverage = "false",
    [string]$Verbose = "false",
    [string]$Parallel = "false"
)

Write-Host "🚀 Lucky Kangaroo - Lancement des tests..." -ForegroundColor Green

# Vérifier que Python est installé
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python détecté: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python n'est pas installé ou n'est pas dans le PATH" -ForegroundColor Red
    exit 1
}

# Vérifier que pytest est installé
try {
    $pytestVersion = pytest --version 2>&1
    Write-Host "✅ pytest détecté: $pytestVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ pytest n'est pas installé. Installation..." -ForegroundColor Yellow
    pip install -r requirements-test.txt
}

# Activer l'environnement virtuel si il existe
if (Test-Path "backend/venv/Scripts/Activate.ps1") {
    Write-Host "🔧 Activation de l'environnement virtuel..." -ForegroundColor Blue
    & "backend/venv/Scripts/Activate.ps1"
}

# Construire la commande pytest
$pytestCmd = "pytest"

# Ajouter les options selon les paramètres
if ($TestType -eq "unit") {
    $pytestCmd += " -m unit"
} elseif ($TestType -eq "integration") {
    $pytestCmd += " -m integration"
} elseif ($TestType -eq "api") {
    $pytestCmd += " -m api"
} elseif ($TestType -eq "database") {
    $pytestCmd += " -m database"
}

if ($Coverage -eq "true") {
    $pytestCmd += " --cov=backend --cov-report=html --cov-report=term-missing"
}

if ($Verbose -eq "true") {
    $pytestCmd += " -v -s"
}

if ($Parallel -eq "true") {
    $pytestCmd += " -n auto"
}

# Ajouter des options communes
$pytestCmd += " --tb=short --color=yes --durations=10"

Write-Host "📋 Commande: $pytestCmd" -ForegroundColor Cyan
Write-Host ""

# Exécuter les tests
try {
    Invoke-Expression $pytestCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 Tous les tests ont réussi!" -ForegroundColor Green
        
        if ($Coverage -eq "true") {
            Write-Host "📊 Rapport de couverture généré dans htmlcov/" -ForegroundColor Blue
        }
    } else {
        Write-Host ""
        Write-Host "❌ Certains tests ont échoué" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} catch {
    Write-Host "❌ Erreur lors de l'exécution des tests: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✨ Tests terminés!" -ForegroundColor Green
