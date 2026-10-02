#requires -Version 5.1
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
. (Join-Path $root 'scripts/Initialize-OptionalSkills.ps1')
$realGit = Find-OptionalGit
$getRealArchive = ${function:Get-OptionalArchive}
$runRealGit = ${function:Invoke-OptionalGit}
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.IO.Compression
$testRoot = Join-Path $root ('.work/optional-skills-test-' + [Guid]::NewGuid().ToString('N'))
$null = [IO.Directory]::CreateDirectory($testRoot)
$checks = [Collections.Generic.List[string]]::new()
function Check([bool]$Condition, [string]$Name) {
    if (-not $Condition) { throw "FAIL: $Name" }
    $checks.Add($Name)
}
function Must-Fail([scriptblock]$Action, [string]$Name) {
    $failed = $false
    try { $null = & $Action } catch { $failed = $true }
    Check $failed $Name
}
function Write-Text([string]$Path, [string]$Body) {
    $null = [IO.Directory]::CreateDirectory((Split-Path $Path -Parent))
    [IO.File]::WriteAllText($Path, $Body, [Text.UTF8Encoding]::new($false))
}
function New-TestArchive([string]$Name, $Contents) {
    $path = Join-Path $testRoot ($Name + '.zip')
    $zip = [IO.Compression.ZipFile]::Open($path, [IO.Compression.ZipArchiveMode]::Create)
    try {
        foreach ($entryName in $Contents.Keys) {
            $stream = $zip.CreateEntry($entryName).Open()
            try {
                $bytes = [Text.Encoding]::UTF8.GetBytes($Contents[$entryName])
                $stream.Write($bytes, 0, $bytes.Length)
            } finally { $stream.Dispose() }
        }
    } finally { $zip.Dispose() }
    return $path
}
function Text-Hash([string]$Value) {
    $hash = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($hash.ComputeHash([Text.Encoding]::UTF8.GetBytes($Value)))).Replace('-', '').ToLowerInvariant() }
    finally { $hash.Dispose() }
}

# Replace only retrieval boundaries; verify real placement/checking without third-party text or Gemini.
$script:fetches = 0
$script:gitChecks = 0
$script:gitAvailable = $true
function Find-OptionalGit {
    $script:gitChecks++
    if ($script:gitAvailable) { return 'dummy-git' }
    return $null
}
function Get-OptionalArchive($Source, [string]$Work, [string]$Git) {
    $script:fetches++
    return $script:archive
}
$contents = [ordered]@{
    'SKILL.md' = "---`nname: test-only`ndescription: Installation-test fixture only. Do not execute.`n---`n# Original text for testing`n"
    'LICENSE' = 'Test permission notice'
    'NOTICE' = 'Test copyright notice'
}
$script:archive = New-TestArchive 'valid' $contents
$validArchive = $script:archive
$fileHashes = [ordered]@{}
foreach ($name in $contents.Keys) { $fileHashes[$name] = Text-Hash $contents[$name] }
$registry = [ordered]@{
    schemaVersion = 1
    providers = [ordered]@{
        'humanizer-jp' = [ordered]@{ method = 'git'; revision = ('a' * 40); requiresGeminiConsent = $false; prefix = ''; files = $fileHashes }
        'japanese-natural-writing' = [ordered]@{ method = 'zip'; revision = ('b' * 64); requiresGeminiConsent = $true; prefix = ''; files = $fileHashes }
    }
}
function New-TestProject([string]$Name, [string]$Selection = 'none') {
    $path = Join-Path $testRoot $Name
    Write-Text (Join-Path $path 'project.json') '{"name":"Test fixture"}'
    Write-Text (Join-Path $path 'OPTION.md') "| Japanese polishing skill | $Selection | Test |`n"
    Write-OptionalJson $registry (Join-Path $path 'config/optional-skills.json')
    return $path
}

