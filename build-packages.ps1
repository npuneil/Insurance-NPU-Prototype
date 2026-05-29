<#
.SYNOPSIS
    Build downloadable Intel and Snapdragon packages for the Zava Insurance
    On-Device AI demo.

.DESCRIPTION
    Produces two zips in dist\:
      ZavaInsuranceAI-Intel-v<version>.zip
      ZavaInsuranceAI-Snapdragon-v<version>.zip

    Each zip contains a stand-alone copy of the Flask app plus the
    platform-specific overlay (README, START_HERE, Setup.bat, StartApp.bat,
    platform.txt). Run Setup.bat once, then StartApp.bat thereafter.

.EXAMPLE
    .\build-packages.ps1
    .\build-packages.ps1 -Version 1.1.0 -Clean
#>
[CmdletBinding()]
param(
    [string]$Version = "1.0.0",
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$root  = Split-Path -Parent $MyInvocation.MyCommand.Path
$dist  = Join-Path $root "dist"
$stage = Join-Path $dist "staging"

# Source files to include in EVERY package (relative to repo root).
$includeFiles = @(
    "app.py",
    "requirements.txt",
    "Setup.ps1",
    "DEMO_SCRIPT.txt",
    ".gitignore"
)
$includeDirs = @(
    "static",
    "templates"
)

# Platform overlays: name -> @{ ZipName; OverlayDir }
$platforms = @{
    "Intel"      = @{ ZipName = "ZavaInsuranceAI-Intel-v$Version.zip";      OverlayDir = "packaging\intel" }
    "Snapdragon" = @{ ZipName = "ZavaInsuranceAI-Snapdragon-v$Version.zip"; OverlayDir = "packaging\snapdragon" }
}

# ── Pre-flight: confirm all source files exist ────────────────────────────────
foreach ($f in $includeFiles + $includeDirs) {
    if (-not (Test-Path (Join-Path $root $f))) {
        Write-Warning "Missing source: $f  (will be skipped)"
    }
}

if ($Clean -and (Test-Path $dist)) {
    Write-Host "[CLEAN] Removing $dist" -ForegroundColor Yellow
    Remove-Item -Recurse -Force $dist
}
New-Item -ItemType Directory -Force -Path $dist  | Out-Null
New-Item -ItemType Directory -Force -Path $stage | Out-Null

foreach ($platformName in $platforms.Keys) {
    $spec       = $platforms[$platformName]
    $platDir    = Join-Path $stage $platformName
    $overlayDir = Join-Path $root  $spec.OverlayDir
    $zipPath    = Join-Path $dist  $spec.ZipName

    Write-Host ""
    Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  Building $platformName package -> $($spec.ZipName)"        -ForegroundColor Cyan
    Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan

    if (-not (Test-Path $overlayDir)) {
        throw "Overlay directory not found: $overlayDir"
    }

    # Clean stage dir
    if (Test-Path $platDir) { Remove-Item -Recurse -Force $platDir }
    New-Item -ItemType Directory -Force -Path $platDir | Out-Null

    # 1. Copy shared source files
    foreach ($f in $includeFiles) {
        $src = Join-Path $root $f
        if (Test-Path $src) {
            Copy-Item $src -Destination $platDir -Force
            Write-Host "  [+] $f"
        }
    }
    foreach ($d in $includeDirs) {
        $src = Join-Path $root $d
        if (Test-Path $src) {
            Copy-Item $src -Destination $platDir -Recurse -Force
            Write-Host "  [+] $d\"
        }
    }

    # 2. Apply platform overlay (overwrites shared files where they exist)
    Get-ChildItem -Path $overlayDir -Recurse | Where-Object { -not $_.PSIsContainer } | ForEach-Object {
        $rel = $_.FullName.Substring($overlayDir.Length).TrimStart('\','/')
        $dst = Join-Path $platDir $rel
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null
        Copy-Item $_.FullName -Destination $dst -Force
        Write-Host "  [^] overlay: $rel"
    }

    # 3. Drop a platform marker (read by app.py if env var isn't set)
    "$($platformName.ToLower())" | Out-File -FilePath (Join-Path $platDir "platform.txt") -Encoding ascii -NoNewline

    # 4. Create empty uploads dir so Flask's mkdir(exist_ok=True) is happy
    New-Item -ItemType Directory -Force -Path (Join-Path $platDir "uploads") | Out-Null
    "# Placeholder so the empty uploads folder is included in the zip." `
        | Out-File -FilePath (Join-Path $platDir "uploads\.gitkeep") -Encoding ascii

    # 5. Zip it
    if (Test-Path $zipPath) { Remove-Item -Force $zipPath }
    Write-Host "  [zip] -> $zipPath"
    Compress-Archive -Path (Join-Path $platDir "*") -DestinationPath $zipPath -CompressionLevel Optimal -Force

    $sizeMb = [math]::Round((Get-Item $zipPath).Length / 1MB, 2)
    Write-Host "  [OK ] $($spec.ZipName)  ($sizeMb MB)" -ForegroundColor Green
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  Build complete. Artifacts in: $dist" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Green
Get-ChildItem $dist -Filter "*.zip" | Format-Table Name, @{N='SizeMB';E={[math]::Round($_.Length/1MB,2)}}, LastWriteTime
