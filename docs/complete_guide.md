# BitProbe — Scan - Complete Project Guide

## 📋 Project Overview

BitProbe — Scan is an **all-in-one automated malware analysis and forensic tool** that:

1. ✅ **Automatically installs** all required dependencies and tools
2. ✅ **Captures volatile data**: processes, network, logs, registry, browser history, memory
3. ✅ **Generates individual reports** from each forensic tool
4. ✅ **Compiles a master report** combining all findings
5. ✅ **Packages as standalone .exe** - no manual setup required

---

## 🎯 Key Features

### Automated Installation
- Auto-detects missing dependencies
- Installs Python packages (psutil, wmi, pywin32)
- Downloads and installs forensic tools (Sysinternals, Wireshark, WinPMEM)

### Comprehensive Artifact Capture
- **Processes**: Running processes, PIDs, memory usage, CPU usage
- **Network**: Active connections, listening ports, TCP/UDP sessions
- **System Logs**: Security, Application, and System event logs
- **Registry**: Startup keys, Run keys, persistence mechanisms
- **Browser History**: Chrome, Firefox, Edge browsing data
- **Memory Dump**: Full RAM capture for deep analysis

### Intelligent Reporting
- Individual reports for each artifact type
- Master report combining all findings
- Timestamped, organized, court-admissible format
- JSON artifacts for programmatic analysis

---

## 📂 Project Structure

```
bitprobe-scan/
├── forensic_master.py          ← Main orchestration script
├── capture_artifacts.py        ← Data collection module
├── install_tools.py            ← Tool installation script
├── build_executable.py         ← EXE builder script
├── requirements.txt            ← Python dependencies
├── README.md                   ← Quick start guide
│
├── tools/                      ← Downloaded forensic tools
│   ├── sysinternals/
│   ├── wireshark/
│   └── winpmem/
│
├── artifacts/                  ← Captured raw data
│   ├── memory/
│   ├── network/
│   ├── processes/
│   ├── registry/
│   ├── logs/
│   └── browser/
│
├── reports/                    ← Generated reports
│   ├── individual/             ← Individual tool reports
│   └── master/                 ← Compiled master reports
│
└── logs/                       ← Execution logs
```

---

## 🚀 Quick Start Guide

### Option 1: Run as Python Script (Development)

```bash
# Step 1: Install Python 3.10+
# Download from python.org

# Step 2: Clone or download project files
cd bitprobe-scan

# Step 3: Install dependencies
pip install -r requirements.txt

# Step 4: Run as Administrator
python forensic_master.py
```

### Option 2: Build Standalone Executable

```bash
# Step 1: Build the EXE
python build_executable.py

# Step 2: Find the executable
# Location: dist/BitProbe-Scan.exe

# Step 3: Deploy to target system
# Just copy the .exe file - no installation needed!

# Step 4: Run as Administrator
# Right-click → Run as Administrator
```

### Option 3: Use Pre-built Executable (Recommended for Field Use)

```
1. Copy BitProbe-Scan.exe to USB drive
2. Insert USB into target system
3. Run BitProbe-Scan.exe as Administrator
4. Wait for analysis to complete
5. Collect generated reports from reports/master/ folder
```

---

## 📖 Detailed Usage

### Phase 1: Environment Initialization
```
[PHASE 0] Initializing Environment
  → Creates directory structure
  → Checks admin privileges
  → Sets up logging system
```

### Phase 2: Dependency Installation
```
[PHASE 1] Installing Dependencies
  → Checks Python packages (psutil, wmi, pywin32)
  → Auto-installs missing packages
  → Verifies installations
```

### Phase 3: Forensic Tool Setup (Optional)
```
[PHASE 2] Setting Up Forensic Tools
  → Downloads Sysinternals Suite
  → Installs Wireshark/TShark
  → Sets up WinPMEM for memory capture
  
Note: This phase can be skipped if tools are pre-installed
```

