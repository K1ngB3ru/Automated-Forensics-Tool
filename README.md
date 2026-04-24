# 🔍 BitProbe — Scan

**Simplifying digital forensics through automated bit-level inspection.**

---

## 🎯 What This Tool Does

BitProbe — Scan is an **all-in-one executable** that automatically:

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
Download: BitProbe-Scan.exe
Location: Will be in dist/ folder after building
```

**Option B - Build It Yourself**
```bash
python build_executable.py
```

### Step 2: Run on Target System

```
1. Copy BitProbe-Scan.exe to target system
2. Right-click → "Run as Administrator"
3. Wait 2-5 minutes for completion
```

### Step 3: Collect Reports

```
Output locations (project root when you run the tool):
📁 reports/master/MASTER_FORENSIC_REPORT_[timestamp].txt
📁 reports/individual/ (all individual reports)
📁 artifacts/ (raw data: memory dumps, PCAPs, etc.)
📁 artifacts/logs/ (run and install logs)
📁 downloads/ (installer files cached during tool setup)
📁 tools/ (Sysinternals, Ghidra, WinPMEM — created by installer)
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
║            MASTER FORENSIC ANALYSIS REPORT                ║
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
# From repository root, after pip install -r requirements.txt
python src/forensic_master.py
```

### Build Executable
```bash
pip install pyinstaller
python src/build_executable.py

# Output: dist/BitProbe-Scan.exe
```

---

## 📂 Project layout

```
BitProbe/
├── src/                    # Application code (forensic_master, capture_artifacts, …)
├── tests/                  # Pytest / unittest suite
├── config/                 # settings.ini, tools_config.json
├── rules/                  # YARA rules (malware_rules.yar)
├── scripts/                # Optional helpers (verify_installation, cross-platform install)
├── docs/                   # Guides
├── artifacts/              # Created at runtime (gitignored)
│   ├── logs/               # Run and install logs
│   └── ...                 # memory/, network/, processes/, etc.
├── reports/                # individual/ + master/ (gitignored)
├── downloads/              # Cached installers (gitignored)
├── tools/                  # Sysinternals, Ghidra, WinPMEM (gitignored)
├── requirements.txt
├── setup.py
└── README.md
```

If you still have an old `output/` folder from a previous layout, you can move its contents into the folders above (matching names) and then remove `output/`.

---

## 🐛 Common Issues

### "Not running as administrator"
```
Solution: Right-click .exe → "Run as Administrator"
```

### "Module not found: psutil"
```
Solution: pip install psutil wmi pywin32 yara-python
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

##🎓 For Your College Project

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

**Questions?** Check `COMPLETE_PROJECT_GUIDE.md` for detailed troubleshooting!

---
