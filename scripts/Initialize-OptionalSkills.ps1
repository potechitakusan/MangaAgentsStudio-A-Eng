#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$ProjectRoot = '',
    [ValidateSet('', 'none', 'humanizer-jp', 'japanese-natural-writing')][string]$Provider = '',
    [ValidateSet('Unspecified', 'Granted', 'Denied')][string]$GeminiConsent = 'Unspecified',
    [string]$ConsentNote = ''
)

function Assert-OptionalPath([string]$Root, [string]$Relative) {
    if ([IO.Path]::IsPathRooted($Relative) -or $Relative -match '(^|[\\/])\.\.([\\/]|$)') { throw 'Paths outside the project are not allowed.' }
    $path = [IO.Path]::GetFullPath((Join-Path $Root $Relative))
    $rootPrefix = $Root.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    if (-not $path.StartsWith($rootPrefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'Specify a path inside the project.' }
    $current = $path
    while ($current) {
        if (Test-Path -LiteralPath $current) {
            $item = Get-Item -LiteralPath $current -Force
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Installation destinations must not traverse links.' }
        }
        $current = Split-Path $current -Parent
    }
    return $path
}

function Write-OptionalJson($Value, [string]$Path) {
    $null = [IO.Directory]::CreateDirectory((Split-Path $Path -Parent))
    [IO.File]::WriteAllText($Path, ($Value | ConvertTo-Json -Depth 20), [Text.UTF8Encoding]::new($false))
}

function Get-OptionalSelection([string]$Root) {
    $path = Assert-OptionalPath $Root 'OPTION.md'
    if (-not (Test-Path -LiteralPath $path)) { return 'none' }
    $body = [string](Get-Content -LiteralPath $path -Raw -Encoding UTF8)
    $rows = [regex]::Matches($body, '(?m)^\|\s*(?:Japanese polishing skill|日本語推敲スキル)\s*\|\s*([^|]*)\|')
    if ($rows.Count -eq 0) { return 'none' }
    if ($rows.Count -gt 1) { throw 'Duplicate Japanese polishing skill setting rows.' }
    $value = $rows[0].Groups[1].Value.Trim()
    switch -Regex ($value) {
        '^(|disabled|do not use|使用しない|無効|none)$' { return 'none' }
        '^(enabled|use|使用する|有効|humanizer-jp)$' { return 'humanizer-jp' }
        '^japanese-natural-writing(?:[（(]Gemini[）)])?$' { return 'japanese-natural-writing' }
        default { throw 'Set Japanese polishing skill to none, humanizer-jp, or japanese-natural-writing.' }
    }
}

function Find-OptionalGit {
    $command = Get-Command git -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($command) { return $command.Source }
    return $null
}

function Invoke-OptionalGit([string]$Git, [string[]]$Arguments) {
    $priorPreference = $ErrorActionPreference
    $priorPrompt = [Environment]::GetEnvironmentVariable('GIT_TERMINAL_PROMPT', 'Process')
    try {
        $ErrorActionPreference = 'Continue'
        $env:GIT_TERMINAL_PROMPT = '0'
        $output = @(& $Git @Arguments 2>&1 | ForEach-Object { "$_" })
        if ($LASTEXITCODE -ne 0) { throw ('Git operation failed: ' + ($output -join "`n")) }
        return ($output -join "`n")
    } finally {
        $ErrorActionPreference = $priorPreference
        [Environment]::SetEnvironmentVariable('GIT_TERMINAL_PROMPT', $priorPrompt, 'Process')
    }
}

function Get-OptionalArchive($Source, [string]$Work, [string]$Git) {
    $zip = Join-Path $Work 'source.zip'
    if ($Source.method -eq 'git') {
        if ($Source.repository -notmatch '^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\.git$' -or $Source.revision -notmatch '^[a-f0-9]{40}$') { throw 'Invalid Git source or pinned revision.' }
        $repo = Join-Path $Work 'repo'
        $hooks = Join-Path $Work 'empty-hooks'
        $null = [IO.Directory]::CreateDirectory($hooks)
        $null = Invoke-OptionalGit $Git @('-c', "core.hooksPath=$hooks", 'init', '--quiet', $repo)
        $null = Invoke-OptionalGit $Git @('-C', $repo, '-c', "core.hooksPath=$hooks", '-c', 'credential.helper=', 'fetch', '--quiet', '--depth=1', $Source.repository, $Source.revision)
        $head = Invoke-OptionalGit $Git @('-C', $repo, 'rev-parse', 'FETCH_HEAD')
        if ($head.Trim() -cne $Source.revision) { throw 'The fetched Git revision does not match.' }
        $names = @($Source.files.PSObject.Properties.Name)
        $tree = Invoke-OptionalGit $Git (@('-C', $repo, 'ls-tree', '-r', $head, '--') + $names)
        if ($tree -match '(?m)^(120000|160000) ') { throw 'Links and submodules inside skills are not installed.' }
        $null = Invoke-OptionalGit $Git (@('-C', $repo, '-c', 'core.autocrlf=false', '-c', 'core.eol=lf', 'archive', '--format=zip', "--output=$zip", $head, '--') + $names)
    } elseif ($Source.method -eq 'zip') {
        if ($Source.url -notmatch '^https://note\.com/api/v2/attachments/download/[a-f0-9]+$' -or $Source.revision -notmatch '^[a-f0-9]{64}$') { throw 'Invalid ZIP source or pinned hash.' }
        $priorProtocol = [Net.ServicePointManager]::SecurityProtocol
        try {
            [Net.ServicePointManager]::SecurityProtocol = $priorProtocol -bor [Net.SecurityProtocolType]::Tls12
            Invoke-WebRequest -UseBasicParsing -Uri $Source.url -OutFile $zip -TimeoutSec 60
        } finally { [Net.ServicePointManager]::SecurityProtocol = $priorProtocol }
        if ((Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant() -cne $Source.revision) { throw 'ZIP content differs from the verified version.' }
    } else { throw 'Unsupported retrieval method.' }
    return $zip
}

function Expand-OptionalArchive([string]$Zip, $Source, [string]$Stage) {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [IO.Compression.ZipFile]::OpenRead($Zip)
    try {
        $expected = @{}
        foreach ($file in $Source.files.PSObject.Properties) {
            if ($file.Name -notmatch '^[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*$' -or $file.Name.Split('/') -contains '..' -or $file.Value -notmatch '^[a-f0-9]{64}$') { throw 'Invalid file specification for retrieval.' }
            $expected[$Source.prefix + $file.Name] = $file
        }
        $seen = @{}
        foreach ($entry in $archive.Entries) {
            if ($entry.FullName.EndsWith('/')) { continue }
            if (-not $expected.ContainsKey($entry.FullName) -or $seen.ContainsKey($entry.FullName)) { throw 'The ZIP contains unexpected or duplicate files.' }
            if ((($entry.ExternalAttributes -shr 16) -band 0xF000) -eq 0xA000) { throw 'Links inside ZIP files are not installed.' }
            $file = $expected[$entry.FullName]
            $path = Assert-OptionalPath $Stage $file.Name
            $null = [IO.Directory]::CreateDirectory((Split-Path $path -Parent))
            [IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $path, $false)
            if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -cne $file.Value) { throw 'Skill file content does not match the verified version.' }
            $seen[$entry.FullName] = $true
        }
        if ($seen.Count -ne $expected.Count) { throw 'Required skill files are missing.' }
    } finally { $archive.Dispose() }
}

function Initialize-OptionalSkills {
    [CmdletBinding()]
    param([string]$ProjectRoot, [string]$Provider = '', [string]$GeminiConsent = 'Unspecified', [string]$ConsentNote = '')
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'
    $root = [IO.Path]::GetFullPath($ProjectRoot)
    if (-not (Test-Path -LiteralPath (Join-Path $root 'project.json') -PathType Leaf)) { throw 'Run this in a scaffolded comic project.' }
    if (-not $Provider) { $Provider = Get-OptionalSelection $root }
    if ($Provider -eq 'none') { return [pscustomobject]@{ status = 'disabled'; provider = 'none'; message = 'Polishing skills are disabled. No external retrieval, Git check, or Gemini call will run.' } }
    if ($Provider -notin @('humanizer-jp', 'japanese-natural-writing')) { throw 'Unsupported polishing skill.' }
    $manifestPath = Assert-OptionalPath $root 'config/optional-skills.json'
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($manifest.schemaVersion -ne 1) { throw 'Invalid polishing skill distribution settings.' }
    $source = $manifest.providers.$Provider
    $targetRelative = '.agents/skills/' + $Provider
    $target = Assert-OptionalPath $root $targetRelative
    $stateRelative = '.work/optional-skills/' + $Provider
    $receiptPath = Assert-OptionalPath $root ($stateRelative + '-installed.json')
    $consentPath = Assert-OptionalPath $root ($stateRelative + '-consent.json')
    # Detecting or enabling Gemini does not grant permission to consume its quota.
    $requiresConsent = $Provider -eq 'japanese-natural-writing' -or $source.requiresGeminiConsent
    if ($requiresConsent) {
        if ($GeminiConsent -notin @('Unspecified', 'Granted', 'Denied')) { throw 'Invalid Gemini consent state.' }
        if ($GeminiConsent -ne 'Unspecified') {
            if ([string]::IsNullOrWhiteSpace($ConsentNote)) { throw 'Record the explicit user response and authorized scope.' }
            Write-OptionalJson ([ordered]@{ provider = $Provider; revision = $source.revision; decision = $GeminiConsent; note = $ConsentNote; recordedAt = [DateTimeOffset]::Now.ToString('o') }) $consentPath
        }
        $consent = if (Test-Path -LiteralPath $consentPath) { Get-Content -LiteralPath $consentPath -Raw -Encoding UTF8 | ConvertFrom-Json } else { $null }
        if (-not $consent -or $consent.provider -cne $Provider -or $consent.revision -cne $source.revision -or [string]::IsNullOrWhiteSpace($consent.note)) {
            return [pscustomobject]@{ status = 'needs_gemini_consent'; provider = $Provider; message = 'Before installation, ask permission to send the selected project text to Gemini and consume its quota for polishing.' }
        }
        if ($consent.decision -cne 'Granted') { return [pscustomobject]@{ status = 'gemini_declined'; provider = $Provider; message = 'Gemini is not authorized. Continue ordinary production without retrieval, installation, or calls.' } }
    }
    if (Test-Path -LiteralPath $target) {
        if (-not (Test-Path -LiteralPath $receiptPath)) { throw 'An existing skill with this name will not be overwritten. Compare it with the installation receipt.' }
        $receipt = Get-Content -LiteralPath $receiptPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($receipt.provider -cne $Provider -or $receipt.path -cne $targetRelative -or $receipt.revision -cne $source.revision) { throw 'The installed revision or destination differs. Handle updates separately.' }
        $expectedNames = @(@($source.files.PSObject.Properties.Name) + @('agents/openai.yaml') | Sort-Object -Unique)
        if (@(Compare-Object $expectedNames @($receipt.files.PSObject.Properties.Name)).Count -ne 0) { throw 'The installation receipt file list does not match.' }
        foreach ($file in $receipt.files.PSObject.Properties) {
            $path = Assert-OptionalPath $target $file.Name
            if (-not (Test-Path -LiteralPath $path -PathType Leaf) -or (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -cne $file.Value) { throw 'Installed skill files have changed or are missing. They will not be overwritten automatically.' }
        }
        return [pscustomobject]@{ status = 'ready'; provider = $Provider; path = $targetRelative; message = 'Already installed. No external retrieval is needed.' }
    }
    $git = if ($source.method -eq 'git') { Find-OptionalGit } else { $null }
    if ($source.method -eq 'git' -and -not $git) {
        return [pscustomobject]@{ status = 'needs_git_consent'; provider = $Provider; message = 'Git is unavailable. Ask permission to install Git and proceed only after approval.' }
    }
    $work = Assert-OptionalPath $root ('.work/optional-skills/download-' + [Guid]::NewGuid().ToString('N'))
    $stage = Join-Path $work 'skill'
    $null = [IO.Directory]::CreateDirectory($stage)
    $zip = Get-OptionalArchive $source $work $git
    Expand-OptionalArchive $zip $source $stage
    if (-not (Test-Path -LiteralPath (Join-Path $stage 'SKILL.md') -PathType Leaf)) { throw 'SKILL.md is missing.' }
    # Apply only to explicitly selected targets. Preserve original definitions and licenses.
    $policyPath = Join-Path $stage 'agents/openai.yaml'
    $policy = if (Test-Path -LiteralPath $policyPath) { Get-Content -LiteralPath $policyPath -Raw -Encoding UTF8 } else { '' }
    if ($policy -match '(?m)^policy\s*:') { throw 'The invocation policy has changed. Review it before installation.' }
    $null = [IO.Directory]::CreateDirectory((Split-Path $policyPath -Parent))
    [IO.File]::WriteAllText($policyPath, ($policy.TrimEnd() + "`npolicy:`n  allow_implicit_invocation: false`n"), [Text.UTF8Encoding]::new($false))
    $files = [ordered]@{}
    foreach ($name in @($source.files.PSObject.Properties.Name) + @('agents/openai.yaml') | Select-Object -Unique) {
        $files[$name] = (Get-FileHash -LiteralPath (Join-Path $stage $name) -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    $receipt = [ordered]@{ provider = $Provider; revision = $source.revision; path = $targetRelative; installedAt = [DateTimeOffset]::Now.ToString('o'); files = $files; adjustment = 'Implicit invocation disabled. Apply explicitly only to selected targets.' }
    $null = [IO.Directory]::CreateDirectory((Split-Path $target -Parent))
    # Recheck immediately before moving that staging and destination paths are ordinary paths inside the project.
    $null = Assert-OptionalPath $root ($stage.Substring($root.Length).TrimStart('\', '/'))
    $null = Assert-OptionalPath $root $targetRelative
    if (Test-Path -LiteralPath $target) { throw 'The destination now exists. Stopping without overwriting.' }
    Move-Item -LiteralPath $stage -Destination $target
    Write-OptionalJson $receipt $receiptPath
    return [pscustomobject]@{ status = 'installed'; provider = $Provider; path = $targetRelative; message = 'Installed inside the project. Reopen Codex only if the skill is not recognized.' }
}

if ($MyInvocation.InvocationName -ne '.') {
    if (-not $ProjectRoot) { $ProjectRoot = Split-Path $PSScriptRoot -Parent }
    Initialize-OptionalSkills -ProjectRoot $ProjectRoot -Provider $Provider -GeminiConsent $GeminiConsent -ConsentNote $ConsentNote
}
