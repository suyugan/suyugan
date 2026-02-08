 = " C:\Users\Administrator\Desktop\ai群\
if (!(Test-Path )) { New-Item -ItemType Directory -Path -Force }
 = (Get-Date).AddHours(-24)
 = \C:\Users\Administrator\Documents\WeChat Files\wxid_izefflwcf2n822\FileStorage\File\
 = \C:\Users\Administrator\Documents\WeChat Files\wxid_izefflwcf2n822\FileStorage\TempFromPhone\
 = \C:\Users\Administrator\Documents\WeChat Files\wxid_izefflwcf2n822\FileStorage\Video\
 = @(, , )
 = 0; = 0; = @()
foreach ( in ) {
 if (!(Test-Path )) { Write-Host \SKIP: \; continue }
 Get-ChildItem -Path -Recurse -File | Where-Object { .LastWriteTime -gt } | ForEach-Object {
 = Join-Path .Name
 if (Test-Path ) { ++; return }
 Copy-Item .FullName -Destination -Force
 ++
 += .Name
 }
}
Write-Host \COPIED= SKIPPED=\
if (.Count -gt 0) { | ForEach-Object { Write-Host " \ } }