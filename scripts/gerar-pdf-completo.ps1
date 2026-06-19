# Gera arquivo unico para colar no Canva
# Uso: .\scripts\gerar-pdf-completo.ps1

$root = Split-Path -Parent $PSScriptRoot
$out  = Join-Path $root "produto\CONTEUDO-INFINITO-IA-COMPLETO.md"

$capa = @"
---
PAGINA: CAPA (nao colar no corpo — usar canva-guia-paginas.md)
---

# CONTEUDO INFINITO IA
## 45 Prompts para TikTok e Instagram

Arquivo gerado automaticamente. Monte o PDF seguindo produto/canva-guia-paginas.md

---

"@

$files = @(
    "produto\prompts-raw.md",
    "produto\bonus-calendario-30.md",
    "produto\guia-uso-ia.md",
    "produto\exemplos-output.md"
)

$sb = [System.Text.StringBuilder]::new()
[void]$sb.AppendLine($capa)

foreach ($rel in $files) {
    $path = Join-Path $root $rel
    if (Test-Path $path) {
        [void]$sb.AppendLine("")
        [void]$sb.AppendLine("<!-- INICIO: $rel -->")
        [void]$sb.AppendLine("")
        [void]$sb.AppendLine((Get-Content -Path $path -Raw -Encoding UTF8))
        [void]$sb.AppendLine("")
        [void]$sb.AppendLine("<!-- FIM: $rel -->")
        [void]$sb.AppendLine("")
        Write-Host "OK: $rel"
    } else {
        Write-Warning "Arquivo nao encontrado: $rel"
    }
}

$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($out, $sb.ToString(), $utf8NoBom)

$lines = (Get-Content $out).Count
Write-Host ""
Write-Host "Gerado: $out"
Write-Host "Linhas: $lines"