### Phase 4: Artifact Capture & Analysis
```
[PHASE 3] Running Forensic Analysis
  ✓ Capturing System Information
  ✓ Capturing Running Processes
  ✓ Capturing Network Connections
  ✓ Capturing System Logs
  ✓ Capturing Registry Artifacts
  ✓ Capturing Browser History
  ✓ Creating Memory Dump (optional)
```

### Phase 5: Report Compilation
```
[PHASE 4] Compiling Master Report
  → Combines all individual reports
  → Creates timeline of events
  → Generates executive summary
  → Saves to reports/master/
```

---

## 📊 Output Structure

### Individual Reports (reports/individual/)
```
system_info_20241103_143022.txt          ← System specs
processes_report_20241103_143025.txt     ← Process list
network_report_20241103_143027.txt       ← Network connections
system_logs_20241103_143030.txt          ← Event logs
registry_report_20241103_143035.txt      ← Registry keys
browser_history_20241103_143040.txt      ← Browser data
memory_dump_report_20241103_143045.txt   ← Memory info
```

### Master Report (reports/master/)
```
MASTER_FORENSIC_REPORT_20241103_143050.txt

Contents:
├── Header & Metadata
├── Table of Contents
├── System Information
├── Process Analysis
├── Network Activity
├── System Logs Summary
├── Registry Artifacts
├── Browser History
├── Memory Dump Info
└── Executive Summary
```

### Raw Artifacts (artifacts/)
```
artifacts/
├── memory/
│   └── memory_dump_20241103_143045.raw
├── network/
│   └── connections_20241103_143027.txt
├── processes/
│   └── processes_20241103_143025.txt
├── registry/
│   └── registry_20241103_143035.txt
└── browser/
    ├── chrome_temp_20241103_143040.sqlite
    └── firefox_temp_20241103_143040.sqlite
```

---

## 🔧 Configuration

### Edit forensic_master.py for custom settings:

```python
CONFIG = {
    "capture_memory": True,           # Create memory dump
    "capture_browser": True,          # Capture browser history
    "install_tools": False,           # Skip tool installation
    "execution_timeout": 600,         # Max runtime (seconds)
    "max_processes": 100,             # Processes to report
    "max_connections": 50,            # Network connections to report
}
```

---

## ⚠️ Important Safety Notes

### 1. Administrator Privileges Required
```
The tool MUST run as Administrator to:
- Access system logs
- Read registry keys
- Create memory dumps
- Install tools
```

### 2. Antivirus May Flag the Tool
```
Why: Memory dump and registry access triggers AV
Solution: Add exception in Windows Defender
```

### 3. VM Usage Recommended
```
For malware analysis:
- Always use isolated VM
- Take snapshot before execution
- Disconnect from network
- Never run on production systems
```

### 4. Data Privacy
```
Captured data includes:
- Browser history (URLs, searches)
- Running processes (may include passwords in memory)
- Network connections (IP addresses)

Handle responsibly and comply with privacy laws!
```

---

## 🐛 Troubleshooting

### Error: "Script requires administrator privileges"
**Solution:**
```
Right-click → Run as Administrator
OR
Use elevated command prompt
```

### Error: "Module not found: psutil"
**Solution:**
```bash
pip install psutil wmi pywin32
```

### Error: "WinPMEM not found"
**Solution:**
```bash
# Download manually:
https://github.com/Velocidex/WinPmem/releases

# Place in: tools/winpmem/winpmem_mini_x64_rc2.exe
```

### Memory Dump Takes Too Long
**Solution:**
```python
# Edit capture_artifacts.py
# Set timeout in create_memory_dump():
timeout=300  # 5 minutes instead of 10
```

### Browser History Empty
**Causes:**
- Browser is currently open (locks database)
- Profile path changed
- Permission denied

**Solution:**
```
1. Close all browser windows
2. Run tool as Administrator
3. Check browser_history report for errors
```

---

## 🎓 Week 1 Implementation Plan

### Day 1-2 (Nov 3-4): Setup & Testing
```
✓ Download all project files
✓ Install Python and dependencies
✓ Test forensic_master.py in development mode
✓ Verify all modules work correctly
✓ Review generated reports
```

