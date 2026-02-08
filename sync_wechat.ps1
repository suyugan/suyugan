$srcBase = 'C:\Users\Administrator\Documents\WeChat Files\wxid_izefflwcf2n822\FileStorage'
$dest = 'C:\Users\Administrator\Desktop\ai群'
$cutoff = (Get-Date).AddHours(-24)
$dirs = @('File','TempFromPhone','Video')
$copied = @()
$skipped = 0

if (!(Test-Path $dest)) { New-Item -ItemType Directory -Path $dest -Force | Out-Null }

foreach ($d in $dirs) {
    $src = Join-Path $srcBase $d
    if (!(Test-Path $src)) { Write-Host "SKIP: $src not found"; continue }
    Get-ChildItem -Path $src -Recurse -File | Where-Object { $_.LastWriteTime -gt $cutoff } | ForEach-Object {
        $destFile = Join-Path $dest $_.Name
        if (Test-Path $destFile) { $skipped++; return }
        Copy-Item $_.FullName -Destination $destFile -Force
        $copied += $_.Name
    }
}

Write-Host "COPIED: $($copied.Count)"
Write-Host "SKIPPED: $skipped"
if ($copied.Count -gt 0) { $copied | ForEach-Object { Write-Host "  - $_" } }
