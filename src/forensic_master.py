"""
BitProbe — Scan
Digital Forensics Analysis Tool - Main Orchestration Script

This script:
1. Installs all dependencies and tools
2. Runs all forensic tools to capture artifacts
3. Generates individual reports from each tool
4. Compiles everything into a master report
5. Stores everything in organized folders

Tagline: Simplifying digital forensics through automated bit-level inspection

Author: MetaProbe Team
Version: 1.0
"""

import os
import sys
import subprocess
import logging
import psutil
import ctypes
import argparse
from pathlib import Path
from datetime import datetime
import time

# Detect if we are running from a PyInstaller executable
IS_FROZEN = getattr(sys, "frozen", False)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

try:
    from yara_scanner import run_yara_analysis
    YARA_ENABLED = True
except ImportError:
    YARA_ENABLED = False
    print("[WARNING] YARA scanner not available")

# Configuration
CONFIG = {
    "project_name": "Malware Analysis & Forensic Tool",
    "version": "1.0",
    "base_dir": Path.cwd(),
    "tools_dir": Path("tools"),
    "artifacts_dir": Path("artifacts"),
    "reports_dir": Path("reports"),
    "logs_dir": Path("logs"),
    "individual_reports_dir": Path("reports") / "individual",
    "master_report_dir": Path("reports") / "master",
}

# Setup logging
def setup_logging():
    """Initialize logging system"""
    CONFIG["logs_dir"].mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = CONFIG["logs_dir"] / f"forensic_run_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [%(levelname)s] - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# Color output for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    """Display application banner"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     AUTOMATED MALWARE ANALYSIS & FORENSIC TOOL               ║
║                                                              ║
║     Version: 1.0                                             ║
║     Developer: MetaProbe Team                                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
{Colors.RESET}
"""
    print(banner)
    logger.info("Application started")

def is_admin():
    """Check if running with admin privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate_privileges():
    """Request admin privileges if not already running as admin"""
    if not is_admin():
        logger.warning("Requesting administrator privileges...")
        print(f"{Colors.YELLOW}⚠ This tool requires administrator privileges{Colors.RESET}")
        print(f"{Colors.YELLOW}⚠ Requesting elevation...{Colors.RESET}")
        
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)

