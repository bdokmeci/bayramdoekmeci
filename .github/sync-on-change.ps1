param([switch]$Install)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$taskName = 'BayramdoekmeciGitHubAutoSync'

if ($Install) {
    $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$PSCommandPath`""
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    $settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero)
    $principal = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited

    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description 'Commits and pushes changes in the Bayramdoekmeci project.' -Force | Out-Null
    Start-ScheduledTask -TaskName $taskName
    Write-Output "Auto-sync installed and started. Task: $taskName"
    exit 0
}

$stateDirectory = Join-Path $env:LOCALAPPDATA 'BayramdoekmeciGitHubAutoSync'
New-Item -ItemType Directory -Path $stateDirectory -Force | Out-Null
$signalPath = Join-Path $stateDirectory 'pending-change'
$logPath = Join-Path $stateDirectory 'sync.log'
$gitDirectory = Join-Path $repoRoot '.git'

function Write-SyncLog([string]$message) {
    Add-Content -Path $logPath -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $message"
}

function Invoke-Git([string[]]$gitArguments) {
    $output = & git -C $repoRoot @gitArguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "git $($gitArguments -join ' ') failed: $($output -join [Environment]::NewLine)"
    }
    return $output
}

$watcher = [System.IO.FileSystemWatcher]::new($repoRoot)
$watcher.IncludeSubdirectories = $true
$watcher.NotifyFilter = [System.IO.NotifyFilters]::FileName -bor [System.IO.NotifyFilters]::DirectoryName -bor [System.IO.NotifyFilters]::LastWrite
$watcher.EnableRaisingEvents = $true

$eventAction = {
    $message = $Event.MessageData
    $eventArgs = $Event.SourceEventArgs
    $changedPaths = @($eventArgs.FullPath)
    if ($eventArgs.PSObject.Properties['OldFullPath']) {
        $changedPaths += $eventArgs.OldFullPath
    }

    foreach ($changedPath in $changedPaths) {
        $gitDirectoryPrefix = $message.GitDirectory + [System.IO.Path]::DirectorySeparatorChar
        $isGitMetadata = $changedPath.Equals($message.GitDirectory, [StringComparison]::OrdinalIgnoreCase) -or $changedPath.StartsWith($gitDirectoryPrefix, [StringComparison]::OrdinalIgnoreCase)
        if (-not $isGitMetadata) {
            [System.IO.File]::WriteAllText($message.SignalPath, [DateTime]::UtcNow.Ticks.ToString())
            break
        }
    }
}

$eventData = @{ SignalPath = $signalPath; GitDirectory = $gitDirectory }
foreach ($eventName in 'Changed', 'Created', 'Deleted', 'Renamed') {
    Register-ObjectEvent -InputObject $watcher -EventName $eventName -SourceIdentifier "BayramGitSync$eventName" -MessageData $eventData -Action $eventAction | Out-Null
}

Write-SyncLog "Watcher started for $repoRoot"
$lastHandledSignal = 0L
$lastPushAttempt = [DateTime]::MinValue

while ($true) {
    Start-Sleep -Milliseconds 500

    if (Test-Path $signalPath) {
        $signalTicks = [Int64](Get-Content -Path $signalPath -Raw)
        if ($signalTicks -gt $lastHandledSignal -and ([DateTime]::UtcNow.Ticks - $signalTicks) -ge [TimeSpan]::FromSeconds(2).Ticks) {
            $lastHandledSignal = $signalTicks
            try {
                Invoke-Git @('add', '--all') | Out-Null
                & git -C $repoRoot diff --cached --quiet
                $diffExitCode = $LASTEXITCODE
                if ($diffExitCode -eq 1) {
                    $commitMessage = "Auto-sync: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
                    Invoke-Git @('commit', '-m', $commitMessage) | Out-Null
                    Invoke-Git @('push', 'origin', 'main') | Out-Null
                    $lastPushAttempt = [DateTime]::UtcNow
                    Write-SyncLog "Committed and pushed: $commitMessage"
                }
                elseif ($diffExitCode -ne 0) {
                    throw "git diff --cached --quiet failed with exit code $diffExitCode"
                }
            }
            catch {
                Write-SyncLog "ERROR: $($_.Exception.Message)"
            }
        }
    }

    if (([DateTime]::UtcNow - $lastPushAttempt) -ge [TimeSpan]::FromSeconds(30)) {
        try {
            Invoke-Git @('push', 'origin', 'main') | Out-Null
            $lastPushAttempt = [DateTime]::UtcNow
        }
        catch {
            Write-SyncLog "ERROR: $($_.Exception.Message)"
            $lastPushAttempt = [DateTime]::UtcNow
        }
    }
}