$off = New-TestProject 'default'
$state = Initialize-OptionalSkills $off
Check ($state.status -eq 'disabled' -and $script:fetches -eq 0 -and $script:gitChecks -eq 0) 'Defaults perform no Git check or retrieval'
Check (-not (Test-Path -LiteralPath (Join-Path $off '.work')) -and -not (Test-Path -LiteralPath (Join-Path $off '.agents'))) 'Disabled mode creates no work records or installation directory'
$missing = Join-Path $testRoot 'missing-option'
Write-Text (Join-Path $missing 'project.json') '{}'
Check ((Initialize-OptionalSkills $missing).status -eq 'disabled') 'Missing OPTION or retrieval settings defaults to disabled'
Write-Text (Join-Path $missing 'OPTION.md') ''
Check ((Initialize-OptionalSkills $missing).status -eq 'disabled') 'Empty OPTION defaults to disabled'
foreach ($selection in @('', 'disabled', 'none')) {
    Write-Text (Join-Path $off 'OPTION.md') "| Japanese polishing skill | $selection | Test |"
    Check ((Get-OptionalSelection $off) -eq 'none') "Resolve a disabled selection: $selection"
}
Write-Text (Join-Path $off 'OPTION.md') '| Another field | humanizer-jp | Japanese polishing skill is mentioned only as an example |'
Check ((Get-OptionalSelection $off) -eq 'none') 'Descriptions and unrelated fields do not enable a skill'
Write-Text (Join-Path $off 'OPTION.md') '| Japanese polishing skill | use | Test |'
Check ((Get-OptionalSelection $off) -eq 'humanizer-jp') 'A simple enable instruction selects the non-Gemini provider'
Write-Text (Join-Path $off 'OPTION.md') '| Japanese polishing skill | japanese-natural-writing(Gemini) | Test |'
Check ((Get-OptionalSelection $off) -eq 'japanese-natural-writing') 'Resolve the Gemini provider selection'
Write-Text (Join-Path $off 'OPTION.md') '| Japanese polishing skill | unknown | Test |'
Must-Fail { Get-OptionalSelection $off } 'Do not silently install an unknown skill'
Write-Text (Join-Path $off 'OPTION.md') "| Japanese polishing skill | none |`n| Japanese polishing skill | humanizer-jp |"
Must-Fail { Get-OptionalSelection $off } 'Reject duplicate settings'
Must-Fail { Initialize-OptionalSkills $testRoot -Provider humanizer-jp } 'Do not install outside a project'

# Intentional legacy Japanese OPTION compatibility; ordinary fixtures above use English.
foreach ($legacySelection in @('無効', '使用しない')) {
    Write-Text (Join-Path $off 'OPTION.md') "| 日本語推敲スキル | $legacySelection | Legacy compatibility |"
    Check ((Get-OptionalSelection $off) -eq 'none') "Legacy Japanese disabled alias resolves: $legacySelection"
}
Write-Text (Join-Path $off 'OPTION.md') '| 日本語推敲スキル | 使用する | Legacy compatibility |'
Check ((Get-OptionalSelection $off) -eq 'humanizer-jp') 'Legacy Japanese enable alias resolves'

