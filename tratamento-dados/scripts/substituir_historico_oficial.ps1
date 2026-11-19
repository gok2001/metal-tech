$ErrorActionPreference = 'Stop'

$tratamentoDados = Split-Path -Parent $PSScriptRoot
$dataDir = Join-Path $tratamentoDados 'data'
$arquivoOficial = Join-Path $dataDir 'historico_oficial\leituras.csv'
$diretorioRaw = Join-Path $dataDir 'raw'
$diretorioSamples = Join-Path $dataDir 'samples'
$destino = Join-Path $diretorioRaw '2026\11\18\leituras.csv'
$timestampBackup = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
$desktopDir = Split-Path -Parent (Split-Path -Parent $tratamentoDados)
$backupRoot = Join-Path $desktopDir 'metaltech_backups'
$backupRaw = Join-Path $backupRoot "raw_backup_$timestampBackup"
$backupSamples = Join-Path $backupRoot "samples_backup_$timestampBackup"

if (-not (Test-Path $arquivoOficial)) {
    throw "Arquivo oficial não encontrado: $arquivoOficial"
}

$linhasOficiais = Import-Csv -Path $arquivoOficial
$contagemTotal = @($linhasOficiais).Count
$contagemPeca = @($linhasOficiais | Where-Object { $_.tipo_evento -eq 'PECA_DETECTADA' }).Count
$contagemSemPeca = @($linhasOficiais | Where-Object { $_.tipo_evento -eq 'SEM_PECA' }).Count
$contagemNivel = @($linhasOficiais | Where-Object { $_.tipo_evento -eq 'NIVEL_RESERVATORIO' }).Count

if ($contagemTotal -ne 258 -or $contagemPeca -ne 129 -or $contagemSemPeca -ne 129 -or $contagemNivel -ne 0) {
    throw "CSV oficial inesperado. Total=$contagemTotal; PECA_DETECTADA=$contagemPeca; SEM_PECA=$contagemSemPeca; NIVEL_RESERVATORIO=$contagemNivel. Nenhum arquivo foi alterado."
}

New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null

if (Test-Path $diretorioRaw) {
    Move-Item -Path $diretorioRaw -Destination $backupRaw
}
if (Test-Path $diretorioSamples) {
    Move-Item -Path $diretorioSamples -Destination $backupSamples
}

try {
    New-Item -ItemType Directory -Path (Split-Path -Parent $destino) -Force | Out-Null
    Copy-Item -Path $arquivoOficial -Destination $destino -Force
    New-Item -ItemType File -Path (Join-Path $diretorioRaw '.gitkeep') -Force | Out-Null

    $confirmacao = Import-Csv -Path $destino
    if (@($confirmacao).Count -ne 258) {
        throw 'A conferência após a cópia não encontrou exatamente 258 registros.'
    }

    Write-Host 'Histórico oficial preparado com sucesso.' -ForegroundColor Green
    Write-Host "Eventos: $(@($confirmacao).Count)"
    Write-Host "PECA_DETECTADA: $contagemPeca"
    Write-Host "SEM_PECA: $contagemSemPeca"
    Write-Host 'NIVEL_RESERVATORIO: 0'
    if (Test-Path $backupRaw) { Write-Host "Backup do histórico anterior: $backupRaw" }
    if (Test-Path $backupSamples) { Write-Host "Backup dos samples anteriores: $backupSamples" }

    # Remove módulos antigos de geração/análise de nível físico simulado.
    $arquivosLegados = @(
        (Join-Path $tratamentoDados 'src\simulation\data_generator.py'),
        (Join-Path $tratamentoDados 'src\analytics\reservoir_analysis.py'),
        (Join-Path $tratamentoDados 'tests\test_reservoir_analysis.py')
    )
    foreach ($arquivoLegado in $arquivosLegados) {
        if (Test-Path $arquivoLegado) {
            Remove-Item -Path $arquivoLegado -Force
            Write-Host "Arquivo legado removido: $arquivoLegado"
        }
    }
    $pastaSimulacao = Join-Path $tratamentoDados 'src\simulation'
    if (Test-Path $pastaSimulacao) {
        if ((Get-ChildItem -Path $pastaSimulacao -Force | Measure-Object).Count -eq 0) {
            Remove-Item -Path $pastaSimulacao -Force
        }
    }
}
catch {
    if (Test-Path $diretorioRaw) {
        Remove-Item -Path $diretorioRaw -Recurse -Force
    }
    if (Test-Path $backupRaw) {
        Move-Item -Path $backupRaw -Destination $diretorioRaw
    }
    if ((Test-Path $backupSamples) -and (-not (Test-Path $diretorioSamples))) {
        Move-Item -Path $backupSamples -Destination $diretorioSamples
    }
    throw
}
