"""
Artifact Capture Module
Captures volatile data and generates individual reports

Functions:
- Process listing
- Network connections
- System logs
- Registry artifacts
- Browser history
- Memory dumps
- Network traffic capture (TShark/Wireshark)
- Process monitoring (ProcMon)
- Network connection monitoring (TCPView)
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

try:
    import psutil  # type: ignore
except ImportError:
    print("ERROR: psutil is required but not installed.")
    print("Please install it using: pip install psutil")
    sys.exit(1)
from datetime import datetime
import logging
import winreg
import sqlite3
import shutil

logger = logging.getLogger(__name__)

# Paths
ARTIFACTS_DIR = Path("artifacts")
REPORTS_DIR = Path("reports/individual")

def get_timestamp():
    """Get formatted timestamp"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def capture_running_processes():
    """Capture list of running processes"""
    logger.info("Capturing running processes...")
    
    timestamp = get_timestamp()
    artifact_file = ARTIFACTS_DIR / "processes" / f"processes_{timestamp}.txt"
    report_file = REPORTS_DIR / f"processes_report_{timestamp}.txt"
    
    processes = []
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'create_time', 'memory_info', 'cpu_percent']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'username': pinfo['username'] or 'N/A',
                    'status': pinfo['status'],
                    'created': datetime.fromtimestamp(pinfo['create_time']).strftime('%Y-%m-%d %H:%M:%S') if pinfo['create_time'] else 'N/A',
                    'memory_mb': round(pinfo['memory_info'].rss / (1024*1024), 2) if pinfo['memory_info'] else 0,
                    'cpu_percent': pinfo['cpu_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Write raw artifact data
        with open(artifact_file, 'w') as f:
            f.write(json.dumps(processes, indent=2))
        
        # Write formatted report
        with open(report_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("RUNNING PROCESSES REPORT\n")
            f.write("="*80 + "\n\n")
            f.write(f"Capture Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Processes: {len(processes)}\n\n")
            
            f.write("-"*80 + "\n")
            f.write(f"{'PID':<8} {'Name':<30} {'User':<20} {'Memory (MB)':<12} {'Status':<10}\n")
            f.write("-"*80 + "\n")
            
            for proc in sorted(processes, key=lambda x: x['memory_mb'], reverse=True)[:50]:
                f.write(f"{proc['pid']:<8} {proc['name']:<30} {proc['username']:<20} {proc['memory_mb']:<12.2f} {proc['status']:<10}\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write("Top 10 Memory Consumers:\n")
            f.write("-"*80 + "\n")
            
            for idx, proc in enumerate(sorted(processes, key=lambda x: x['memory_mb'], reverse=True)[:10], 1):
                f.write(f"{idx}. {proc['name']} (PID: {proc['pid']}) - {proc['memory_mb']} MB\n")
        
        logger.info(f"Process list captured: {len(processes)} processes")
        return report_file
        
    except Exception as e:
        logger.error(f"Error capturing processes: {e}")
        return None

def capture_network_connections():
    """Capture active network connections"""
    logger.info("Capturing network connections...")
    
    timestamp = get_timestamp()
    artifact_file = ARTIFACTS_DIR / "network" / f"connections_{timestamp}.txt"
    report_file = REPORTS_DIR / f"network_report_{timestamp}.txt"
    
    try:
        connections = []
        
        for conn in psutil.net_connections(kind='inet'):
            try:
                connections.append({
                    'family': 'IPv4' if conn.family == 2 else 'IPv6',
                    'type': 'TCP' if conn.type == 1 else 'UDP',
                    'local_addr': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else 'N/A',
                    'remote_addr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else 'N/A',
                    'status': conn.status,
                    'pid': conn.pid
                })
            except:
                continue
        
        # Write raw artifact
        with open(artifact_file, 'w') as f:
            f.write(json.dumps(connections, indent=2))
        
        # Write formatted report
        with open(report_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("NETWORK CONNECTIONS REPORT\n")
            f.write("="*80 + "\n\n")
            f.write(f"Capture Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Connections: {len(connections)}\n\n")
            
            # TCP Connections
            tcp_conns = [c for c in connections if c['type'] == 'TCP']
            f.write(f"TCP Connections: {len(tcp_conns)}\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Type':<8} {'Local Address':<30} {'Remote Address':<30} {'Status':<15}\n")
            f.write("-"*80 + "\n")
            
            for conn in tcp_conns[:30]:
                f.write(f"{conn['type']:<8} {conn['local_addr']:<30} {conn['remote_addr']:<30} {conn['status']:<15}\n")
            
            # UDP Connections
            udp_conns = [c for c in connections if c['type'] == 'UDP']
            f.write(f"\nUDP Connections: {len(udp_conns)}\n")
            f.write("-"*80 + "\n")
            
            for conn in udp_conns[:20]:
                f.write(f"{conn['type']:<8} {conn['local_addr']:<30} {conn['remote_addr']:<30}\n")
        
        logger.info(f"Network connections captured: {len(connections)} connections")
        return report_file
        
    except Exception as e:
        logger.error(f"Error capturing network connections: {e}")
        return None

def capture_system_logs():
    """Capture system event logs (Windows)"""
    logger.info("Capturing system logs...")
    
    timestamp = get_timestamp()
    report_file = REPORTS_DIR / f"system_logs_{timestamp}.txt"
    
    try:
        # Use wevtutil to export logs
        logs_to_capture = ['System', 'Security', 'Application']
        
        with open(report_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("SYSTEM LOGS REPORT\n")
            f.write("="*80 + "\n\n")
            f.write(f"Capture Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for log_name in logs_to_capture:
                f.write(f"\n{'='*80}\n")
                f.write(f"{log_name.upper()} LOG (Last 50 entries)\n")
                f.write(f"{'='*80}\n\n")
                
                try:
                    # Export last 50 events from each log
                    cmd = f'wevtutil qe {log_name} /c:50 /rd:true /f:text'
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        f.write(result.stdout)
                    else:
                        f.write(f"Error capturing {log_name} log: {result.stderr}\n")
                except subprocess.TimeoutExpired:
                    f.write(f"Timeout while capturing {log_name} log\n")
                except Exception as e:
                    f.write(f"Error: {e}\n")
        
        logger.info("System logs captured")
        return report_file
        
    except Exception as e:
        logger.error(f"Error capturing system logs: {e}")
        return None

def capture_registry_artifacts():
    """Capture important registry keys"""
    logger.info("Capturing registry artifacts...")
    
    timestamp = get_timestamp()
    artifact_file = ARTIFACTS_DIR / "registry" / f"registry_{timestamp}.txt"
    report_file = REPORTS_DIR / f"registry_report_{timestamp}.txt"
    
    try:
        registry_keys = {
            "Run Keys (HKLM)": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            "Run Keys (HKCU)": (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            "RunOnce Keys (HKLM)": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"),
            "RunOnce Keys (HKCU)": (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"),
        }
        
        registry_data = {}
        
        for key_name, (hive, path) in registry_keys.items():
            try:
                key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ)
                values = []
                
                i = 0
                while True:
                    try:
                        name, value, type_ = winreg.EnumValue(key, i)
                        values.append({
                            'name': name,
                            'value': str(value),
                            'type': type_
                        })
                        i += 1
                    except OSError:
                        break
                
                registry_data[key_name] = values
                winreg.CloseKey(key)
            except FileNotFoundError:
                registry_data[key_name] = []
            except Exception as e:
                logger.error(f"Error reading {key_name}: {e}")
                registry_data[key_name] = []
        
        # Write raw artifact
        with open(artifact_file, 'w') as f:
            f.write(json.dumps(registry_data, indent=2))
        
        # Write formatted report
        with open(report_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("REGISTRY ARTIFACTS REPORT\n")
            f.write("="*80 + "\n\n")
            f.write(f"Capture Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for key_name, values in registry_data.items():
                f.write(f"\n{'-'*80}\n")
                f.write(f"{key_name}\n")
                f.write(f"{'-'*80}\n")
                
                if values:
                    for item in values:
                        f.write(f"Name: {item['name']}\n")
                        f.write(f"Value: {item['value']}\n")
                        f.write(f"Type: {item['type']}\n\n")
                else:
                    f.write("No entries found\n\n")
        
        logger.info("Registry artifacts captured")
        return report_file
        
    except Exception as e:
        logger.error(f"Error capturing registry artifacts: {e}")
        return None

def capture_browser_history():
    """Capture browser history (Chrome, Firefox, Edge)"""
    logger.info("Capturing browser history...")
    
    timestamp = get_timestamp()
    report_file = REPORTS_DIR / f"browser_history_{timestamp}.txt"
    
    try:
        browser_paths = {
            'Chrome': Path(os.environ['LOCALAPPDATA']) / r'Google\Chrome\User Data\Default\History',
            'Edge': Path(os.environ['LOCALAPPDATA']) / r'Microsoft\Edge\User Data\Default\History',
            'Firefox': Path(os.environ['APPDATA']) / r'Mozilla\Firefox\Profiles'
        }
        
        all_history = {}
        
        for browser, path in browser_paths.items():
            try:
                if browser == 'Firefox':
                    # Firefox stores history in multiple profile folders
                    if path.exists():
                        for profile in path.glob('*.default*'):
                            history_db = profile / 'places.sqlite'
                            if history_db.exists():
                                temp_db = ARTIFACTS_DIR / "browser" / f"firefox_temp_{timestamp}.sqlite"
                                shutil.copy(history_db, temp_db)
                                
                                conn = sqlite3.connect(temp_db)
                                cursor = conn.cursor()
                                cursor.execute("SELECT url, title, visit_count, last_visit_date FROM moz_places ORDER BY last_visit_date DESC LIMIT 100")
                                results = cursor.fetchall()
                                conn.close()
                                
                                all_history[f'Firefox ({profile.name})'] = [
                                    {'url': r[0], 'title': r[1], 'visits': r[2], 'last_visit': r[3]}
                                    for r in results
                                ]
                else:
                    # Chrome and Edge
                    if path.exists():
                        temp_db = ARTIFACTS_DIR / "browser" / f"{browser.lower()}_temp_{timestamp}.sqlite"
                        shutil.copy(path, temp_db)
                        
                        conn = sqlite3.connect(temp_db)
                        cursor = conn.cursor()
                        cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 100")
                        results = cursor.fetchall()
                        conn.close()
                        
                        all_history[browser] = [
                            {'url': r[0], 'title': r[1], 'visits': r[2], 'last_visit': r[3]}
                            for r in results
                        ]
            except Exception as e:
                logger.error(f"Error capturing {browser} history: {e}")
                all_history[browser] = []
        
        # Write report
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("BROWSER HISTORY REPORT\n")
            f.write("="*80 + "\n\n")
            f.write(f"Capture Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for browser, history in all_history.items():
                f.write(f"\n{'-'*80}\n")
                f.write(f"{browser} (Last 100 entries)\n")
                f.write(f"{'-'*80}\n\n")
                
                if history:
                    for idx, entry in enumerate(history[:50], 1):
                        f.write(f"{idx}. {entry['title'] or 'No Title'}\n")
                        f.write(f"   URL: {entry['url']}\n")
                        f.write(f"   Visits: {entry['visits']}\n\n")
                else:
                    f.write("No history found or unable to access\n\n")
        
        logger.info("Browser history captured")
        return report_file
        
    except Exception as e:
        logger.error(f"Error capturing browser history: {e}")
        return None

def create_memory_dump():
    """Create memory dump using WinPMEM (if available)"""
    logger.info("Creating memory dump...")
    
    timestamp = get_timestamp()
    dump_file = ARTIFACTS_DIR / "memory" / f"memory_dump_{timestamp}.raw"
    report_file = REPORTS_DIR / f"memory_dump_report_{timestamp}.txt"
    
    try:
        # Check if WinPMEM is available
        winpmem_path = Path("tools/winpmem/winpmem_mini_x64_rc2.exe")
        
        if not winpmem_path.exists():
            logger.warning("WinPMEM not found, skipping memory dump")
            with open(report_file, 'w') as f:
                f.write("="*80 + "\n")
                f.write("MEMORY DUMP REPORT\n")
                f.write("="*80 + "\n\n")
                f.write("Status: Skipped (WinPMEM not installed)\n")
            return report_file
        
        # Create memory dump
        logger.info("Creating memory dump (this may take several minutes)...")
        cmd = f'"{winpmem_path}" "{dump_file}"'
        # Memory acquisition can take a long time on high-RAM systems.
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=1800)
        
        # Write report
        with open(report_file, 'w', encoding='utf-8', errors='ignore') as f:
            f.write("="*80 + "\n")
            f.write("MEMORY DUMP REPORT\n")
            f.write("="*80 + "\n\n")
            f.write(f"Capture Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Command: {cmd}\n\n")
            
            if result.returncode == 0 and dump_file.exists():
                dump_size_mb = dump_file.stat().st_size / (1024*1024)
                f.write(f"Status: Success\n")
                f.write(f"Dump File: {dump_file}\n")
                f.write(f"Size: {dump_size_mb:.2f} MB\n")
                logger.info(f"Memory dump created: {dump_size_mb:.2f} MB")
            else:
                f.write(f"Status: Failed\n")
                if result.stdout:
                    f.write("\n--- STDOUT ---\n")
                    f.write(result.stdout + "\n")
                if result.stderr:
                    f.write("\n--- STDERR ---\n")
                    f.write(result.stderr + "\n")
        
        return report_file
        
    except subprocess.TimeoutExpired:
        logger.error("Memory dump timeout")
        return None
    except Exception as e:
        logger.error(f"Error creating memory dump: {e}")
        return None

def capture_network_traffic(duration=60):
    """Capture network traffic using TShark/Wireshark"""
    logger.info("Capturing network traffic with TShark...")
    
    timestamp = get_timestamp()
    pcap_file = ARTIFACTS_DIR / "network" / f"traffic_{timestamp}.pcap"
    report_file = REPORTS_DIR / f"network_traffic_report_{timestamp}.txt"
    
    try:
        # Check if TShark is available - check PATH first, then common locations
        tshark_path = shutil.which("tshark")
        if not tshark_path:
            # Check common Wireshark installation paths
            common_paths = [
                Path("C:/Program Files/Wireshark/tshark.exe"),
                Path("C:/Program Files (x86)/Wireshark/tshark.exe"),
            ]
            for path in common_paths:
                if path.exists():
                    tshark_path = str(path)
                    logger.info(f"Found tshark at: {tshark_path}")
                    break
        
        if not tshark_path:
            logger.warning("TShark not found in PATH or common locations, skipping network capture")
            with open(report_file, 'w') as f:
                f.write("="*80 + "\n")
                f.write("NETWORK TRAFFIC CAPTURE REPORT\n")
                f.write("="*80 + "\n\n")
                f.write("Status: Skipped (TShark/Wireshark not installed or not in PATH)\n")
                f.write("Please ensure Wireshark is installed and tshark.exe is in your PATH\n")
                f.write("Or install Wireshark using the tool installation script\n")
            return report_file
        
        # Get default network interface
        logger.info(f"Capturing network traffic for {duration} seconds...")
        cmd = [
            tshark_path,
            '-i', '1',  # Use first available interface
            '-w', str(pcap_file),
            '-a', f'duration:{duration}',
            '-q'  # Quiet mode
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration+30)
        
        # Analyze captured packets
        packet_count = 0
        if pcap_file.exists() and pcap_file.stat().st_size > 0:
            # Get packet count
            count_cmd = [tshark_path, '-r', str(pcap_file), '-T', 'fields', '-e', 'frame.number']
            count_result = subprocess.run(count_cmd, capture_output=True, text=True, timeout=30)
            if count_result.returncode == 0:
                packet_count = len([line for line in count_result.stdout.strip().split('\n') if line])
        
        # Generate report
        with open(report_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("NETWORK TRAFFIC CAPTURE REPORT\n")
            f.write("="*80 + "\n\n")
            f.write(f"Capture Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {duration} seconds\n")
            
            if result.returncode == 0 and pcap_file.exists() and pcap_file.stat().st_size > 0:
                pcap_size_mb = pcap_file.stat().st_size / (1024*1024)
                f.write(f"Status: Success\n")
                f.write(f"PCAP File: {pcap_file}\n")
                f.write(f"File Size: {pcap_size_mb:.2f} MB\n")
                f.write(f"Packets Captured: {packet_count}\n\n")
                f.write("To analyze the capture file, use:\n")
                f.write(f"  tshark -r {pcap_file}\n")
                f.write(f"  wireshark {pcap_file}\n")
                logger.info(f"Network traffic captured: {pcap_size_mb:.2f} MB, {packet_count} packets")
            else:
                f.write(f"Status: Failed or No Traffic\n")
                f.write(f"Error: {result.stderr}\n")
        
        return report_file
        
    except subprocess.TimeoutExpired:
        logger.error("Network capture timeout")
        return None

def _find_latest_memory_dump():
    """Locate the most recent memory dump file"""
    dump_dir = ARTIFACTS_DIR / "memory"
    if not dump_dir.exists():
        return None
    dumps = sorted(
        dump_dir.glob("memory_dump_*.raw"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    return dumps[0] if dumps else None

def run_volatility_analysis(memory_dump_path=None):
    """Run Volatility3 against the captured memory dump"""
    logger.info("Running Volatility3 analysis...")
    
    timestamp = get_timestamp()
    report_file = REPORTS_DIR / f"volatility_report_{timestamp}.txt"
    
    dump_path = Path(memory_dump_path) if memory_dump_path else _find_latest_memory_dump()
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("VOLATILITY3 MEMORY ANALYSIS REPORT\n")
        f.write("="*80 + "\n\n")
        f.write(f"Capture Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        if not dump_path or not dump_path.exists():
            f.write("\nStatus: Skipped (memory dump not found)\n")
            f.write("Hint: Enable memory dump or ensure WinPMEM succeeded\n")
            return report_file
        
        f.write(f"\nMemory Dump: {dump_path}\n")
        f.write("Plugins: windows.info, windows.pslist, windows.netscan\n\n")
        
        base_cmd = [sys.executable, "-m", "volatility3", "-f", str(dump_path)]
        plugins = [
            ("windows.info", []),
            ("windows.pslist", []),
            ("windows.netscan", []),
        ]
        
        for plugin, extra in plugins:
            f.write("-"*80 + "\n")
            f.write(f"{plugin.upper()}\n")
            f.write("-"*80 + "\n")
            try:
                result = subprocess.run(
                    base_cmd + [plugin] + extra,
                    capture_output=True,
                    text=True,
                    timeout=180
                )
                if result.returncode == 0:
                    output = result.stdout or "(no output)"
                    f.write(output)
                else:
                    f.write(f"Error (code {result.returncode}): {result.stderr}\n")
            except subprocess.TimeoutExpired:
                f.write("Error: Volatility3 timed out\n")
            except FileNotFoundError:
                f.write("Error: Volatility3 module not found. Install with pip install volatility3\n")
                break
            except Exception as e:
                f.write(f"Error running {plugin}: {e}\n")
            f.write("\n")
    
    logger.info(f"Volatility3 analysis complete: {report_file}")
    return report_file

def _find_ghidra_analyze_headless():
    """Locate the Ghidra analyzeHeadless.bat script"""
    ghidra_root = Path("tools/ghidra")
    if not ghidra_root.exists():
        return None
    candidates = list(ghidra_root.glob("**/analyzeHeadless.bat"))
    return candidates[0] if candidates else None

def _select_default_ghidra_target():
    """Pick a default binary to analyze if none provided"""
    candidates = [
        Path(os.environ.get("WINDIR", r"C:\Windows")) / "System32" / "notepad.exe",
        Path(sys.executable),
    ]
    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate
    return None

def run_ghidra_analysis(target_file=None):
    """Run a lightweight Ghidra headless analysis on a target binary"""
    logger.info("Running Ghidra analysis...")
    
    timestamp = get_timestamp()
    report_file = REPORTS_DIR / f"ghidra_report_{timestamp}.txt"
    
    analyzer = _find_ghidra_analyze_headless()
    target = Path(target_file) if target_file else _select_default_ghidra_target()
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("GHIDRA STATIC ANALYSIS REPORT\n")
        f.write("="*80 + "\n\n")
        f.write(f"Capture Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if not analyzer or not analyzer.exists():
            f.write("Status: Skipped (Ghidra analyzeHeadless.bat not found)\n")
            f.write("Hint: Run tool installation to download/extract Ghidra\n")
            return report_file
        
        if not target or not target.exists():
            f.write("Status: Skipped (no suitable target binary found)\n")
            return report_file
        
        project_dir = ARTIFACTS_DIR / "ghidra" / f"project_{timestamp}"
        project_dir.mkdir(parents=True, exist_ok=True)
        project_name = f"analysis_{timestamp}"
        
        f.write(f"Target File: {target}\n")
        f.write(f"Ghidra Project: {project_dir} ({project_name})\n\n")
        
        cmd = [
            str(analyzer),
            str(project_dir),
            project_name,
            "-import", str(target),
            "-analysisTimeoutPerFile", "120",
            "-overwrite",
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=240,
                shell=True  # required to execute .bat on Windows
            )
            if result.returncode == 0:
                f.write("Status: Success\n\n")
                if result.stdout:
                    f.write("Ghidra Output:\n")
                    f.write(result.stdout)
            else:
                f.write(f"Status: Failed (code {result.returncode})\n")
                if result.stderr:
                    f.write("Error Output:\n")
                    f.write(result.stderr)
        except subprocess.TimeoutExpired:
            f.write("Status: Failed (Ghidra analysis timed out)\n")
        except FileNotFoundError:
            f.write("Status: Failed (Ghidra not found on system)\n")
        except Exception as e:
            f.write(f"Status: Failed ({e})\n")
    
    logger.info(f"Ghidra analysis complete: {report_file}")
    return report_file

def capture_process_monitoring(duration=60):
    """Monitor system calls and file/registry access using ProcMon"""
    logger.info("Starting process monitoring with ProcMon...")
    
    timestamp = get_timestamp()
    procmon_file = ARTIFACTS_DIR / "processes" / f"procmon_{timestamp}.pml"
    report_file = REPORTS_DIR / f"procmon_report_{timestamp}.txt"
    
    try:
        # Check if ProcMon is available
        procmon_path = Path("tools/sysinternals/procmon.exe")
        if not procmon_path.exists():
            logger.warning("ProcMon not found, skipping process monitoring")
            with open(report_file, 'w') as f:
                f.write("="*80 + "\n")
                f.write("PROCESS MONITORING REPORT (PROCMON)\n")
                f.write("="*80 + "\n\n")
                f.write("Status: Skipped (ProcMon not installed)\n")
                f.write("Please ensure Sysinternals Suite is installed\n")
            return report_file
        
        logger.info(f"Monitoring processes for {duration} seconds...")
        
        # Start ProcMon in background mode
        cmd = [
            str(procmon_path),
            "/AcceptEula",
            '/BackingFile', str(procmon_file),
            '/Quiet',
            '/Minimized'
        ]
        
        procmon_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for specified duration
        time.sleep(duration)
        
        # Terminate ProcMon gracefully so it flushes the .PML file.
        # (Killing the process often results in no log file.)
        try:
            subprocess.run(
                [str(procmon_path), "/Terminate"],
                capture_output=True,
                text=True,
                timeout=30,
                shell=False
            )
        except Exception:
            pass
        finally:
            try:
                procmon_process.wait(timeout=15)
            except Exception:
                try:
                    procmon_process.kill()
                except Exception:
                    pass
        
        # Generate report
        with open(report_file, 'w', encoding='utf-8', errors='ignore') as f:
            f.write("="*80 + "\n")
            f.write("PROCESS MONITORING REPORT (PROCMON)\n")
            f.write("="*80 + "\n\n")
            f.write(f"Capture Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {duration} seconds\n")
            f.write(f"ProcMon Path: {procmon_path}\n")
            f.write(f"Backing File: {procmon_file}\n\n")
            
            if procmon_file.exists():
                file_size_mb = procmon_file.stat().st_size / (1024*1024)
                f.write(f"Status: Success\n")
                f.write(f"ProcMon Log File: {procmon_file}\n")
                f.write(f"File Size: {file_size_mb:.2f} MB\n\n")
                f.write("To analyze the ProcMon log, open it with Process Monitor:\n")
                f.write(f"  {procmon_path} /OpenLog {procmon_file}\n")
                logger.info(f"Process monitoring completed: {file_size_mb:.2f} MB")
            else:
                f.write(f"Status: Failed - Log file not created\n")
        
        return report_file
        
    except Exception as e:
        logger.error(f"Error in process monitoring: {e}")
        return None

def capture_network_connections_tcpview():
    """Capture detailed network connections using TCPView"""
    logger.info("Capturing network connections with TCPView...")
    
    timestamp = get_timestamp()
    report_file = REPORTS_DIR / f"tcpview_report_{timestamp}.txt"
    
    try:
        # Check if TCPView is available
        tcpview_path = Path("tools/sysinternals/tcpview.exe")
        if not tcpview_path.exists():
            logger.warning("TCPView not found, skipping network connection monitoring")
            with open(report_file, 'w') as f:
                f.write("="*80 + "\n")
                f.write("NETWORK CONNECTIONS REPORT (TCPVIEW)\n")
                f.write("="*80 + "\n\n")
                f.write("Status: Skipped (TCPView not installed)\n")
                f.write("Please ensure Sysinternals Suite is installed\n")
            return report_file
        
        # TCPView doesn't have command-line export, so we'll use netstat as alternative
        # and note that TCPView GUI can be opened manually
        logger.info("Capturing network connections...")
        
        # Use netstat for detailed connection info
        cmd = ['netstat', '-ano']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        with open(report_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("NETWORK CONNECTIONS REPORT (TCPVIEW)\n")
            f.write("="*80 + "\n\n")
            f.write(f"Capture Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("Note: For GUI view, open TCPView manually:\n")
            f.write(f"  {tcpview_path}\n\n")
            f.write("="*80 + "\n")
            f.write("NETSTAT OUTPUT\n")
            f.write("="*80 + "\n\n")
            
            if result.returncode == 0:
                f.write(result.stdout)
            else:
                f.write(f"Error: {result.stderr}\n")
        
        logger.info("Network connections captured with TCPView/netstat")
        return report_file
        
    except Exception as e:
        logger.error(f"Error capturing network connections: {e}")
        return None