### Day 3-4 (Nov 5-6): Build Executable
```
✓ Run build_executable.py
✓ Test standalone .exe on clean VM
✓ Verify auto-installation works
✓ Check report generation
✓ Document any issues
```

### Day 5-6 (Nov 7-8): Field Testing
```
✓ Test on different Windows versions (Win 10, 11)
✓ Test with/without internet connection
✓ Test with various browsers installed
✓ Measure execution time
✓ Validate report accuracy
```

### Day 7 (Nov 9): Documentation & Demo Prep
```
✓ Create user manual
✓ Prepare demo presentation
✓ Screenshot outputs
✓ Document any limitations
✓ Plan Week 2 enhancements
```

---

## 📈 Performance Metrics

### Execution Time
```
Typical runtime: 2-5 minutes
- Without memory dump: ~2 min
- With memory dump: ~5-10 min (depends on RAM size)
```

### Resource Usage
```
CPU: ~10-20% during capture
Memory: ~100-200 MB
Disk: ~500 MB - 8 GB (with memory dump)
```

### Compatibility
```
✓ Windows 10 (all editions)
✓ Windows 11
✓ Windows Server 2016+
✗ Windows 7/8 (limited support)
✗ Linux/macOS (not supported)
```

---

## 🔄 Future Enhancements (Week 2-4)

### Week 2: Advanced Analysis
```
□ Automated IOC (Indicator of Compromise) detection
□ YARA rule scanning
□ Suspicious process identification
□ Malware signature detection
```

### Week 3: Reporting & Visualization
```
□ HTML reports with charts
□ Timeline visualization
□ Network diagram generation
□ PDF export option
```

### Week 4: Integration & Polish
```
□ Volatility 3 integration for memory analysis
□ VirusTotal API integration
□ GUI interface (optional)
□ Final testing and documentation
```

---

## 📚 References & Learning Resources

### Tools Documentation
- [Sysinternals Suite](https://docs.microsoft.com/en-us/sysinternals/)
- [Wireshark User Guide](https://www.wireshark.org/docs/)
- [Volatility Framework](https://volatility3.readthedocs.io/)
- [Windows Event Logs](https://docs.microsoft.com/en-us/windows/security/threat-protection/auditing/)

### Forensic Analysis Guides
- [NIST Computer Forensics Guide](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf)
- [SANS Digital Forensics](https://www.sans.org/blog/a-forensic-analysts-introduction-to-windows-10/)

### Similar Projects
- TraceHunt (referenced in your PDF)
- Autopsy
- SIFT Workstation

---

## 📞 Support & Contact

### For Issues
```
1. Check troubleshooting section
2. Review logs/ directory for detailed errors
3. Test on clean VM environment
4. Check Windows Event Viewer for system errors
```

### Project Info
```
Version: 1.0
License: Educational Use
Developed for: College Cybersecurity Project
Target Completion: December 1, 2024
```

---

## ⚖️ Legal & Ethical Notice

**CRITICAL WARNINGS:**

1. **Authorization Required**
   - Only analyze systems you own or have written permission to investigate
   - Unauthorized access is illegal

2. **Educational Purpose**
   - This tool is for learning and research
   - Not intended for malicious use

3. **Data Privacy**
   - Captured data may contain personal information
   - Handle according to privacy laws (GDPR, etc.)
   - Secure storage and disposal required

4. **Malware Handling**
   - Only analyze malware in isolated VMs
   - Never execute on production systems
   - Follow institutional safety policies

---

## ✅ Pre-Submission Checklist

Before submitting your project (Dec 1):

```
□ All scripts tested and working
□ Executable builds successfully
□ Documentation complete
□ Sample reports generated
□ Screenshots captured
□ Demo prepared
□ Code commented
□ Limitations documented
□ Future enhancements planned
□ Presentation slides ready
```

---

**Good luck with your project! 🚀**

Remember: Week 1 goal is to have working tool installation and basic artifact capture. Focus on getting the core functionality working first, then enhance in Week 2-4!
