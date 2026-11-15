param([switch]$Run, [ValidatePattern('^[a-z0-9_/-]+$')][string]$Scene = 'pastel_room')
$ErrorActionPreference = 'Stop'
$base = $PSScriptRoot
$vendor = Join-Path $base 'vendor/glfw-3.4.bin.WIN64'
if (-not (Test-Path "$vendor/include/GLFW/glfw3.h")) {
    New-Item -ItemType Directory -Force -Path "$base/vendor" | Out-Null
    $zip = "$base/vendor/glfw.zip"
    Invoke-WebRequest 'https://github.com/glfw/glfw/releases/download/3.4/glfw-3.4.bin.WIN64.zip' -OutFile $zip
    $sha = (Get-FileHash $zip -Algorithm SHA256).Hash
    if ($sha -ne '54EFA829400F2A0537F742B2B3BDD74E437BB4F2F048E4B7D3C5557D11A611E6') { throw 'GLFW archive checksum mismatch' }
    Expand-Archive -LiteralPath $zip -DestinationPath "$base/vendor" -Force
}
New-Item -ItemType Directory -Force -Path "$base/build" | Out-Null
if (-not (Get-Command g++ -ErrorAction SilentlyContinue)) { throw 'Install MinGW-w64 GCC and add its bin directory to PATH. See dream/README.md.' }
& g++ -std=c++17 -O2 -Wall -Wextra -static '-I' "$vendor/include" "$base/src/main.cpp" "$vendor/lib-mingw-w64/libglfw3.a" -lopengl32 -lgdi32 -o "$base/build/dream.exe"
if ($LASTEXITCODE -ne 0) { throw 'Compilation failed' }
if ($Run) { & "$base/build/dream.exe" --root (Split-Path $base) --scene $Scene }
