#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Automated Forensic & Malware Analysis Tool Installation Script (PowerShell Version)

.DESCRIPTION
    Downloads and installs forensic/analysis tools for malware analysis project
    
.NOTES
    Author: Cybersecurity Project
    Date: November 2024
    Requires: Administrator privileges
#>

# Configuration
$ErrorActionPreference = "Continue"
$ToolsDir = ".\tools"
$DownloadsDir = ".\downloads"
$LogsDir = ".\logs"

# Tool configurations
$ToolsConfig = @{
    Sysinternals = @{
        Url = "https://download.sysinternals.com/files/SysinternalsSuite.zip"
        Type = "zip"
        Destination = "$ToolsDir\sysinternals"
    }
    Wireshark = @{
        Url = "https://2.na.dl.wireshark.org/win64/Wireshark-win64-latest.exe"
        Type = "installer"
        SilentArgs = "/S /quicklaunchicon=no /desktopicon=no"
    }
    WinPMEM = @{
        Url = "https://github.com/Velocidex/WinPmem/releases/download/v4.0.rc1/winpmem_mini_x64_rc2.exe"
        Type = "portable"
        Destination = "$ToolsDir\winpmem"
    }
    ProcessMonitor = @{
        Url = "https://download.sysinternals.com/files/ProcessMonitor.zip"
        Type = "zip"
        Destination = "$ToolsDir\procmon"
    }
    TCPView = @{
        Url = "https://download.sysinternals.com/files/TCPView.zip"
        Type = "zip"
        Destination = "$ToolsDir\tcpview"
    }
}

# Create timestamp for logs
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = "$LogsDir\installation_$Timestamp.log"

# Functions
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $LogMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - [$Level] - $Message"
    Write-Host $LogMessage
    Add-Content -Path $LogFile -Value $LogMessage
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Initialize-Directories {
    Write-Log "Creating directory structure..."
    
    $Directories = @($ToolsDir, $DownloadsDir, $LogsDir)
    
    foreach ($Dir in $Directories) {
        if (-not (Test-Path $Dir)) {
            New-Item -ItemType Directory -Path $Dir -Force | Out-Null
            Write-Log "Created directory: $Dir"
        } else {
            Write-Log "Directory exists: $Dir"
        }
    }
}

function Download-File {
    param(
        [string]$Url,
        [string]$Destination
    )
    
    try {
        Write-Log "Downloading from: $Url"
        
        $WebClient = New-Object System.Net.WebClient
        
        # Progress bar
        Register-ObjectEvent -InputObject $WebClient -EventName DownloadProgressChanged -SourceIdentifier WebClient.DownloadProgressChanged -Action {
            $Global:DownloadProgress = $EventArgs.ProgressPercentage
            Write-Progress -Activity "Downloading" -Status "$Global:DownloadProgress% Complete" -PercentComplete $Global:DownloadProgress
        } | Out-Null
        
        $WebClient.DownloadFile($Url, $Destination)
        
        Unregister-Event -SourceIdentifier WebClient.DownloadProgressChanged
        Write-Progress -Activity "Downloading" -Completed
        
        Write-Log "Download completed: $Destination" -Level "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Download failed: $_" -Level "ERROR"
        return $false
    }
}

function Expand-ArchiveCustom {
    param(
        [string]$SourcePath,
        [string]$DestinationPath
    )
    
    try {
        Write-Log "Extracting $SourcePath to $DestinationPath"
        
        if (-not (Test-Path $DestinationPath)) {
            New-Item -ItemType Directory -Path $DestinationPath -Force | Out-Null
        }
        
        Expand-Archive -Path $SourcePath -DestinationPath $DestinationPath -Force
        
        Write-Log "Extraction completed" -Level "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Extraction failed: $_" -Level "ERROR"
        return $false
    }
}

