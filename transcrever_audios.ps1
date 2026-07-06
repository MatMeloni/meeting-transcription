# Script de transcricao em lote - Imersao 2026
# Saida: C:\Users\mathe\AppData\Local\meeting_transcription\outputs\

$base = "C:\Users\mathe\Downloads\meeting-transcription"
$localBase = "C:\Users\mathe\AppData\Local\meeting_transcription"

# Adiciona src/ e raiz ao PYTHONPATH
$env:PYTHONPATH = "$base\src;$base"

# Usa caminhos locais (fora do OneDrive) para outputs e modelos
$env:OUTPUT_DIR = "$localBase\outputs"
$env:MEETING_APP_BASE_DIR = $localBase

# Modelo small para melhor precisao em portugues
$env:WHISPER_MODEL = "small"

# Forca CPU para evitar erro cublas64_12.dll (sem CUDA instalado)
$env:WHISPER_DEVICE = "cpu"
$env:WHISPER_COMPUTE_TYPE = "int8"

# Atualiza PATH para incluir FFmpeg
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")

# Garante que os diretorios existem
[System.IO.Directory]::CreateDirectory("$localBase\outputs\transcripts") | Out-Null
[System.IO.Directory]::CreateDirectory("$localBase\outputs\summaries") | Out-Null
[System.IO.Directory]::CreateDirectory("$localBase\models_cache") | Out-Null

Write-Host "Outputs serao salvos em: $localBase\outputs"
Write-Host ""

# Localiza os audios
$pasta = Join-Path $base "Audios"
$arquivos = Get-ChildItem -Path $pasta -Filter "*.mp3" | Sort-Object Name

if ($arquivos.Count -eq 0) {
    Write-Host "Nenhum arquivo MP3 encontrado em: $pasta"
    exit 1
}

$total = $arquivos.Count
$i = 0

foreach ($arquivo in $arquivos) {
    $i++
    $nome = $arquivo.BaseName -replace '\s*\(.*?\)\s*$', '' -replace '\s*-\s*Carol Soares.*$', '' -replace '\s+', ' '
    $nome = $nome.Trim()

    Write-Host "======================================================"
    Write-Host "[$i/$total] $nome"
    Write-Host "Arquivo: $($arquivo.Name)"
    Write-Host "Inicio: $(Get-Date -Format 'HH:mm:ss')"
    Write-Host "======================================================"

    Set-Location $base
    python app.py --audio "$($arquivo.FullName)" --meeting-name "$nome"

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERRO] Falha: $nome"
    } else {
        Write-Host "[OK] Concluido: $nome - $(Get-Date -Format 'HH:mm:ss')"
    }
    Write-Host ""
}

Write-Host "======================================================"
Write-Host "Transcricoes concluidas!"
Write-Host "Resultados em: $localBase\outputs\transcripts"
Write-Host "Resumos em:    $localBase\outputs\summaries"
Write-Host "======================================================"