$standard = New-TestProject 'standard' 'humanizer-jp'
$script:gitAvailable = $false
Check ((Initialize-OptionalSkills $standard).status -eq 'needs_git_consent' -and $script:fetches -eq 0) 'Missing Git requires consent without retrieval'
Check (-not (Test-Path -LiteralPath (Join-Path $standard '.agents'))) 'Do not create the installation directory before a Git decision'
$script:gitAvailable = $true
$state = Initialize-OptionalSkills $standard
Check ($state.status -eq 'installed' -and $script:fetches -eq 1) 'Install the enabled standard provider on first use'
$installed = Join-Path $standard '.agents/skills/humanizer-jp'
foreach ($name in $contents.Keys) {
    Check ((Get-FileHash -LiteralPath (Join-Path $installed $name)).Hash.ToLowerInvariant() -ceq $fileHashes[$name]) "Preserve source text and copyright notices: $name"
}
Check ((Get-Content -LiteralPath (Join-Path $installed 'agents/openai.yaml') -Raw -Encoding UTF8) -match 'allow_implicit_invocation: false') 'Installed skills cannot be invoked implicitly'
$priorGitChecks = $script:gitChecks
$script:gitAvailable = $false
Check ((Initialize-OptionalSkills $standard).status -eq 'ready' -and $script:fetches -eq 1 -and $script:gitChecks -eq $priorGitChecks) 'Resume verifies the installation without Git or another download'
$receiptPath = Join-Path $standard '.work/optional-skills/humanizer-jp-installed.json'
$receipt = Get-Content -LiteralPath $receiptPath -Raw -Encoding UTF8 | ConvertFrom-Json
Check ($receipt.path -ceq '.agents/skills/humanizer-jp' -and -not (Get-Content -LiteralPath $receiptPath -Raw).Contains($testRoot)) 'Installation records contain no machine-specific absolute paths'
Write-Text (Join-Path $standard 'OPTION.md') '| Japanese polishing skill | none |'
Check ((Initialize-OptionalSkills $standard).status -eq 'disabled' -and (Test-Path -LiteralPath $installed) -and $script:fetches -eq 1) 'Disabling retains installed files and returns disabled'
Check ((Initialize-OptionalSkills $standard -Provider humanizer-jp).status -eq 'ready') 'Effective conversation settings can be passed explicitly'
Write-Text (Join-Path $installed 'SKILL.md') 'User modification'
Must-Fail { Initialize-OptionalSkills $standard -Provider humanizer-jp } 'Do not overwrite a modified skill'
Check ((Get-Content -LiteralPath (Join-Path $installed 'SKILL.md') -Raw -Encoding UTF8) -ceq 'User modification') 'Preserve modified files'
$existing = New-TestProject 'existing' 'humanizer-jp'
Write-Text (Join-Path $existing '.agents/skills/humanizer-jp/SKILL.md') 'Another existing skill'
Must-Fail { Initialize-OptionalSkills $existing } 'Do not overwrite an unrecorded same-name skill'

$gemini = New-TestProject 'gemini' 'japanese-natural-writing'
$script:gitAvailable = $true
$beforeFetch = $script:fetches
$beforeGit = $script:gitChecks
Check ((Initialize-OptionalSkills $gemini).status -eq 'needs_gemini_consent') 'Enabling Gemini does not authorize quota use'
Check ($script:fetches -eq $beforeFetch -and $script:gitChecks -eq $beforeGit -and -not (Test-Path -LiteralPath (Join-Path $gemini '.agents'))) 'Before Gemini consent, do not retrieve, install, or probe the environment'
Must-Fail { Initialize-OptionalSkills $gemini -GeminiConsent Granted } 'Do not invent consent without a recorded response and scope'
Check ((Initialize-OptionalSkills $gemini -GeminiConsent Denied -ConsentNote 'Test denial response').status -eq 'gemini_declined') 'Save the denial response'
Check ((Initialize-OptionalSkills $gemini).status -eq 'gemini_declined' -and $script:fetches -eq $beforeFetch) 'Resumption after denial does not fetch or repeatedly ask permission'
# Granted below is solely for installing original dummy text; no external skill or Gemini connection occurs.
Check ((Initialize-OptionalSkills $gemini -GeminiConsent Granted -ConsentNote 'Simulated consent for a dummy placement test, not authorization to use a real service').status -eq 'installed') 'Install the dummy provider only after simulated consent'
Check ($script:fetches -eq ($beforeFetch + 1) -and $script:gitChecks -eq $beforeGit) 'ZIP retrieval does not require Git'
Check ((Initialize-OptionalSkills $gemini).status -eq 'ready' -and $script:fetches -eq ($beforeFetch + 1)) 'Reuse consent for the same project and pinned version'
Check ((Initialize-OptionalSkills $gemini -GeminiConsent Denied -ConsentNote 'Test withdrawal response').status -eq 'gemini_declined') 'Honor withdrawal even after installation'
$configPath = Join-Path $gemini 'config/optional-skills.json'
$changed = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
$changed.providers.'japanese-natural-writing'.revision = 'c' * 64
Write-OptionalJson $changed $configPath
Check ((Initialize-OptionalSkills $gemini).status -eq 'needs_gemini_consent') 'Do not reuse old consent after a version change'
$otherGemini = New-TestProject 'other-gemini' 'japanese-natural-writing'
Check ((Initialize-OptionalSkills $otherGemini).status -eq 'needs_gemini_consent') 'Do not transfer consent to another project'
$changed.providers.'japanese-natural-writing'.requiresGeminiConsent = $false
Write-OptionalJson $changed (Join-Path $otherGemini 'config/optional-skills.json')
Check ((Initialize-OptionalSkills $otherGemini).status -eq 'needs_gemini_consent') 'An incorrect Gemini setting cannot bypass consent'

