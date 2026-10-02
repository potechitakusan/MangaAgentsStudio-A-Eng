#requires -Version 5.1
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$maker = Join-Path $root 'scripts\New-MangaProject.ps1'
$resolver = Join-Path $root 'scripts\Resolve-ReviewProfile.ps1'
$testRoot = Join-Path $root ('.work\scaffold-' + [Guid]::NewGuid().ToString('N'))
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
function Write-Json($Value, [string]$Path) {
    [IO.File]::WriteAllText($Path, ($Value | ConvertTo-Json -Depth 20), [Text.UTF8Encoding]::new($false))
}
# Intentional Unicode compatibility coverage: Japanese project names must survive scaffolding.
$japaneseName = ([string][char]0x661f) + [char]0x6e21 + [char]0x308a + ' Test'
# Create only empty distribution-test projects in .work/; do not produce comics here.
$result = & $maker -ProjectName $japaneseName -DestinationParent $testRoot -InformationVariable creationMessages
$projectRoot = (Resolve-Path -LiteralPath $result.Path).ProviderPath
Check (@($result).Count -eq 1) 'Reopening guidance does not contaminate the script return value'
Check (([IO.Path]::IsPathRooted($result.AbsolutePath)) -and ($result.AbsolutePath -eq $projectRoot) -and
       (-not [IO.Path]::IsPathRooted($result.Path))) 'The display absolute path matches the actual project and preserves the relative path'
$creationText = ($creationMessages | Out-String -Width 4096)
Check ($creationText.Contains($projectRoot) -and $creationText.Contains('Reopen Codex in this folder')) 'Reopening guidance includes the full destination'
$project = Get-Content -LiteralPath (Join-Path $projectRoot 'project.json') -Raw -Encoding UTF8 | ConvertFrom-Json
Check ($project.name -ceq $japaneseName) 'Japanese project name survives JSON round trip'
Check ((Split-Path $projectRoot -Parent) -eq $testRoot) 'Project is a direct child of the selected parent'
Check (@(Get-ChildItem -LiteralPath (Join-Path $projectRoot '.agents\skills') -Directory).Count -eq 10) 'Ten skills include supervision, process checking, and external panel generation'
Check ((Test-Path -LiteralPath (Join-Path $projectRoot '.agents/skills/manga-process-checker/SKILL.md')) -and
       (Test-Path -LiteralPath (Join-Path $projectRoot 'scripts/process_checker.py')) -and
       (Test-Path -LiteralPath (Join-Path $projectRoot 'docs/knowledge/process-checker.md'))) 'Process checker procedure, management script, and knowledge are distributed'
$processRequirements = Get-Content -LiteralPath (Join-Path $projectRoot 'config/process-requirements.json') -Raw -Encoding UTF8 | ConvertFrom-Json
Check ($processRequirements.schemaVersion -eq 1 -and $processRequirements.requirements.Count -eq 0 -and
       -not (Test-Path -LiteralPath (Join-Path $projectRoot '.codex/hooks.json'))) 'New projects without carry-forward contain no personal requirements or Hooks'
Check ((Test-Path -LiteralPath (Join-Path $projectRoot 'scripts/Initialize-OptionalSkills.ps1')) -and
       (Test-Path -LiteralPath (Join-Path $projectRoot 'config/optional-skills.json')) -and
       (Test-Path -LiteralPath (Join-Path $projectRoot 'docs/knowledge/optional-skills.md'))) 'Editing-skill initialization, source settings, and consent procedures are distributed'
Check (-not (Test-Path -LiteralPath (Join-Path $projectRoot '.agents/skills/humanizer-jp')) -and
       -not (Test-Path -LiteralPath (Join-Path $projectRoot '.agents/skills/japanese-natural-writing')) -and
       -not (Test-Path -LiteralPath (Join-Path $projectRoot '.work/optional-skills'))) 'Third-party skills and consent are not carried into new projects'
$optionalState = & (Join-Path $projectRoot 'scripts/Initialize-OptionalSkills.ps1')
Check ($optionalState.status -eq 'disabled' -and -not (Test-Path -LiteralPath (Join-Path $projectRoot '.work/optional-skills'))) 'Default initialization finishes without retrieving optional skills'
Check ((Test-Path -LiteralPath (Join-Path $projectRoot '.agents\skills\manga-supervision\SKILL.md')) -and
       (Test-Path -LiteralPath (Join-Path $projectRoot 'docs\reviews\SUPERVISION.md'))) 'Supervision skill and scene consultation/review forms are available'
