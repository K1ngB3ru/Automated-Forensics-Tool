"""
Installation Verification Script
Checks if all required tools are properly installed and accessible
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def check_python_version():
    """Verify Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} (Requires 3.8+)")
        return False

def check_python_package(package_name):
    """Check if Python package is installed"""
    try:
        __import__(package_name)
        print_success(f"Python package: {package_name}")
        return True
    except ImportError:
        print_error(f"Python package: {package_name} (Not installed)")
        return False

def check_command(command_name, friendly_name=None):
    """Check if command-line tool is available"""
    if friendly_name is None:
        friendly_name = command_name
    
    if shutil.which(command_name):
        print_success(f"Command-line tool: {friendly_name}")
        return True
    else:
        print_error(f"Command-line tool: {friendly_name} (Not found in PATH)")
        return False

def check_file_exists(file_path, friendly_name=None):
    """Check if file exists"""
    if friendly_name is None:
        friendly_name = file_path
    
    if Path(file_path).exists():
        print_success(f"File: {friendly_name}")
        return True
    else:
        print_error(f"File: {friendly_name} (Not found)")
        return False

def check_directory_structure():
    """Verify project directory structure"""
    print_header("Checking Directory Structure")
    
    required_dirs = [
        ("tools", "Tools directory"),
        ("downloads", "Downloads directory"),
        ("logs", "Logs directory"),
        ("artifacts", "Artifacts directory"),
        ("reports", "Reports directory")
    ]
    
    results = []
    for dir_path, friendly_name in required_dirs:
        if Path(dir_path).exists():
            print_success(f"{friendly_name}: {dir_path}")
            results.append(True)
        else:
            print_warning(f"{friendly_name}: {dir_path} (Will be created)")
            results.append(False)
    
    return all(results)

def check_memory_tools():
    """Check memory analysis tools"""
    print_header("Checking Memory Analysis Tools")
    
    results = []
    
    # Volatility 3
    results.append(check_python_package("volatility3"))
    
    # WinPMEM
    winpmem_paths = [
        "tools/winpmem/winpmem_mini_x64_rc2.exe",
        "tools/winpmem/winpmem.exe"
    ]
    
    winpmem_found = False
    for path in winpmem_paths:
        if Path(path).exists():
            print_success(f"WinPMEM: {path}")
            winpmem_found = True
            break
    
    if not winpmem_found:
        print_error("WinPMEM (Not found)")
    
    results.append(winpmem_found)
    
    return all(results)

def check_network_tools():
    """Check network analysis tools"""
    print_header("Checking Network Analysis Tools")
    
    results = []
    
    # TShark/Wireshark
    results.append(check_command("tshark", "TShark (Wireshark CLI)"))
    
    # TCPDump (Linux)
    if sys.platform.startswith('linux'):
        results.append(check_command("tcpdump", "TCPDump"))
    
    return any(results)  # At least one network tool should be available

def check_process_tools():
    """Check process analysis tools"""
    print_header("Checking Process Analysis Tools")
    
    results = []
    
    # Sysinternals Suite
    sysinternals_tools = [
        ("tools/sysinternals/procmon.exe", "Process Monitor"),
        ("tools/sysinternals/procexp.exe", "Process Explorer"),
        ("tools/sysinternals/autoruns.exe", "Autoruns"),
        ("tools/sysinternals/tcpview.exe", "TCPView"),
        ("tools/sysinternals/strings.exe", "Strings")
    ]
    
    sysinternals_count = 0
    for path, name in sysinternals_tools:
        if Path(path).exists():
            print_success(f"{name}: {path}")
            sysinternals_count += 1
        else:
            print_warning(f"{name}: {path} (Not found)")
    
    if sysinternals_count > 0:
        print_info(f"Sysinternals Suite: {sysinternals_count}/{len(sysinternals_tools)} tools found")
        results.append(True)
    else:
        print_error("Sysinternals Suite: No tools found")
        results.append(False)
    
    return any(results)