$badContents = [ordered]@{}
foreach ($name in $contents.Keys) { $badContents[$name] = $contents[$name] }
$badContents['SKILL.md'] = 'Changed downloaded material'
$script:archive = New-TestArchive 'bad-hash' $badContents
$bad = New-TestProject 'bad-hash' 'humanizer-jp'
Must-Fail { Initialize-OptionalSkills $bad } 'Reject a downloaded hash mismatch'
Check (-not (Test-Path -LiteralPath (Join-Path $bad '.agents/skills/humanizer-jp'))) 'A failed download is not an installed skill'
$script:archive = New-TestArchive 'missing-file' ([ordered]@{'SKILL.md' = $contents['SKILL.md']})
$bad = New-TestProject 'missing-file' 'humanizer-jp'
Must-Fail { Initialize-OptionalSkills $bad } 'Reject packages missing required files such as permission notices'
$badContents['SKILL.md'] = $contents['SKILL.md']
$badContents['../outside.txt'] = 'Outside installation scope'
$script:archive = New-TestArchive 'unexpected-file' $badContents
$bad = New-TestProject 'unexpected-file' 'humanizer-jp'
Must-Fail { Initialize-OptionalSkills $bad } 'Reject unexpected files and ZIP entries escaping the project'
Check (-not (Test-Path -LiteralPath (Join-Path $bad '.agents/skills/humanizer-jp'))) 'Do not install an invalid ZIP as a usable skill'
Must-Fail { Assert-OptionalPath $bad '../escape' } 'Reject explicit paths outside the project too'