$knowledgeManifest = Get-Content -LiteralPath (Join-Path $root 'docs\knowledge\supervision\distribution.json') -Raw -Encoding UTF8 | ConvertFrom-Json
Check ((Test-Path -LiteralPath (Join-Path $projectRoot 'docs\knowledge\manga\03-beat-pacing-timing.md')) -and
       (Test-Path -LiteralPath (Join-Path $projectRoot 'docs\knowledge\supervision\distribution.json'))) 'Production knowledge is distributed under docs/knowledge'
Check (@($knowledgeManifest.files | Where-Object {
    -not (Test-Path -LiteralPath (Join-Path $projectRoot $_) -PathType Leaf)
}).Count -eq 0) 'Bundled supervision documents and sources are accessible within the project'
Check ((Get-ChildItem -LiteralPath (Join-Path $projectRoot 'docs/knowledge/supervision') -Recurse -File).Count -eq ($knowledgeManifest.files.Count + 1)) 'Distributed supervision files match the manifest'
Check ((@(Get-ChildItem -LiteralPath (Join-Path $projectRoot 'docs/knowledge/supervision') -Directory | Sort-Object Name).Name -join ',') -eq 'allure,awkwardness,bargaining,conflict,endearment,gag,grief,horror,payoff,reconciliation,revelation,romance,stature,trust,tsukkomi,urgency') 'Only comedy and the 15 additional themes are distributed'
Check ((Test-Path -LiteralPath (Join-Path $projectRoot 'docs\knowledge\story-structure.md')) -and
       (Test-Path -LiteralPath (Join-Path $projectRoot 'docs\knowledge\japanese-manga-readability.md'))) 'Knowledge is included'
Check ((Test-Path -LiteralPath (Join-Path $projectRoot 'templates\panel-templates\catalog.json')) -and
       (Test-Path -LiteralPath (Join-Path $projectRoot 'config\panel-layout-policy.json')) -and
       (Test-Path -LiteralPath (Join-Path $projectRoot 'scripts\validate_panel_plan.py')) -and
       (Test-Path -LiteralPath (Join-Path $projectRoot 'docs\knowledge\panel-layout-policy.md')) -and
       (Test-Path -LiteralPath (Join-Path $projectRoot 'templates\panel-templates\index.html'))) 'Panel catalog, settings, and validation script are bundled'
