$WeChatBase = "C:\Users\Administrator\Documents\WeChat Files\wxid_izefflwcf2n822\FileStorage"
$TargetDir = "C:\Users\Administrator\Desktop\ai群"
$StateFile = Join-Path $TargetDir ".sync-state.json"

if (!(Test-Path $TargetDir)) { New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null }

$syncedFiles = @{}
if (Test-Path $StateFile) {
    try {
        $json = Get-Content $StateFile -Raw
        $syncedFiles = $json | ConvertFrom-Json -AsHashtable
    } catch { $syncedFiles = @{} }
}
if ($null -eq $syncedFiles) { $syncedFiles = @{} }

$since = (Get-Date).AddHours(-24)
$copiedCount = 0

$fileDir = Join-Path $WeChatBase "File"
if (Test-Path $fileDir) {
    Get-ChildItem $fileDir -Recurse -File -ErrorAction SilentlyContinue | Where-Object { 
        $_.LastWriteTime -gt $since -and 
        $_.Extension -notmatch '^\.(tmp|downloading)$' -and
        -not $syncedFiles.ContainsKey($_.FullName)
    } | ForEach-Object {
        $destPath = Join-Path $TargetDir $_.Name
        $counter = 1
        while (Test-Path $destPath) {
            $destPath = Join-Path $TargetDir "$($_.BaseName)_$counter$($_.Extension)"
            $counter++
        }
        Copy-Item $_.FullName $destPath -Force
        $syncedFiles[$_.FullName] = (Get-Date).ToString("o")
        Write-Host "Copied file: $($_.Name)"
        $copiedCount++
    }
}

$tempPhoneDir = Join-Path $WeChatBase "TempFromPhone"
if (Test-Path $tempPhoneDir) {
    Get-ChildItem $tempPhoneDir -Recurse -File -ErrorAction SilentlyContinue | Where-Object { 
        $_.LastWriteTime -gt $since -and 
        -not $syncedFiles.ContainsKey($_.FullName)
    } | ForEach-Object {
        $destPath = Join-Path $TargetDir $_.Name
        $counter = 1
        while (Test-Path $destPath) {
            $destPath = Join-Path $TargetDir "$($_.BaseName)_$counter$($_.Extension)"
            $counter++
        }
        Copy-Item $_.FullName $destPath -Force
        $syncedFiles[$_.FullName] = (Get-Date).ToString("o")
        Write-Host "Copied phone file: $($_.Name)"
        $copiedCount++
    }
}

$videoDir = Join-Path $WeChatBase "Video"
if (Test-Path $videoDir) {
    Get-ChildItem $videoDir -Recurse -File -ErrorAction SilentlyContinue | Where-Object { 
        $_.LastWriteTime -gt $since -and 
        $_.Extension -match '\.(mp4|avi|mov|mkv)$' -and
        -not $syncedFiles.ContainsKey($_.FullName)
    } | ForEach-Object {
        $destPath = Join-Path $TargetDir $_.Name
        $counter = 1
        while (Test-Path $destPath) {
            $destPath = Join-Path $TargetDir "$($_.BaseName)_$counter$($_.Extension)"
            $counter++
        }
        Copy-Item $_.FullName $destPath -Force
        $syncedFiles[$_.FullName] = (Get-Date).ToString("o")
        Write-Host "Copied video: $($_.Name)"
        $copiedCount++
    }
}

$syncedFiles | ConvertTo-Json | Set-Content $StateFile -Encoding UTF8

if ($copiedCount -gt 0) {
    Write-Host "Copied $copiedCount new file(s) to: $TargetDir"
} else {
    Write-Host "No new files found"
}