# Preserve a supplied interface definition and append only the policy.
$withPolicy = [ordered]@{'SKILL.md' = $contents['SKILL.md']; 'agents/openai.yaml' = "interface:`n  display_name: test-only`n"}
$policyHashes = [ordered]@{}
foreach ($name in $withPolicy.Keys) { $policyHashes[$name] = Text-Hash $withPolicy[$name] }
$policyProject = New-TestProject 'interface' 'humanizer-jp'
$policyConfig = Get-Content -LiteralPath (Join-Path $policyProject 'config/optional-skills.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$policyConfig.providers.'humanizer-jp'.files = [pscustomobject]$policyHashes
Write-OptionalJson $policyConfig (Join-Path $policyProject 'config/optional-skills.json')
$script:archive = New-TestArchive 'interface' $withPolicy
$null = Initialize-OptionalSkills $policyProject
$policyText = Get-Content -LiteralPath (Join-Path $policyProject '.agents/skills/humanizer-jp/agents/openai.yaml') -Raw -Encoding UTF8
Check ($policyText.Contains('display_name: test-only') -and $policyText.Contains('allow_implicit_invocation: false')) 'Preserve the interface while disabling implicit invocation'
Check ((Initialize-OptionalSkills $policyProject).status -eq 'ready') 'On resume, verify hashes including the appended policy'

# Mock only ZIP network retrieval; verify the archive hash and package subfolder.
$prefixedContents = [ordered]@{}
foreach ($name in $contents.Keys) { $prefixedContents['japanese-natural-writing/' + $name] = $contents[$name] }
$zipFixture = New-TestArchive 'prefixed' $prefixedContents
$zipSource = [pscustomobject]@{ method = 'zip'; url = 'https://note.com/api/v2/attachments/download/123abc'; revision = (Get-FileHash -LiteralPath $zipFixture).Hash.ToLowerInvariant(); prefix = 'japanese-natural-writing/'; files = [pscustomobject]$fileHashes }
function Invoke-WebRequest([switch]$UseBasicParsing, [string]$Uri, [string]$OutFile, [int]$TimeoutSec) {
    Copy-Item -LiteralPath $zipFixture -Destination $OutFile
}
$zipWork = Join-Path $testRoot 'zip-download'
$null = [IO.Directory]::CreateDirectory($zipWork)
$zipDownloaded = & $getRealArchive $zipSource $zipWork ''
Check ((Get-FileHash -LiteralPath $zipDownloaded).Hash.ToLowerInvariant() -ceq $zipSource.revision) 'Verify the pinned whole-ZIP hash on retrieval'
$zipStage = Join-Path $zipWork 'expanded'
$null = [IO.Directory]::CreateDirectory($zipStage)
Expand-OptionalArchive $zipDownloaded $zipSource $zipStage
Check ((Get-FileHash -LiteralPath (Join-Path $zipStage 'SKILL.md')).Hash.ToLowerInvariant() -ceq $fileHashes['SKILL.md']) 'Strip the package prefix when placing skill files'
$zipSource.revision = '0' * 64
Must-Fail { & $getRealArchive $zipSource $zipWork '' } 'Reject a replaced ZIP'

# Verify the real Git retrieval path offline, replacing only the fetch target with a local test repository.
if (-not $realGit) { throw 'Testing the Git retrieval path requires an installed Git executable.' }
$localRepo = Join-Path $testRoot 'local-repository'
$emptyHooks = Join-Path $testRoot 'empty-hooks'
$null = [IO.Directory]::CreateDirectory($emptyHooks)
$null = & $runRealGit $realGit @('-c', "core.hooksPath=$emptyHooks", 'init', '--quiet', $localRepo)
Write-Text (Join-Path $localRepo 'SKILL.md') $contents['SKILL.md']
$null = & $runRealGit $realGit @('-C', $localRepo, '-c', 'core.autocrlf=false', 'add', 'SKILL.md')
$null = & $runRealGit $realGit @('-C', $localRepo, '-c', "core.hooksPath=$emptyHooks", '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '--quiet', '-m', 'Test fixture')
$localRevision = & $runRealGit $realGit @('-C', $localRepo, 'rev-parse', 'HEAD')
$localSource = [pscustomobject]@{ method = 'git'; repository = 'https://github.com/test/fixture.git'; revision = $localRevision.Trim(); prefix = ''; files = [pscustomobject]@{'SKILL.md' = $fileHashes['SKILL.md']} }
function Invoke-OptionalGit([string]$Git, [string[]]$Arguments) {
    if ($Arguments -contains 'fetch') {
        $Arguments = @($Arguments | ForEach-Object { if ($_ -eq 'https://github.com/test/fixture.git') { $localRepo } else { $_ } })
    }
    return (& $runRealGit $Git $Arguments)
}
$gitWork = Join-Path $testRoot 'git-archive'
$null = [IO.Directory]::CreateDirectory($gitWork)
$savedEnvironment = @{}
foreach ($key in @('GIT_CONFIG_COUNT', 'GIT_CONFIG_KEY_0', 'GIT_CONFIG_VALUE_0')) { $savedEnvironment[$key] = [Environment]::GetEnvironmentVariable($key, 'Process') }
try {
    $env:GIT_CONFIG_COUNT = '1'
    $env:GIT_CONFIG_KEY_0 = 'core.autocrlf'
    $env:GIT_CONFIG_VALUE_0 = 'true'
    $gitArchive = & $getRealArchive $localSource $gitWork $realGit
    $gitStage = Join-Path $gitWork 'expanded'
    $null = [IO.Directory]::CreateDirectory($gitStage)
    Expand-OptionalArchive $gitArchive $localSource $gitStage
    Check ((Get-FileHash -LiteralPath (Join-Path $gitStage 'SKILL.md')).Hash.ToLowerInvariant() -ceq $fileHashes['SKILL.md']) 'Preserve pinned source text and hashes regardless of Git auto-CRLF settings'
} finally {
    foreach ($key in $savedEnvironment.Keys) { [Environment]::SetEnvironmentVariable($key, $savedEnvironment[$key], 'Process') }
}

$report = [ordered]@{ passed = $checks.Count; checks = @($checks); network = $false; externalSkills = $false; geminiCalls = 0; testedAt = [DateTimeOffset]::Now.ToString('o'); powershell = $PSVersionTable.PSVersion.ToString() }
Write-OptionalJson $report (Join-Path $testRoot 'result.json')
$report | ConvertTo-Json -Depth 10
