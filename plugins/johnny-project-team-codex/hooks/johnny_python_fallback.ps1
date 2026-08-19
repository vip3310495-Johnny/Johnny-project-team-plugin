[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$workspace = (Get-Location).Path
$excludedSegments = @('.git', 'node_modules')
$enabledRepositories = [System.Collections.Generic.List[string]]::new()

try {
    $markers = Get-ChildItem -LiteralPath $workspace -Filter 'enabled.json' -File -Recurse -Force -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Directory.Name -eq '.johnny' -and
            -not ($_.FullName.Split([IO.Path]::DirectorySeparatorChar) | Where-Object { $_ -in $excludedSegments })
        }

    foreach ($marker in $markers) {
        try {
            $state = Get-Content -LiteralPath $marker.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
            $repository = $marker.Directory.Parent.FullName
            if ($state.enabled -eq $true -and $state.scope -eq $repository) {
                $enabledRepositories.Add($repository)
            }
        }
        catch {
            Write-Error "Johnny hook cannot validate enabled marker: $($marker.FullName)"
            exit 1
        }
    }
}
catch {
    Write-Error "Johnny hook cannot inspect the workspace for enabled repositories: $workspace"
    exit 1
}

if ($enabledRepositories.Count -gt 0) {
    $rendered = ($enabledRepositories | Sort-Object -Unique) -join ', '
    Write-Error "Johnny hook cannot find Python for enabled repository scope: $rendered. Set CODEX_PYTHON or install Python 3."
    exit 1
}

Write-Warning 'Johnny hook could not find Python; no enabled Johnny repository is in scope, so the hook is not applicable.'
exit 0
