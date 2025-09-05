# scripts\fix-env.ps1
$ErrorActionPreference = 'Stop'
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Chemin du projet (dossier racine backend)
$root = (Get-Item "$PSScriptRoot\..").FullName
Set-Location $root

$envFile = ".env"
if (-not (Test-Path $envFile)) { New-Item -ItemType File -Path $envFile | Out-Null }

Copy-Item $envFile "$envFile.bak" -Force

# Valeurs cibles cohérentes avec les noms de services docker
$dbUrl    = 'postgresql+psycopg2://lk:lkpass@lk-postgres:5432/luckykangaroo'
$redisBase= 'redis://lk-redis:6379'   # ⚠️ sans /db ici à cause de la concat dans config.py

$desired = [ordered]@{
  'FLASK_ENV'                 = 'production'
  'PYTHONUNBUFFERED'          = '1'

  'DATABASE_URL'              = $dbUrl
  'SQLALCHEMY_DATABASE_URI'   = $dbUrl

  # Base + DBs déportées (config.py fait f"{REDIS_URL}/{REDIS_*_DB}")
  'REDIS_URL'                 = $redisBase
  'REDIS_CACHE_DB'            = '1'
  'REDIS_QUEUE_DB'            = '2'
  'REDIS_SOCKETIO_DB'         = '3'

  # URLs directes pour les libs qui ne lisent pas tes *_DB
  'CACHE_REDIS_URL'           = "$redisBase/1"
  'CELERY_BROKER_URL'         = "$redisBase/2"
  'CELERY_RESULT_BACKEND'     = "$redisBase/2"
  'SOCKETIO_MESSAGE_QUEUE'    = "$redisBase/3"
  'RATELIMIT_STORAGE_URI'     = "$redisBase/3"

  # Alignement socketio/gunicorn
  'SOCKETIO_ASYNC_MODE'       = 'gevent'

  # Pour éviter l'erreur int('') sur le mail
  'MAIL_PORT'                 = '587'
}

# Remplacer/Ajouter proprement clé=valeur
$text = Get-Content $envFile -Raw
foreach ($k in $desired.Keys) {
  $v = $desired[$k]
  if ($text -match "(?m)^$([regex]::Escape($k))=") {
    $text = [regex]::Replace($text, "(?m)^$([regex]::Escape($k))=.*$", "$k=$v")
  } else {
    $text += "`n$k=$v"
  }
}

# Nettoyage des anciens hôtes erronés (redis/postgres nus)
$text = $text -replace '(?m)^(CACHE_REDIS_URL|RATELIMIT_STORAGE_URI|SOCKETIO_MESSAGE_QUEUE)\s*=\s*redis://redis:6379/\d+\s*$',''
$text = $text -replace '(?m)^(SQLALCHEMY_DATABASE_URI)\s*=\s*postgresql\+psycopg2://[^@\r\n]+@postgres:5432/[^\s\r\n]+$',''

# Trim lignes vides multiples
$text = ($text -split "`r?`n" | Where-Object { $_ -ne '' } | Select-Object -Unique) -join "`r`n"

Set-Content -Path $envFile -Value $text -Encoding UTF8
Write-Host "✅ .env mis à jour. Sauvegarde: $envFile.bak"