$panelCatalog = Get-Content -Encoding UTF8 -Raw -LiteralPath (Join-Path $projectRoot 'templates\panel-templates\catalog.json') | ConvertFrom-Json
$missingPanelAssets = @($panelCatalog.templates | ForEach-Object {
    $_.assets.PSObject.Properties | ForEach-Object {
        if (-not (Test-Path -LiteralPath (Join-Path $projectRoot ('templates\panel-templates\' + $_.Value)) -PathType Leaf)) { $_.Value }
    }
})
Check ($panelCatalog.templateCount -eq 79 -and $missingPanelAssets.Count -eq 0) 'SVG, PNG, and individual JSON assets exist for all 79 templates'
Check ((Get-FileHash -LiteralPath (Join-Path $projectRoot 'docs\toolkit-license.txt')).Hash -eq
       (Get-FileHash -LiteralPath (Join-Path $root 'LICENSE')).Hash) 'Bundled kit license matches the original'
Check ((Test-Path -LiteralPath (Join-Path $projectRoot 'OPTION.md') -PathType Leaf) -and
       (Test-Path -LiteralPath (Join-Path $projectRoot 'docs\knowledge\project-options.md') -PathType Leaf)) 'Production options and fallback application procedures are bundled'
Check ((Test-Path -LiteralPath (Join-Path $projectRoot 'PRINT-OPTION.md')) -and
       (Test-Path -LiteralPath (Join-Path $projectRoot 'docs\knowledge\page-layout.md')) -and
       (Test-Path -LiteralPath (Join-Path $projectRoot 'scripts\prepare_page_layout.py'))) 'Separate print options and Web basic-frame guidance/tools are distributed'
Check ((Test-Path -LiteralPath (Join-Path $projectRoot 'scripts\typeset_manga.py') -PathType Leaf) -and
       (Get-Content -LiteralPath (Join-Path $projectRoot 'docs\reviews\NAME-REVIEW.md') -Raw -Encoding UTF8).Contains('## Post-artwork comparison')) 'Typesetting script and pre-typesetting artwork comparison form are distributed'
Check ((Test-Path -LiteralPath (Join-Path $projectRoot 'scripts\novelai_batch.py') -PathType Leaf) -and
       (Test-Path -LiteralPath (Join-Path $projectRoot 'docs\production\NOVELAI-BATCH.md') -PathType Leaf)) 'NovelAI batch generation, selection, rebuild tools, and record templates are distributed'
$pageConfig = Get-Content -LiteralPath (Join-Path $projectRoot 'config\page-layout.json') -Raw -Encoding UTF8 | ConvertFrom-Json
Check ($pageConfig.schemaVersion -eq 2 -and $null -eq $pageConfig.generationCanvas -and
       $null -eq $pageConfig.canvas -and $null -eq $pageConfig.exportCanvas -and
       $pageConfig.referenceCanvas.width -eq 2000 -and $pageConfig.referenceCanvas.height -eq 3000 -and
       $pageConfig.basicFrame.left -eq 120 -and $pageConfig.textSafeArea.left -eq 160 -and
       $pageConfig.frameStroke -eq 10 -and
       $pageConfig.showGuide -eq $false) 'Automatic generation, placement, and PNG dimensions remain separate from margin/stroke baselines'
Check ($project.distributionVersion -eq (Get-Content -LiteralPath (Join-Path $root 'distribution-version.txt') -Raw).Trim()) 'Project distribution version matches the source version'
Check (@(Get-ChildItem -LiteralPath (Join-Path $projectRoot '.secrets') -Force).Count -eq 0) 'Secret directory starts empty'
$snapshot = Get-Content -LiteralPath (Join-Path $projectRoot 'docs\distribution-snapshot.json') -Raw -Encoding UTF8 | ConvertFrom-Json
Check (@($project.PSObject.Properties | Where-Object { $_.Name -match 'Path' -and [IO.Path]::IsPathRooted([string]$_.Value) }).Count -eq 0 -and
       @($snapshot.files | Where-Object { [IO.Path]::IsPathRooted($_.path) }).Count -eq 0) 'Absolute creation paths are not saved in project settings or distribution records'
Check (-not [string]::IsNullOrWhiteSpace($project.sourceKitRelativePath) -and
       ((Resolve-Path -LiteralPath (Join-Path $projectRoot $project.sourceKitRelativePath)).ProviderPath -eq $root)) 'Source relative path resolves from the project root to the actual kit'
$hashesValid = $true
foreach ($entry in $snapshot.files) {
    if ((Get-FileHash -LiteralPath (Join-Path $projectRoot $entry.path)).Hash -ne $entry.sha256) { $hashesValid = $false }
}
Check $hashesValid 'Every distributed file matches its recorded SHA-256'
Check ((Get-Content -LiteralPath (Join-Path $projectRoot '.gitignore') -Raw -Encoding UTF8).Contains('/config/process-requirements.json')) 'Project Git ignores personal process requirements'
# Carry forward only requirements from the explicit source; leave execution records and Hooks there.
$processSource = Join-Path $testRoot 'process-source'
$null = [IO.Directory]::CreateDirectory((Join-Path $processSource 'config'))
$null = [IO.Directory]::CreateDirectory((Join-Path $processSource '.work/process-checker'))
$null = [IO.Directory]::CreateDirectory((Join-Path $processSource '.codex'))
Write-Json ([ordered]@{ schemaVersion = 1; name = 'Requirements Source Project' }) (Join-Path $processSource 'project.json')
$inheritedRule = [ordered]@{
    id = 'proc-review'; level = 'strong-instruction'; instruction = 'Review character actions after completing the panel script'
    checkpoint = 'script-complete'; scope = 'project'; condition = 'When creating or revising the panel script'
    completionCriteria = 'The target manuscript and review exist'; carryForward = $true; enforcement = 'agents+hooks'
    decision = 'discussed'; decisionNote = 'Test registration fixture'
}
$localRule = [ordered]@{}
foreach ($key in $inheritedRule.Keys) { $localRule[$key] = $inheritedRule[$key] }
$localRule.id = 'proc-local'
$localRule.carryForward = $false
Write-Json ([ordered]@{ schemaVersion = 1; requirements = @($inheritedRule, $localRule) }) (Join-Path $processSource 'config/process-requirements.json')
Write-Json ([ordered]@{ private = 'Previous project execution record' }) (Join-Path $processSource '.work/process-checker/state.json')
Write-Json ([ordered]@{ private = 'Previous project Hooks' }) (Join-Path $processSource '.codex/hooks.json')
$sourceRequirementsHash = (Get-FileHash -LiteralPath (Join-Path $processSource 'config/process-requirements.json')).Hash
$null = & $maker -ProjectName 'InheritedPreview' -DestinationParent $testRoot -ProcessRequirementsFrom $processSource -WhatIf
Check (-not (Test-Path -LiteralPath (Join-Path $testRoot 'InheritedPreview'))) 'WhatIf with carry-forward creates no project'
$inheritedResult = & $maker -ProjectName 'Inherited' -DestinationParent $testRoot -ProcessRequirementsFrom $processSource
$inheritedRoot = $inheritedResult.AbsolutePath
$inheritedData = Get-Content -LiteralPath (Join-Path $inheritedRoot 'config/process-requirements.json') -Raw -Encoding UTF8 | ConvertFrom-Json
Check ($inheritedData.requirements.Count -eq 1 -and $inheritedData.requirements[0].id -eq 'proc-review') 'Only eligible requirements reach the next project'
Check ((Get-Content -LiteralPath (Join-Path $inheritedRoot 'AGENTS.md') -Raw -Encoding UTF8).Contains('proc-review') -and
       -not (Test-Path -LiteralPath (Join-Path $inheritedRoot '.work/process-checker/state.json')) -and
       -not (Test-Path -LiteralPath (Join-Path $inheritedRoot '.codex/hooks.json'))) 'Strong requirements enter AGENTS without copying execution records or Hooks'
$inheritedProject = Get-Content -LiteralPath (Join-Path $inheritedRoot 'project.json') -Raw -Encoding UTF8 | ConvertFrom-Json
Check (-not [IO.Path]::IsPathRooted($inheritedProject.processRequirementsSourceRelativePath) -and
       (Resolve-Path -LiteralPath (Join-Path $inheritedRoot $inheritedProject.processRequirementsSourceRelativePath)).ProviderPath -eq $processSource) 'Carry-forward source is recorded as a correct relative path'
$inheritedSnapshot = Get-Content -LiteralPath (Join-Path $inheritedRoot 'docs/distribution-snapshot.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$inheritedHashesValid = $true
foreach ($entry in $inheritedSnapshot.files) {
    if ((Get-FileHash -LiteralPath (Join-Path $inheritedRoot $entry.path)).Hash -ne $entry.sha256) { $inheritedHashesValid = $false }
}
Check $inheritedHashesValid 'Inherited AGENTS and requirements match creation-time hashes'
Check ((Get-FileHash -LiteralPath (Join-Path $processSource 'config/process-requirements.json')).Hash -eq $sourceRequirementsHash) 'Source requirements remain unchanged'
$originalHash = (Get-FileHash -LiteralPath (Join-Path $projectRoot 'project.json')).Hash
Must-Fail { & $maker -ProjectName $japaneseName -DestinationParent $testRoot } 'Existing project is rejected'
# Codex is the default; environment-specific files require explicit mode selection.
Check ($project.agentMode -eq 'Codex' -and
       -not (Test-Path -LiteralPath (Join-Path $projectRoot 'CLAUDE.md')) -and
       -not (Test-Path -LiteralPath (Join-Path $projectRoot 'GEMINI.md')) -and
       -not (Test-Path -LiteralPath (Join-Path $projectRoot 'AGENT-MODE.md')) -and
       -not (Test-Path -LiteralPath (Join-Path $projectRoot 'agent-modes'))) 'Default Codex mode creates no other environment-specific files'
$claudeResult = & $maker -ProjectName 'ClaudeMode' -DestinationParent $testRoot -AgentMode Claude -InformationVariable claudeMessages
$claudeRoot = (Resolve-Path -LiteralPath $claudeResult.Path).ProviderPath
$claudeProject = Get-Content -LiteralPath (Join-Path $claudeRoot 'project.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$claudeSnapshot = Get-Content -LiteralPath (Join-Path $claudeRoot 'docs\distribution-snapshot.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$claudeFiles = @($claudeSnapshot.files | Where-Object { $_.path -in @('CLAUDE.md', 'AGENT-MODE.md') })
Check ($claudeProject.agentMode -eq 'Claude' -and $claudeResult.AgentMode -eq 'Claude' -and $claudeFiles.Count -eq 2 -and
       @($claudeFiles | Where-Object { $_.sha256 -ne (Get-FileHash -LiteralPath (Join-Path $claudeRoot $_.path) -Algorithm SHA256).Hash.ToLowerInvariant() }).Count -eq 0 -and
       (Get-Content -LiteralPath (Join-Path $claudeRoot 'CLAUDE.md') -Raw -Encoding UTF8).Contains('@AGENTS.md') -and
       -not (Test-Path -LiteralPath (Join-Path $claudeRoot 'agent-modes'))) 'Claude mode distributes and records CLAUDE.md and adaptation instructions'
Check (($claudeMessages | Out-String -Width 4096).Contains('Reopen Claude in this folder')) 'Claude mode instructs reopening in Claude'
Check (-not (Test-Path -LiteralPath (Join-Path $claudeRoot 'GEMINI.md'))) 'Claude mode does not distribute the Antigravity entry point'
$antigravityResult = & $maker -ProjectName 'AntigravityMode' -DestinationParent $testRoot -AgentMode Antigravity -InformationVariable antigravityMessages
$antigravityRoot = (Resolve-Path -LiteralPath $antigravityResult.Path).ProviderPath
$antigravityProject = Get-Content -LiteralPath (Join-Path $antigravityRoot 'project.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$antigravitySnapshot = Get-Content -LiteralPath (Join-Path $antigravityRoot 'docs\distribution-snapshot.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$antigravityFiles = @($antigravitySnapshot.files | Where-Object { $_.path -in @('GEMINI.md', 'AGENT-MODE.md') })
Check ($antigravityProject.agentMode -eq 'Antigravity' -and $antigravityResult.AgentMode -eq 'Antigravity' -and $antigravityFiles.Count -eq 2 -and
       @($antigravityFiles | Where-Object { $_.sha256 -ne (Get-FileHash -LiteralPath (Join-Path $antigravityRoot $_.path) -Algorithm SHA256).Hash.ToLowerInvariant() }).Count -eq 0 -and
       (Get-Content -LiteralPath (Join-Path $antigravityRoot 'GEMINI.md') -Raw -Encoding UTF8).Contains('@[Antigravity adaptations](AGENT-MODE.md)') -and
       -not (Test-Path -LiteralPath (Join-Path $antigravityRoot 'CLAUDE.md')) -and
       -not (Test-Path -LiteralPath (Join-Path $antigravityRoot 'agent-modes'))) 'Distribute and record only the two Antigravity mode files'
Check ((Get-FileHash -LiteralPath (Join-Path $antigravityRoot 'AGENTS.md')).Hash -eq (Get-FileHash -LiteralPath (Join-Path $projectRoot 'AGENTS.md')).Hash -and
       (Get-FileHash -LiteralPath (Join-Path $antigravityRoot 'OPTION.md')).Hash -eq (Get-FileHash -LiteralPath (Join-Path $projectRoot 'OPTION.md')).Hash) 'Antigravity retains common rules and default options'
Check (($antigravityMessages | Out-String -Width 4096).Contains('Reopen Antigravity in this folder')) 'Antigravity mode gives reopening guidance'
$null = & $maker -ProjectName 'AntigravityPreviewOnly' -DestinationParent $testRoot -AgentMode Antigravity -WhatIf -InformationVariable antigravityPreviewMessages
Check (-not (Test-Path -LiteralPath (Join-Path $testRoot 'AntigravityPreviewOnly')) -and
       -not (($antigravityPreviewMessages | Out-String).Contains('Reopen Antigravity in this folder'))) 'Antigravity WhatIf neither creates files nor reports completion'
Must-Fail { & $maker -ProjectName 'UnknownMode' -DestinationParent $testRoot -AgentMode 'Gemini' } 'Unsupported agent mode is rejected'
Check ((Get-FileHash -LiteralPath (Join-Path $projectRoot 'project.json')).Hash -eq $originalHash) 'Existing project remains unchanged'
$previewResult = & $maker -ProjectName 'PreviewOnly' -DestinationParent $testRoot -WhatIf -InformationVariable previewMessages
Check (-not (Test-Path -LiteralPath (Join-Path $testRoot 'PreviewOnly'))) 'WhatIf does not create files'
Check ($null -eq $previewResult -and -not (($previewMessages | Out-String).Contains('Reopen Codex in this folder'))) 'WhatIf reports neither completed creation nor reopening instructions'
$null = & $maker -ProjectName 'PreviewOnly' -WhatIf
Check (-not (Test-Path -LiteralPath (Join-Path (Split-Path $root -Parent) 'PreviewOnly'))) 'Default sibling destination preview is read only'
Must-Fail { & $maker -ProjectName '..\escape' -DestinationParent $testRoot } 'Path traversal is rejected'
Must-Fail { & $maker -ProjectName 'CON' -DestinationParent $testRoot } 'Windows reserved device name is rejected'
$reservedUnicode = 'COM' + [char]0x00b9
Must-Fail { & $maker -ProjectName $reservedUnicode -DestinationParent $testRoot -WhatIf } 'Unicode Windows reserved device name is rejected in PS5.1'
$null = & $maker -ProjectName 'CodexMangaPreviewOnly' -DestinationParent ([IO.Path]::GetPathRoot($root)) -WhatIf
Check $true 'Drive root is accepted as an output parent for preview'
$profilePath = Join-Path $projectRoot 'config\review-profiles.json'
$effective = & (Join-Path $projectRoot 'scripts\Resolve-ReviewProfile.ps1') -ConfigPath $profilePath -Preset 'battle'
Check ($effective.weights.cinema -eq 5 -and $effective.weights.story -eq 4) 'Distributed resolver applies preset and inherits defaults'
$config = Get-Content -LiteralPath $profilePath -Raw -Encoding UTF8 | ConvertFrom-Json
$config.scenes | Add-Member -NotePropertyName 'scene-001' -NotePropertyValue ([pscustomobject]@{
    preset = 'confession'; weights = [pscustomobject]@{ cinema = 5; terminology = 1 }; reason = 'Test override'
})
Write-Json $config $profilePath
$effective = & $resolver -ConfigPath $profilePath -Preset 'daily' -SceneId 'scene-001'
Check ($effective.preset -eq 'confession' -and $effective.weights.story -eq 4 -and
       $effective.weights.cinema -eq 5 -and $effective.weights.terminology -eq 1) 'Scene preset overrides requested preset; scene weights apply last'
Must-Fail { & $resolver -ConfigPath $profilePath -SceneId 'missing' } 'Unknown scene is rejected'
Must-Fail { & $resolver -ConfigPath $profilePath -Preset 'missing' } 'Unknown preset is rejected'
$badPath = Join-Path $testRoot 'bad-profile.json'
foreach ($invalid in @(0, 6, 2.5, '5', $true)) {
    $config.defaults.immersion = $invalid
    Write-Json $config $badPath
    Must-Fail { & $resolver -ConfigPath $badPath } "Invalid weight rejected: $invalid"
}
$config.defaults.immersion = 5
$config.defaults | Add-Member -NotePropertyName 'misspelled' -NotePropertyValue 3
Write-Json $config $badPath
Must-Fail { & $resolver -ConfigPath $badPath } 'Misspelled weight key is rejected'

# Use an isolated packaging fixture to prove accidental secret files are rejected.
$fixture = Join-Path $testRoot 'source-fixture'
$null = [IO.Directory]::CreateDirectory($fixture)
foreach ($directory in @('scripts', 'templates', 'skills')) {
    Copy-Item -LiteralPath (Join-Path $root $directory) -Destination (Join-Path $fixture $directory) -Recurse
}
$null = [IO.Directory]::CreateDirectory((Join-Path $fixture 'docs'))
Copy-Item -LiteralPath (Join-Path $root 'docs\knowledge') -Destination (Join-Path $fixture 'docs\knowledge') -Recurse
Copy-Item -LiteralPath (Join-Path $root 'distribution-version.txt') -Destination (Join-Path $fixture 'distribution-version.txt')
Copy-Item -LiteralPath (Join-Path $root 'LICENSE') -Destination (Join-Path $fixture 'LICENSE')
foreach ($relative in @('docs/knowledge/supervision/unlisted.md',
                         'docs/knowledge/supervision/gag/unlisted.md',
                         'docs/knowledge/supervision/tsukkomi/unlisted.md',
                         'docs/knowledge/supervision/allure/unlisted.md',
                         'docs/knowledge/supervision/stature/unlisted.md',
                         'docs/knowledge/supervision/horror/unlisted.md',
                         'docs/knowledge/supervision/conflict/unlisted.md',
                         'docs/knowledge/supervision/grief/unlisted.md',
                         'docs/knowledge/supervision/romance/unlisted.md',
                         'docs/knowledge/supervision/trust/unlisted.md',
                         'docs/knowledge/supervision/awkwardness/unlisted.md',
                         'docs/knowledge/supervision/urgency/unlisted.md',
                         'docs/knowledge/supervision/revelation/unlisted.md',
                         'docs/knowledge/supervision/payoff/unlisted.md',
                         'docs/knowledge/supervision/endearment/unlisted.md',
                         'docs/knowledge/supervision/bargaining/unlisted.md',
                         'docs/knowledge/supervision/reconciliation/unlisted.md',
                         'docs/knowledge/supervision/unreleased-theme/README.md')) {
    $destination = Join-Path $fixture $relative
    $null = [IO.Directory]::CreateDirectory((Split-Path $destination -Parent))
    [IO.File]::WriteAllText($destination, 'File absent from manifest')
}
$fixtureResult = & (Join-Path $fixture 'scripts\New-MangaProject.ps1') -ProjectName 'WithUnlistedFiles' -DestinationParent $testRoot
$fixtureProject = (Resolve-Path -LiteralPath $fixtureResult.Path).ProviderPath
Check (@(Get-ChildItem -LiteralPath (Join-Path $fixtureProject 'docs/knowledge/supervision') -Recurse -File | Where-Object {
    $_.Name -eq 'unlisted.md'
}).Count -eq 0 -and -not (Test-Path -LiteralPath (Join-Path $fixtureProject 'docs/knowledge/supervision/unreleased-theme'))) 'Unlisted files and unsupported themes are not distributed to projects'
# Reject disallowed paths before creation even if added to the manifest.
$fixtureManifest = Join-Path $fixture 'docs\knowledge\supervision\distribution.json'
foreach ($unlistedPath in @('docs/knowledge/supervision/unlisted.md',
                           'docs/knowledge/supervision/gag/unlisted.md',
                           'docs/knowledge/supervision/tsukkomi/unlisted.md',
                           'docs/knowledge/supervision/allure/unlisted.md',
                           'docs/knowledge/supervision/stature/unlisted.md',
                           'docs/knowledge/supervision/horror/unlisted.md',
                           'docs/knowledge/supervision/conflict/unlisted.md',
                           'docs/knowledge/supervision/grief/unlisted.md',
                           'docs/knowledge/supervision/romance/unlisted.md',
                           'docs/knowledge/supervision/trust/unlisted.md',
                           'docs/knowledge/supervision/awkwardness/unlisted.md',
                           'docs/knowledge/supervision/urgency/unlisted.md',
                           'docs/knowledge/supervision/revelation/unlisted.md',
                           'docs/knowledge/supervision/payoff/unlisted.md',
                           'docs/knowledge/supervision/endearment/unlisted.md',
                           'docs/knowledge/supervision/bargaining/unlisted.md',
                           'docs/knowledge/supervision/reconciliation/unlisted.md',
                           'docs/knowledge/supervision/unreleased-theme/README.md')) {
    $badKnowledge = [ordered]@{ schemaVersion = 1; files = @($knowledgeManifest.files) + @($unlistedPath) }
    Write-Json $badKnowledge $fixtureManifest
    Must-Fail { & (Join-Path $fixture 'scripts\New-MangaProject.ps1') -ProjectName 'RejectedEntries' -DestinationParent $testRoot } "Reject a disallowed manifest path: $unlistedPath"
}
Check (-not (Test-Path -LiteralPath (Join-Path $testRoot 'RejectedEntries'))) 'Invalid knowledge distribution creates no project folder'
Write-Json $knowledgeManifest $fixtureManifest
[IO.File]::WriteAllText((Join-Path $fixture 'templates\manga-project\.env'), '# Empty accidental private config')
Must-Fail { & (Join-Path $fixture 'scripts\New-MangaProject.ps1') -ProjectName 'RejectedSecrets' -DestinationParent $testRoot } 'Accidental private configuration in template is rejected'
Check (-not (Test-Path -LiteralPath (Join-Path $testRoot 'RejectedSecrets'))) 'Invalid package leaves no target directory'
$report = [ordered]@{ passed = $checks.Count; checks = @($checks); pathBase = '.'; output = $japaneseName; testedAt = [DateTimeOffset]::Now.ToString('o'); powershell = $PSVersionTable.PSVersion.ToString() }
Write-Json $report (Join-Path $testRoot 'result.json')
$report | ConvertTo-Json -Depth 10
