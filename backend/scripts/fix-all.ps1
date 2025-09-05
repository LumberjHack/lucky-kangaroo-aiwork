# scripts\fix-all.ps1
$ErrorActionPreference = 'Stop'
Write-Host "Working dir: $((Get-Location).Path)"

# --- 1) Requirements : psycopg2-binary + gevent ---
$req = ".\requirements.txt"
if (-not (Test-Path $req)) { throw "requirements.txt introuvable" }

function Ensure-LineInFile([string]$Path, [string]$Pattern, [string]$LineToAdd) {
    $lines = @(); if (Test-Path $Path) { $lines = Get-Content $Path }
    $found = $false
    foreach ($l in $lines) { if ($l -match $Pattern) { $found = $true; break } }
    if (-not $found) { Add-Content -Path $Path -Value $LineToAdd; Write-Host " + $LineToAdd -> $Path" }
    else { Write-Host " = déjà présent -> $LineToAdd" }
}
Ensure-LineInFile $req '^\s*psycopg2-binary' 'psycopg2-binary==2.9.9'
Ensure-LineInFile $req '^\s*gevent(\b|==)' 'gevent==24.2.1'

# --- 2) .env : clés minimales pour booter sans erreur ---
$envPath = ".\.env"
if (-not (Test-Path $envPath)) { Set-Content -Path $envPath -Value "" -Encoding UTF8 }

function Set-EnvKV([string]$Key, [string]$Val) {
    $lines = @(); if (Test-Path $envPath) { $lines = Get-Content $envPath }
    $done = $false; $new = @()
    foreach ($l in $lines) {
        if ($l -match "^\s*$Key\s*=") { $new += "$Key=$Val"; $done = $true }
        else { $new += $l }
    }
    if (-not $done) { $new += "$Key=$Val" }
    Set-Content $envPath $new -Encoding UTF8
    Write-Host " .env: $Key set"
}
$db = "postgresql+psycopg2://lk:lkpass@lk-postgres:5432/luckykangaroo"
Set-EnvKV "DATABASE_URL" $db
Set-EnvKV "SQLALCHEMY_DATABASE_URI" $db
Set-EnvKV "REDIS_URL" "redis://lk-redis:6379/0"
Set-EnvKV "CELERY_BROKER_URL" "redis://lk-redis:6379/2"
Set-EnvKV "CELERY_RESULT_BACKEND" "redis://lk-redis:6379/2"
Set-EnvKV "MAIL_SERVER" "localhost"
Set-EnvKV "MAIL_PORT" "587"
Set-EnvKV "FLASK_ENV" "production"
Set-EnvKV "JWT_SECRET_KEY" "change_me"
Set-EnvKV "UPLOAD_FOLDER" "./uploads"

# --- 3) Avertissement sockets: supprimer les imports relatifs de sockets.py (non bloquant) ---
$targets = @(".\sockets.py", ".\backend\sockets.py") | Where-Object { Test-Path $_ }
foreach ($t in $targets) {
    $txt = Get-Content $t -Raw
    $patched = [regex]::Replace($txt, 'from\s+\.\s*([A-Za-z_][A-Za-z0-9_\.]*)\s+import', 'from $1 import')
    if ($patched -ne $txt) {
        Set-Content $t $patched -Encoding UTF8
        Write-Host "Patched relative imports in $t"
    }
}

# --- 4) Docker rebuild & up ---
Write-Host "`n--- Docker rebuild ---`n"
docker compose down
docker compose build --no-cache
docker compose up