function Install-Tool {
    param(
        [string]$InstallerPath,
        [string]$Arguments
    )
    
    try {
        Write-Log "Running installer: $InstallerPath $Arguments"
        
        $Process = Start-Process -FilePath $InstallerPath -ArgumentList $Arguments -Wait -PassThru -NoNewWindow
        
        if ($Process.ExitCode -eq 0) {
            Write-Log "Installation completed successfully" -Level "SUCCESS"
            return $true
        } else {
            Write-Log "Installation failed with exit code: $($Process.ExitCode)" -Level "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Installation error: $_" -Level "ERROR"
        return $false
    }
}

function Test-ToolInstallation {
    param(
        [string]$ToolName
    )
    
    $VerificationResults = @{
        Sysinternals = { Test-Path "$ToolsDir\sysinternals\procmon.exe" }
        Wireshark = { (Get-Command tshark -ErrorAction SilentlyContinue) -ne $null }
        WinPMEM = { Test-Path "$ToolsDir\winpmem\winpmem_mini_x64_rc2.exe" }
        ProcessMonitor = { Test-Path "$ToolsDir\procmon\procmon.exe" }
        TCPView = { Test-Path "$ToolsDir\tcpview\Tcpview.exe" }
    }
    
    if ($VerificationResults.ContainsKey($ToolName)) {
        $Result = & $VerificationResults[$ToolName]
        $Status = if ($Result) { "PASSED" } else { "FAILED" }
        Write-Log "Verification for $ToolName : $Status"
        return $Result
    }
    
    return $false
}

function Install-Sysinternals {
    Write-Log "=" * 50
    Write-Log "Installing Sysinternals Suite"
    Write-Log "=" * 50
    
    $Config = $ToolsConfig.Sysinternals
    $DownloadPath = "$DownloadsDir\SysinternalsSuite.zip"
    
    # Download
    if (-not (Download-File -Url $Config.Url -Destination $DownloadPath)) {
        return $false
    }
    
    # Extract
    if (-not (Expand-ArchiveCustom -SourcePath $DownloadPath -DestinationPath $Config.Destination)) {
        return $false
    }
    
    # Verify
    return Test-ToolInstallation -ToolName "Sysinternals"
}

function Install-Wireshark {
    Write-Log "=" * 50
    Write-Log "Installing Wireshark"
    Write-Log "=" * 50
    
    $Config = $ToolsConfig.Wireshark
    $DownloadPath = "$DownloadsDir\Wireshark-installer.exe"
    
    # Download
    if (-not (Download-File -Url $Config.Url -Destination $DownloadPath)) {
        return $false
    }
    
    # Install
    if (-not (Install-Tool -InstallerPath $DownloadPath -Arguments $Config.SilentArgs)) {
        return $false
    }
    
    # Verify
    return Test-ToolInstallation -ToolName "Wireshark"
}

function Install-WinPMEM {
    Write-Log "=" * 50
    Write-Log "Installing WinPMEM"
    Write-Log "=" * 50
    
    $Config = $ToolsConfig.WinPMEM
    
    if (-not (Test-Path $Config.Destination)) {
        New-Item -ItemType Directory -Path $Config.Destination -Force | Out-Null
    }
    
    $DownloadPath = "$($Config.Destination)\winpmem_mini_x64_rc2.exe"
    
    # Download
    if (-not (Download-File -Url $Config.Url -Destination $DownloadPath)) {
        return $false
    }
    
    # Verify
    return Test-ToolInstallation -ToolName "WinPMEM"
}

function Install-ProcessMonitor {
    Write-Log "=" * 50
    Write-Log "Installing Process Monitor"
    Write-Log "=" * 50
    
    $Config = $ToolsConfig.ProcessMonitor
    $DownloadPath = "$DownloadsDir\ProcessMonitor.zip"
    
    # Download
    if (-not (Download-File -Url $Config.Url -Destination $DownloadPath)) {
        return $false
    }
    
    # Extract
    if (-not (Expand-ArchiveCustom -SourcePath $DownloadPath -DestinationPath $Config.Destination)) {
        return $false
    }
    
    # Verify
    return Test-ToolInstallation -ToolName "ProcessMonitor"
}

function Install-TCPView {
    Write-Log "=" * 50
    Write-Log "Installing TCPView"
    Write-Log "=" * 50
    
    $Config = $ToolsConfig.TCPView
    $DownloadPath = "$DownloadsDir\TCPView.zip"
    
    # Download
    if (-not (Download-File -Url $Config.Url -Destination $DownloadPath)) {
        return $false
    }
    
    # Extract
    if (-not (Expand-ArchiveCustom -SourcePath $DownloadPath -DestinationPath $Config.Destination)) {
        return $false
    }
    
    # Verify
    return Test-ToolInstallation -ToolName "TCPView"
}

function New-InstallationReport {
    param(
        [hashtable]$Results
    )
    
    $ReportPath = "$LogsDir\installation_report_$Timestamp.txt"
    
    $Report = @"
============================================================
FORENSIC TOOLS INSTALLATION REPORT
============================================================

Installation Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

Installation Results:
------------------------------------------------------------
"@
    
    foreach ($Tool in $Results.Keys) {
        $Status = if ($Results[$Tool]) { "✓ SUCCESS" } else { "✗ FAILED" }
        $Report += "`n$($Tool.PadRight(20)): $Status"
    }
    
    $SuccessCount = ($Results.Values | Where-Object { $_ -eq $true }).Count
    $TotalCount = $Results.Count
    
    $Report += @"

============================================================
Summary: $SuccessCount/$TotalCount tools installed successfully

"@
    
    if ($SuccessCount -eq $TotalCount) {
        $Report += "Status: ALL TOOLS INSTALLED SUCCESSFULLY ✓`n"
    } else {
        $Report += "Status: SOME INSTALLATIONS FAILED - Review logs for details`n"
    }
    
    $Report += "============================================================`n"
    
    $Report | Out-File -FilePath $ReportPath -Encoding UTF8
    Write-Log "Installation report saved to: $ReportPath"
    
    return $ReportPath
}

# Main execution
function Main {
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "AUTOMATED FORENSIC TOOLS INSTALLATION (PowerShell)" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Check administrator privileges
    if (-not (Test-Administrator)) {
        Write-Host "ERROR: This script requires administrator privileges!" -ForegroundColor Red
        Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
        exit 1
    }
    
    Write-Log "Starting automated tool installation"
    
    # Initialize directories
    Initialize-Directories
    
    # Track results
    $Results = @{}
    
    # Install tools
    $ToolsToInstall = @(
        @{ Name = "Sysinternals"; Function = { Install-Sysinternals } },
        @{ Name = "Wireshark"; Function = { Install-Wireshark } },
        @{ Name = "WinPMEM"; Function = { Install-WinPMEM } },
        @{ Name = "ProcessMonitor"; Function = { Install-ProcessMonitor } },
        @{ Name = "TCPView"; Function = { Install-TCPView } }
    )
    
    foreach ($Tool in $ToolsToInstall) {
        try {
            Write-Host ""
            $Results[$Tool.Name] = & $Tool.Function
        }
        catch {
            Write-Log "Unexpected error installing $($Tool.Name): $_" -Level "ERROR"
            $Results[$Tool.Name] = $false
        }
    }
    
    # Generate report
    $ReportPath = New-InstallationReport -Results $Results
    
    # Print summary
    Write-Host "`n============================================================" -ForegroundColor Cyan
    Write-Host "INSTALLATION SUMMARY" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    
    foreach ($Tool in $Results.Keys) {
        $StatusIcon = if ($Results[$Tool]) { "✓" } else { "✗" }
        $Color = if ($Results[$Tool]) { "Green" } else { "Red" }
        $Status = if ($Results[$Tool]) { "SUCCESS" } else { "FAILED" }
        
        Write-Host "$StatusIcon $($Tool.PadRight(20)): $Status" -ForegroundColor $Color
    }
    
    Write-Host "`n============================================================" -ForegroundColor Cyan
    Write-Host "Detailed logs: $LogsDir" -ForegroundColor Yellow
    Write-Host "Installation report: $ReportPath" -ForegroundColor Yellow
    Write-Host "============================================================" -ForegroundColor Cyan
    
    $AllSuccess = -not ($Results.Values -contains $false)
    return $AllSuccess
}

# Execute
try {
    $Success = Main
    exit $(if ($Success) { 0 } else { 1 })
}
catch {
    Write-Host "FATAL ERROR: $_" -ForegroundColor Red
    Write-Log "Fatal error: $_" -Level "CRITICAL"
    exit 1
}