def check_debugging_tools():
    """Check debugging and disassembly tools"""
    print_header("Checking Debugging & Disassembly Tools")
    
    results = []
    
    # Ghidra
    ghidra_dirs = list(Path("tools/ghidra").glob("ghidra_*"))
    if ghidra_dirs:
        print_success(f"Ghidra: {ghidra_dirs[0]}")
        results.append(True)
    else:
        print_warning("Ghidra (Not found)")
        results.append(False)
    
    # x64dbg
    x64dbg_paths = [
        "tools/x64dbg/release/x64/x64dbg.exe",
        "tools/x64dbg/x64dbg.exe"
    ]
    
    x64dbg_found = False
    for path in x64dbg_paths:
        if Path(path).exists():
            print_success(f"x64dbg: {path}")
            x64dbg_found = True
            break
    
    if not x64dbg_found:
        print_warning("x64dbg (Not found)")
    
    results.append(x64dbg_found)
    
    # Radare2 (Linux)
    if sys.platform.startswith('linux'):
        results.append(check_command("radare2", "Radare2"))
    
    return any(results)  # At least one debugging tool

def check_python_dependencies():
    """Check Python package dependencies"""
    print_header("Checking Python Dependencies")
    
    packages = [
        "volatility3",
        "pefile",
        "scapy",
        "yara",
        "requests"
    ]
    
    results = []
    for package in packages:
        results.append(check_python_package(package))
    
    return results

def generate_report(all_results):
    """Generate verification report"""
    report_path = Path("logs") / f"verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    with open(report_path, 'w') as f:
        f.write("="*60 + "\n")
        f.write("INSTALLATION VERIFICATION REPORT\n")
        f.write("="*60 + "\n\n")
        f.write(f"Verification Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Python Version: {sys.version}\n")
        f.write(f"Platform: {sys.platform}\n\n")
        
        f.write("Verification Results:\n")
        f.write("-"*60 + "\n")
        
        total = len(all_results)
        passed = sum(all_results)
        
        f.write(f"Total Checks: {total}\n")
        f.write(f"Passed: {passed}\n")
        f.write(f"Failed: {total - passed}\n")
        f.write(f"Success Rate: {(passed/total)*100:.1f}%\n\n")
        
        if passed == total:
            f.write("Status: ALL CHECKS PASSED ✓\n")
        elif passed >= total * 0.7:
            f.write("Status: MOST CHECKS PASSED - Review warnings\n")
        else:
            f.write("Status: MULTIPLE FAILURES - Installation incomplete\n")
        
        f.write("\n" + "="*60 + "\n")
    
    return report_path

def main():
    """Main verification routine"""
    print_header("INSTALLATION VERIFICATION TOOL")
    print_info(f"Platform: {sys.platform}")
    print_info(f"Python: {sys.version.split()[0]}")
    print()
    
    all_results = []
    
    # Check Python version
    print_header("Checking Python Environment")
    all_results.append(check_python_version())
    
    # Check directory structure
    check_directory_structure()
    
    # Check tools by category
    memory_ok = check_memory_tools()
    all_results.append(memory_ok)
    
    network_ok = check_network_tools()
    all_results.append(network_ok)
    
    process_ok = check_process_tools()
    all_results.append(process_ok)
    
    debugging_ok = check_debugging_tools()
    all_results.append(debugging_ok)
    
    # Check Python dependencies
    python_deps = check_python_dependencies()
    all_results.extend(python_deps)
    
    # Generate summary
    print_header("VERIFICATION SUMMARY")
    
    total = len(all_results)
    passed = sum(all_results)
    failed = total - passed
    success_rate = (passed / total) * 100
    
    print(f"Total Checks: {total}")
    print(f"Passed: {Colors.GREEN}{passed}{Colors.RESET}")
    print(f"Failed: {Colors.RED}{failed}{Colors.RESET}")
    print(f"Success Rate: {Colors.CYAN}{success_rate:.1f}%{Colors.RESET}")
    print()
    
    # Final status
    if passed == total:
        print_success("ALL CHECKS PASSED - Installation complete! ✓")
        status_code = 0
    elif passed >= total * 0.7:
        print_warning("MOST CHECKS PASSED - Some tools missing but core functionality available")
        status_code = 0
    else:
        print_error("MULTIPLE FAILURES - Installation incomplete")
        print_info("Please run installation script again or install missing tools manually")
        status_code = 1
    
    # Generate report
    report_path = generate_report(all_results)
    print()
    print_info(f"Detailed report saved to: {report_path}")
    
    return status_code

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nVerification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Error during verification: {e}{Colors.RESET}")
        sys.exit(1)
