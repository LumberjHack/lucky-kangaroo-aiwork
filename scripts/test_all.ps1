param(
  [string]$BaseUrl = "http://localhost:5006"
)

Write-Host "Lucky Kangaroo - Test complet" -ForegroundColor Cyan

# Force UTF-8 output to avoid garbled characters on Windows consoles
try {
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  $OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}

# Helper: Multipart POST compatible PowerShell 5.1 (no -Form, no curl)
function Invoke-MultipartFormData {
  param(
    [Parameter(Mandatory=$true)][string]$Uri,
    [hashtable]$Files,
    [hashtable]$Fields,
    [hashtable]$Headers
  )
  Add-Type -AssemblyName System.Net.Http | Out-Null
  $handler = New-Object System.Net.Http.HttpClientHandler
  $client  = New-Object System.Net.Http.HttpClient($handler)
  try {
    if ($Headers) { foreach ($k in $Headers.Keys) { $client.DefaultRequestHeaders.Remove($k) | Out-Null; $client.DefaultRequestHeaders.Add($k, [string]$Headers[$k]) } }
    $content = New-Object System.Net.Http.MultipartFormDataContent
    if ($Fields) {
      foreach ($k in $Fields.Keys) {
        $sc = New-Object System.Net.Http.StringContent([string]$Fields[$k], [Text.Encoding]::UTF8)
        $cd = New-Object System.Net.Http.Headers.ContentDispositionHeaderValue("form-data")
        $cd.Name = '"' + $k + '"'
        $sc.Headers.ContentDisposition = $cd
        $content.Add($sc)
      }
    }
    if ($Files) {
      foreach ($k in $Files.Keys) {
        $path = [string]$Files[$k]
        $fs = [System.IO.File]::OpenRead($path)
        $fc = New-Object System.Net.Http.StreamContent($fs)
        $fc.Headers.ContentType = [System.Net.Http.Headers.MediaTypeHeaderValue]::Parse("application/octet-stream")
        $cd = New-Object System.Net.Http.Headers.ContentDispositionHeaderValue("form-data")
        $cd.Name = '"' + $k + '"'
        $cd.FileName = '"' + (Split-Path $path -Leaf) + '"'
        $fc.Headers.ContentDisposition = $cd
        $content.Add($fc)
      }
    }
    $resp = $client.PostAsync($Uri, $content).Result
    $raw  = $resp.Content.ReadAsStringAsync().Result
    if (-not $resp.IsSuccessStatusCode) { throw "HTTP $($resp.StatusCode): $raw" }
    return $raw | ConvertFrom-Json
  }
  finally {
    if ($content) { $content.Dispose() }
    if ($client)  { $client.Dispose() }
  }
}

# Health
Invoke-RestMethod -Uri "$BaseUrl/api/health" -Method Get | ConvertTo-Json -Depth 6

# Demo login
$loginBody = @{ email = "alice@example.com"; password = "password123" } | ConvertTo-Json
$loginResp = Invoke-RestMethod -Uri "$BaseUrl/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
$TOKEN = $loginResp.token
$headers = @{ Authorization = "Bearer $TOKEN" }

# Listings
$listings = Invoke-RestMethod -Uri "$BaseUrl/api/listings" -Method Get -Headers $headers
$listings | ConvertTo-Json -Depth 6

# AI analyze/lookup quick test (download sample image)
$Tmp = Join-Path $env:TEMP "lk_fulltest"; New-Item -ItemType Directory -Force -Path $Tmp | Out-Null
$img = Join-Path $Tmp "sample.jpg"
Invoke-WebRequest -Uri "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=1000" -OutFile $img

# Multipart helper: PS7+ => -Form, PS5.1 => HttpClient helper
$SupportsForm = $PSVersionTable.PSVersion.Major -ge 7
if ($SupportsForm) {
  Invoke-RestMethod -Uri "$BaseUrl/api/ai/analyze" -Method Post -Form @{ file = Get-Item $img } | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Uri "$BaseUrl/api/ai/lookup" -Method Post -Form @{ file = Get-Item $img; remove_bg = "1" } | ConvertTo-Json -Depth 8
}
else {
  Invoke-MultipartFormData -Uri "$BaseUrl/api/ai/analyze" -Files @{ file = $img } | ConvertTo-Json -Depth 8
  Invoke-MultipartFormData -Uri "$BaseUrl/api/ai/lookup"  -Files @{ file = $img } -Fields @{ remove_bg = "1" } | ConvertTo-Json -Depth 8
}

# Upload to first listing if exists
if ($listings.listings.Count -ge 1) {
  $uuid = $listings.listings[0].uuid
  if ($SupportsForm) {
    Invoke-RestMethod -Uri "$BaseUrl/api/listings/$uuid/images" -Method Post -Headers $headers -Form @{ files = Get-Item $img; remove_bg = "1" } | ConvertTo-Json -Depth 8
  }
  else {
    Invoke-MultipartFormData -Uri "$BaseUrl/api/listings/$uuid/images" -Headers $headers -Files @{ files = $img } -Fields @{ remove_bg = "1" } | ConvertTo-Json -Depth 8
  }
}

# Matching score and recommendations
if ($listings.listings.Count -ge 2) {
  $a = $listings.listings[0].uuid
  $b = $listings.listings[1].uuid
  $scoreBody = @{ listing_a_uuid = $a; listing_b_uuid = $b; user_prefs = @("iphone","velo") } | ConvertTo-Json
  Invoke-RestMethod -Uri "$BaseUrl/api/matching/score" -Method Post -Body $scoreBody -ContentType "application/json" | ConvertTo-Json -Depth 8
}
Invoke-RestMethod -Uri "$BaseUrl/api/matching/recommendations" -Method Get -Headers $headers | ConvertTo-Json -Depth 8

# Diagnostic
$diag = @{ listing = @{ title = "Test"; description = "Courte"; category = ""; brand = ""; estimated_value = 5 } } | ConvertTo-Json
Invoke-RestMethod -Uri "$BaseUrl/api/matching/diagnostic" -Method Post -Body $diag -ContentType "application/json" | ConvertTo-Json -Depth 8

Write-Host "Tests terminés." -ForegroundColor Green