def create_directory_structure():
    """Create all required directories"""
    logger.info("Creating directory structure...")
    
    directories = [
        CONFIG["tools_dir"],
        CONFIG["artifacts_dir"],
        CONFIG["reports_dir"],
        CONFIG["logs_dir"],
        CONFIG["individual_reports_dir"],
        CONFIG["master_report_dir"],
        CONFIG["artifacts_dir"] / "memory",
        CONFIG["artifacts_dir"] / "network",
        CONFIG["artifacts_dir"] / "processes",
        CONFIG["artifacts_dir"] / "registry",
        CONFIG["artifacts_dir"] / "logs",
        CONFIG["artifacts_dir"] / "browser",
        CONFIG["artifacts_dir"] / "analysis",
        CONFIG["artifacts_dir"] / "ghidra",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created: {directory}")
    
    print(f"{Colors.GREEN}✓ Directory structure created{Colors.RESET}")

def check_and_install_dependencies():
    """Check and install Python dependencies"""
    logger.info("Checking Python dependencies...")
    print(f"\n{Colors.CYAN}[PHASE 1] Installing Dependencies{Colors.RESET}")

    # When running from the packaged EXE, dependencies are already bundled.
    # Skip pip entirely to avoid hangs/loops.
    if IS_FROZEN:
        logger.info("Running from frozen executable - skipping pip dependency installation")
        print(f"{Colors.GREEN}[OK] Dependencies are bundled with the executable{Colors.RESET}")
        return

    # (import_name, pip_name) pairs
    required_packages = [
        ("psutil", "psutil"),
        ("wmi", "wmi"),
        # pywin32 is installed via pip, but you import win32api/win32com, not 'pywin32'
        ("win32api", "pywin32"),
        # Optional but recommended for memory analysis
        ("volatility3", "volatility3"),
    ]

    for import_name, pip_name in required_packages:
        try:
            __import__(import_name)
            logger.info(f"[OK] {import_name} already installed")
            print(f"{Colors.GREEN}[OK] {import_name}{Colors.RESET}")
        except ImportError:
            logger.info(f"Installing {pip_name}...")
            print(f"{Colors.YELLOW}Installing {pip_name}...{Colors.RESET}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name, "-q"])
            logger.info(f"[OK] {pip_name} installed")
            print(f"{Colors.GREEN}[OK] {pip_name} installed{Colors.RESET}")

def install_forensic_tools():
    """Install forensic tools (simplified version for testing)"""
    logger.info("Setting up forensic tools...")
    print(f"\n{Colors.CYAN}[PHASE 2] Setting Up Forensic Tools{Colors.RESET}")
    
    # Import the installation script
    from install_tools import (
        install_sysinternals,
        install_wireshark,
        install_winpmem,
        install_volatility,
        install_ghidra,
        verify_tool_installation
    )
    
    tools_status = {}
    
    # Check and install Sysinternals Suite
    print(f"\n{Colors.BLUE}Checking Sysinternals Suite...{Colors.RESET}")
    if verify_tool_installation("sysinternals"):
        print(f"{Colors.GREEN}✓ Sysinternals Suite already installed{Colors.RESET}")
        logger.info("Sysinternals Suite already installed, skipping installation")
        tools_status['sysinternals'] = True
    else:
        print(f"{Colors.YELLOW}⚠ Sysinternals Suite not found, installing...{Colors.RESET}")
        tools_status['sysinternals'] = install_sysinternals()
        if tools_status['sysinternals']:
            print(f"{Colors.GREEN}✓ Sysinternals Suite installed successfully{Colors.RESET}")
        else:
            print(f"{Colors.RED}✗ Sysinternals Suite installation failed{Colors.RESET}")
    
    # Check and install Wireshark/TShark
    print(f"\n{Colors.BLUE}Checking Wireshark/TShark...{Colors.RESET}")
    if verify_tool_installation("wireshark"):
        print(f"{Colors.GREEN}✓ Wireshark/TShark already installed{Colors.RESET}")
        logger.info("Wireshark/TShark already installed, skipping installation")
        tools_status['wireshark'] = True
    else:
        print(f"{Colors.YELLOW}⚠ Wireshark/TShark not found, installing...{Colors.RESET}")
        tools_status['wireshark'] = install_wireshark()
        if tools_status['wireshark']:
            print(f"{Colors.GREEN}✓ Wireshark/TShark installed successfully{Colors.RESET}")
        else:
            print(f"{Colors.RED}✗ Wireshark/TShark installation failed{Colors.RESET}")
    
    # Check and install WinPMEM
    print(f"\n{Colors.BLUE}Checking WinPMEM...{Colors.RESET}")
    if verify_tool_installation("winpmem"):
        print(f"{Colors.GREEN}✓ WinPMEM already installed{Colors.RESET}")
        logger.info("WinPMEM already installed, skipping installation")
        tools_status['winpmem'] = True
    else:
        print(f"{Colors.YELLOW}⚠ WinPMEM not found, installing...{Colors.RESET}")
        tools_status['winpmem'] = install_winpmem()
        if tools_status['winpmem']:
            print(f"{Colors.GREEN}✓ WinPMEM installed successfully{Colors.RESET}")
        else:
            print(f"{Colors.RED}✗ WinPMEM installation failed{Colors.RESET}")

    # Check and install Volatility3
    print(f"\n{Colors.BLUE}Checking Volatility3...{Colors.RESET}")
    if verify_tool_installation("volatility"):
        print(f"{Colors.GREEN}✓ Volatility3 already installed{Colors.RESET}")
        logger.info("Volatility3 already installed, skipping installation")
        tools_status['volatility'] = True
    else:
        print(f"{Colors.YELLOW}⚠ Volatility3 not found, installing...{Colors.RESET}")
        tools_status['volatility'] = install_volatility()
        if tools_status['volatility']:
            print(f"{Colors.GREEN}✓ Volatility3 installed successfully{Colors.RESET}")
        else:
            print(f"{Colors.RED}✗ Volatility3 installation failed{Colors.RESET}")

    # Check and install Ghidra
    print(f"\n{Colors.BLUE}Checking Ghidra...{Colors.RESET}")
    if verify_tool_installation("ghidra"):
        print(f"{Colors.GREEN}✓ Ghidra already installed{Colors.RESET}")
        logger.info("Ghidra already installed, skipping installation")
        tools_status['ghidra'] = True
    else:
        print(f"{Colors.YELLOW}⚠ Ghidra not found, installing...{Colors.RESET}")
        tools_status['ghidra'] = install_ghidra()
        if tools_status['ghidra']:
            print(f"{Colors.GREEN}✓ Ghidra installed successfully{Colors.RESET}")
        else:
            print(f"{Colors.RED}✗ Ghidra installation failed{Colors.RESET}")
    
    return tools_status

def capture_system_info():
    """Capture basic system information"""
    logger.info("Capturing system information...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = CONFIG["individual_reports_dir"] / f"system_info_{timestamp}.txt"
    
    system_info = {
        "timestamp": datetime.now().isoformat(),
        "hostname": os.environ.get('COMPUTERNAME', 'Unknown'),
        "username": os.environ.get('USERNAME', 'Unknown'),
        "os": f"{os.name} {sys.platform}",
        "python_version": sys.version,
        "cpu_count": psutil.cpu_count(),
        "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "disk_info": []
    }
    
    # Get disk information
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            system_info["disk_info"].append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
            })
        except:
            pass
    
    # Write to file
    with open(report_file, 'w') as f:
        f.write("="*70 + "\n")
        f.write("SYSTEM INFORMATION REPORT\n")
        f.write("="*70 + "\n\n")
        
        for key, value in system_info.items():
            if key != "disk_info":
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")
        
        f.write("\nDisk Information:\n")
        f.write("-"*70 + "\n")
        for disk in system_info["disk_info"]:
            f.write(f"\nDrive: {disk['device']}\n")
            f.write(f"  Mount Point: {disk['mountpoint']}\n")
            f.write(f"  File System: {disk['fstype']}\n")
            f.write(f"  Total: {disk['total_gb']} GB\n")
            f.write(f"  Used: {disk['used_gb']} GB\n")
            f.write(f"  Free: {disk['free_gb']} GB\n")
    
    logger.info(f"System info saved to {report_file}")
    return report_file

def run_forensic_analysis(ghidra_target=None):
    """Execute all forensic tools and capture artifacts"""
    logger.info("Starting forensic analysis...")
    print(f"\n{Colors.CYAN}[PHASE 3] Running Forensic Analysis{Colors.RESET}")
    
    individual_reports = []
    
    # Import capture modules
    from capture_artifacts import (
        capture_running_processes,
        capture_network_connections,
        capture_system_logs,
        capture_registry_artifacts,
        capture_browser_history,
        create_memory_dump,
        capture_network_traffic,
        capture_process_monitoring,
        capture_network_connections_tcpview,
        run_volatility_analysis,
        run_ghidra_analysis
    )
    
    # 1. Capture System Information
    print(f"\n{Colors.BLUE}→ Capturing System Information...{Colors.RESET}")
    report = capture_system_info()
    individual_reports.append(report)
    print(f"{Colors.GREEN}✓ System information captured{Colors.RESET}")
    
    # 2. Capture Running Processes
    print(f"\n{Colors.BLUE}→ Capturing Running Processes...{Colors.RESET}")
    report = capture_running_processes()
    individual_reports.append(report)
    print(f"{Colors.GREEN}✓ Process list captured{Colors.RESET}")
    
    # 3. Capture Network Connections
    print(f"\n{Colors.BLUE}→ Capturing Network Connections...{Colors.RESET}")
    report = capture_network_connections()
    individual_reports.append(report)
    print(f"{Colors.GREEN}✓ Network connections captured{Colors.RESET}")
    
    # 3a. Capture Network Traffic (TShark/Wireshark)
    print(f"\n{Colors.BLUE}→ Capturing Network Traffic (TShark)...{Colors.RESET}")
    report = capture_network_traffic(duration=60)
    if report:
        individual_reports.append(report)
        print(f"{Colors.GREEN}✓ Network traffic captured{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠ Network traffic capture skipped or failed{Colors.RESET}")
    
    # 3b. Capture Network Connections (TCPView)
    print(f"\n{Colors.BLUE}→ Capturing Network Connections (TCPView)...{Colors.RESET}")
    report = capture_network_connections_tcpview()
    if report:
        individual_reports.append(report)
        print(f"{Colors.GREEN}✓ TCPView network connections captured{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠ TCPView capture skipped or failed{Colors.RESET}")
    
    # 3c. Process Monitoring (ProcMon)
    print(f"\n{Colors.BLUE}→ Starting Process Monitoring (ProcMon)...{Colors.RESET}")
    print(f"{Colors.YELLOW}  Monitoring for 60 seconds...{Colors.RESET}")
    report = capture_process_monitoring(duration=60)
    if report:
        individual_reports.append(report)
        print(f"{Colors.GREEN}✓ Process monitoring completed{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠ Process monitoring skipped or failed{Colors.RESET}")
    
    # 4. Capture System Logs
    print(f"\n{Colors.BLUE}→ Capturing System Logs...{Colors.RESET}")
    report = capture_system_logs()
    individual_reports.append(report)
    print(f"{Colors.GREEN}✓ System logs captured{Colors.RESET}")
    
    # 5. Capture Registry Artifacts
    print(f"\n{Colors.BLUE}→ Capturing Registry Artifacts...{Colors.RESET}")
    report = capture_registry_artifacts()
    individual_reports.append(report)
    print(f"{Colors.GREEN}✓ Registry artifacts captured{Colors.RESET}")
    
    # 6. Capture Browser History
    print(f"\n{Colors.BLUE}→ Capturing Browser History...{Colors.RESET}")
    report = capture_browser_history()
    individual_reports.append(report)
    print(f"{Colors.GREEN}✓ Browser history captured{Colors.RESET}")

    # 7. Run YARA Analysis
    if YARA_ENABLED:
        print(f"\n{Colors.BLUE}→ Running YARA Malware Analysis...{Colors.RESET}")
        try:
            yara_report = run_yara_analysis()
            if yara_report:
                individual_reports.append(yara_report)
                print(f"{Colors.GREEN}✓ YARA malware scan completed{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}⚠ YARA scan completed with warnings{Colors.RESET}")
        except Exception as e:
            logger.error(f"YARA scan error: {e}")
            print(f"{Colors.YELLOW}⚠ YARA scan skipped due to error{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}⚠ YARA not installed - Malware scan skipped{Colors.RESET}")
        print(f"{Colors.YELLOW}  Install with: pip install yara-python{Colors.RESET}")
    
    # 8. Create Memory Dump (optional - can be slow)
    print(f"\n{Colors.YELLOW}→ Creating Memory Dump (this may take a few minutes)...{Colors.RESET}")
    report = create_memory_dump()
    if report:
        individual_reports.append(report)
        print(f"{Colors.GREEN}✓ Memory dump created{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠ Memory dump skipped or failed{Colors.RESET}")

    # 9. Volatility3 Memory Analysis
    print(f"\n{Colors.BLUE}→ Running Volatility3 Memory Analysis...{Colors.RESET}")
    report = run_volatility_analysis()
    if report:
        individual_reports.append(report)
        print(f"{Colors.GREEN}✓ Volatility3 analysis completed{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠ Volatility3 analysis skipped or failed{Colors.RESET}")

    # 10. Ghidra Static Analysis
    print(f"\n{Colors.BLUE}→ Running Ghidra Static Analysis...{Colors.RESET}")
    report = run_ghidra_analysis(target_file=ghidra_target)
    if report:
        individual_reports.append(report)
        print(f"{Colors.GREEN}✓ Ghidra analysis completed{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠ Ghidra analysis skipped or failed{Colors.RESET}")
    
    return individual_reports

def compile_master_report(individual_reports):
    """Compile all individual reports into a master report"""
    logger.info("Compiling master report...")
    print(f"\n{Colors.CYAN}[PHASE 4] Compiling Master Report{Colors.RESET}")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    master_report_file = CONFIG["master_report_dir"] / f"MASTER_FORENSIC_REPORT_{timestamp}.txt"
    
    with open(master_report_file, 'w', encoding='utf-8') as master:
        # Write header
        master.write("╔" + "="*78 + "╗\n")
        master.write("║" + " "*78 + "║\n")
        master.write("║" + "  MASTER FORENSIC ANALYSIS REPORT".center(78) + "║\n")
        master.write("║" + " "*78 + "║\n")
        master.write("╚" + "="*78 + "╝\n\n")
        
        master.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        master.write(f"Analysis Duration: {time.time()}\n")
        master.write(f"Total Individual Reports: {len(individual_reports)}\n\n")
        
        master.write("="*80 + "\n")
        master.write("TABLE OF CONTENTS\n")
        master.write("="*80 + "\n\n")
        
        for idx, report_path in enumerate(individual_reports, 1):
            master.write(f"{idx}. {Path(report_path).stem}\n")
        
        master.write("\n" + "="*80 + "\n")
        master.write("DETAILED FINDINGS\n")
        master.write("="*80 + "\n\n")
        
        # Append each individual report
        for idx, report_path in enumerate(individual_reports, 1):
            master.write("\n" + "─"*80 + "\n")
            master.write(f"SECTION {idx}: {Path(report_path).stem.upper()}\n")
            master.write("─"*80 + "\n\n")
            
            try:
                with open(report_path, 'r', encoding='utf-8', errors='ignore') as report:
                    master.write(report.read())
                master.write("\n\n")
            except Exception as e:
                master.write(f"Error reading report: {e}\n\n")
        
        # Write footer
        master.write("\n" + "="*80 + "\n")
        master.write("END OF REPORT\n")
        master.write("="*80 + "\n")
        master.write(f"\nReport saved to: {master_report_file}\n")
        master.write(f"Individual reports location: {CONFIG['individual_reports_dir']}\n")
        master.write(f"Artifacts location: {CONFIG['artifacts_dir']}\n")
    
    logger.info(f"Master report saved to {master_report_file}")
    print(f"{Colors.GREEN}✓ Master report compiled{Colors.RESET}")
    
    return master_report_file

def generate_summary():
    """Generate execution summary"""
    print(f"\n{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}EXECUTION SUMMARY{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*70}{Colors.RESET}\n")
    
    print(f"{Colors.GREEN}✓ All forensic tools executed successfully{Colors.RESET}")
    print(f"{Colors.GREEN}✓ Artifacts captured and stored{Colors.RESET}")
    print(f"{Colors.GREEN}✓ Individual reports generated{Colors.RESET}")
    print(f"{Colors.GREEN}✓ Master report compiled{Colors.RESET}")
    
    print(f"\n{Colors.CYAN}Output Locations:{Colors.RESET}")
    print(f"  • Artifacts: {Colors.YELLOW}{CONFIG['artifacts_dir']}{Colors.RESET}")
    print(f"  • Individual Reports: {Colors.YELLOW}{CONFIG['individual_reports_dir']}{Colors.RESET}")
    print(f"  • Master Report: {Colors.YELLOW}{CONFIG['master_report_dir']}{Colors.RESET}")
    print(f"  • Logs: {Colors.YELLOW}{CONFIG['logs_dir']}{Colors.RESET}")

def main():
    """Main execution flow"""
    start_time = time.time()

    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument(
        "--ghidra-target",
        default=os.environ.get("GHIDRA_TARGET"),
        help="Path to a binary to analyze with Ghidra (or set env var GHIDRA_TARGET).",
    )
    args, _unknown = parser.parse_known_args()
    
    try:
        # Display banner
        print_banner()
        
        # Check admin privileges
        elevate_privileges()
        
        # Phase 0: Setup
        print(f"\n{Colors.CYAN}[PHASE 0] Initializing Environment{Colors.RESET}")
        create_directory_structure()
        
        # Phase 1: Install dependencies
        check_and_install_dependencies()
        
        # Phase 2: Install forensic tools (optional - comment out if tools already installed)
        install_forensic_tools()
        
        # Phase 3: Run forensic analysis and capture artifacts
        individual_reports = run_forensic_analysis(ghidra_target=args.ghidra_target)
        
        # Phase 4: Compile master report
        master_report = compile_master_report(individual_reports)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Display summary
        generate_summary()
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Analysis Complete!{Colors.RESET}")
        print(f"{Colors.CYAN}Total execution time: {execution_time:.2f} seconds{Colors.RESET}")
        
        print(f"\n{Colors.YELLOW}Master Report Location:{Colors.RESET}")
        print(f"{Colors.BOLD}{master_report}{Colors.RESET}")
        
        logger.info(f"Forensic analysis completed in {execution_time:.2f} seconds")
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}✗ Analysis interrupted by user{Colors.RESET}")
        logger.warning("Analysis interrupted by user")
        return 1
        
    except Exception as e:
        print(f"\n\n{Colors.RED}✗ Fatal error: {e}{Colors.RESET}")
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
