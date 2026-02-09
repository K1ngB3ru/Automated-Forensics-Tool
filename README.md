# 🔍 Automated Forensic Analysis Tool

**One-click malware analysis and forensic data collection for Windows systems**

---

## 🎯 What This Tool Does

This is an **all-in-one executable** that automatically:

1. ✅ Installs all forensic tools and dependencies
2. ✅ Captures volatile system data (processes, network, logs, registry, browser history, memory)
3. ✅ Generates individual reports from each tool
4. ✅ Compiles everything into a master forensic report
5. ✅ Organizes all output in timestamped folders

**No manual setup required!** Just run the .exe and collect your reports.

---

## 🚀 Quick Start (3 Steps)

### Step 1: Get the Tool

**Option A - Use Pre-built Executable (Recommended)**
```
Download: ForensicAnalysisTool.exe
Location: Will be in dist/ folder after building
```

**Option B - Build It Yourself**
```bash
python build_executable.py
```

### Step 2: Run on Target System

```
1. Copy ForensicAnalysisTool.exe to target system
2. Right-click → "Run as Administrator"
3. Wait 2-5 minutes for completion
```

### Step 3: Collect Reports

```
Output locations:
📁 reports/master/MASTER_FORENSIC_REPORT_[timestamp].txt
📁 reports/individual/ (all individual reports)
📁 artifacts/ (raw data: memory dumps, logs, etc.)
```

---

## 📋 System Requirements

- **OS:** Windows 10/11 (64-bit)
- **Privileges:** Administrator required
- **Storage:** 500 MB - 8 GB (with memory dump)
- **RAM:** 4 GB minimum

---

## 📊 What Gets Captured

| Category | Details |
|----------|---------|
| **System Info** | OS version, hardware specs, disk usage |
| **Processes** | Running processes, PIDs, memory usage |
| **Network** | Active connections, listening ports, TCP/UDP sessions |
| **System Logs** | Security, Application, System event logs (last 50 events each) |
| **Registry** | Startup keys, Run keys, persistence mechanisms |
| **Browser History** | Chrome, Firefox, Edge (last 100 URLs) |
| **Memory Dump** | Full RAM capture (optional) |

---

## 🖥️ Example Output

### Master Report Structure
```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║          MASTER FORENSIC ANALYSIS REPORT                  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

Report Generated: 2024-11-03 14:30:22
Analysis Duration: 3.2 minutes
Total Individual Reports: 7

TABLE OF CONTENTS
────────────────────────────────────────────────────────────
1. System Information
2. Running Processes
3. Network Connections
4. System Logs
5. Registry Artifacts
6. Browser History
7. Memory Dump

[... detailed findings from each section ...]
```

---

## ⚠️ Important Warnings

### 🔴 Must Run as Administrator
The tool requires admin privileges to access system logs, registry, and create memory dumps.

### 🔴 Antivirus May Flag It
Memory capture and system access can trigger antivirus. Add exception if needed.

### 🔴 Use in VM for Malware Analysis
**NEVER** run malware on your production system. Always use isolated VMs:
- Take snapshot before execution
- Disconnect from network
- Use Host-Only network adapter

### 🔴 Data Privacy
Captured data includes:
- Browser history (URLs, searches)
- Running processes (may contain sensitive data)
- Network connections (IP addresses)

Handle responsibly!

---

## 🛠️ Development Mode

### Run as Python Script
```bash
# Install dependencies
pip install psutil wmi pywin32

# Run
python forensic_master.py
```

### Build Executable
```bash
# Install PyInstaller
pip install pyinstaller

# Build
python build_executable.py

# Output: dist/ForensicAnalysisTool.exe
```

---

## 📂 Project Files

```
forensic-analysis-tool/
├── forensic_master.py          # Main orchestration
├── capture_artifacts.py        # Data collection
├── install_tools.py            # Tool installation
├── build_executable.py         # EXE builder
├── requirements.txt            # Dependencies
├── COMPLETE_PROJECT_GUIDE.md   # Full documentation
└── README.md                   # This file
```

---

## 🐛 Common Issues

### "Not running as administrator"
```
Solution: Right-click .exe → "Run as Administrator"
```

### "Module not found: psutil"
```
Solution: pip install psutil wmi pywin32
```

### Browser history is empty
```
Cause: Browser is open (locks database)
Solution: Close all browsers before running
```

### Memory dump takes forever
```
Normal: Can take 5-10 minutes depending on RAM size
To skip: Edit capture_artifacts.py and comment out memory dump
```

---

## 📅 Week 1 Goals (Nov 3-9)

- [x] Day 1-2: Setup and test Python scripts
- [x] Day 3-4: Build standalone executable
- [x] Day 5-6: Test on different systems
- [x] Day 7: Documentation and demo prep

---

## 🎓 For Your College Project

### What to Submit
1. ✅ Source code (all .py files)
2. ✅ Executable (.exe file)
3. ✅ Sample reports (generated output)
4. ✅ Documentation (this guide + technical details)
5. ✅ Presentation slides

### Demo Tips
1. Show the .exe running (2-3 minutes)
2. Explain each phase of execution
3. Open the master report
4. Highlight key findings
5. Discuss use cases (incident response, malware analysis)

### Comparison with TraceHunt
Your tool improves on TraceHunt by:
- ✅ Full automation (no manual setup)
- ✅ Standalone executable
- ✅ Comprehensive reporting
- ✅ Memory dump capability
- ✅ Multi-browser support

---

## 📚 Learn More

- [Complete Project Guide](COMPLETE_PROJECT_GUIDE.md) - Detailed documentation
- [NIST Computer Forensics](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf)
- [Windows Forensics](https://www.sans.org/blog/a-forensic-analysts-introduction-to-windows-10/)

---

## 📝 License & Ethics

**Educational Use Only**
- For learning and research purposes
- Requires authorization to analyze systems
- Comply with privacy laws and institutional policies
- Never use for unauthorized access

---

## ✅ Status: Week 1 Complete!

You now have:
- ✅ Working Python scripts
- ✅ Executable build system
- ✅ Comprehensive documentation
- ✅ Sample outputs
- ✅ Ready for Week 2 enhancements

**Next Steps:** Test thoroughly, then move to Week 2 (automated analysis and IOC detection)

---

**Questions?** Check `COMPLETE_PROJECT_GUIDE.md` for detailed troubleshooting!

**Good luck with your project! 🚀**
