#!/bin/bash

################################################################################
# Automated Forensic & Malware Analysis Tool Installation Script (Linux)
# Author: Cybersecurity Project
# Description: Downloads and installs forensic/analysis tools for Linux
# Requirements: Root/sudo privileges, Ubuntu/Debian-based system
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
TOOLS_DIR="./tools"
DOWNLOADS_DIR="./downloads"
LOGS_DIR="./logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOGS_DIR}/installation_${TIMESTAMP}.log"

# Tool versions
VOLATILITY3_VERSION="2.5.0"
GHIDRA_VERSION="10.4"

################################################################################
# Functions
################################################################################

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo -e "${timestamp} - [${level}] - ${message}" | tee -a "${LOG_FILE}"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $@"
    log "INFO" "$@"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $@"
    log "SUCCESS" "$@"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $@"
    log "ERROR" "$@"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $@"
    log "WARNING" "$@"
}

print_header() {
    echo -e "${CYAN}============================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}============================================================${NC}"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root or with sudo"
        exit 1
    fi
    log_info "Running with root privileges ✓"
}

create_directories() {
    log_info "Creating directory structure..."
    
    local dirs=("${TOOLS_DIR}" "${DOWNLOADS_DIR}" "${LOGS_DIR}")
    
    for dir in "${dirs[@]}"; do
        if [[ ! -d "${dir}" ]]; then
            mkdir -p "${dir}"
            log_info "Created directory: ${dir}"
        else
            log_info "Directory exists: ${dir}"
        fi
    done
}

check_internet() {
    log_info "Checking internet connectivity..."
    if ping -c 1 8.8.8.8 &> /dev/null; then
        log_success "Internet connection available"
        return 0
    else
        log_error "No internet connection detected"
        return 1
    fi
}

update_system() {
    log_info "Updating package lists..."
    apt-get update -qq || {
        log_error "Failed to update package lists"
        return 1
    }
    log_success "Package lists updated"
}

install_system_dependencies() {
    print_header "Installing System Dependencies"
    
    local packages=(
        "python3"
        "python3-pip"
        "python3-dev"
        "build-essential"
        "git"
        "wget"
        "curl"
        "unzip"
        "tcpdump"
        "wireshark"
        "tshark"
        "volatility"
        "binwalk"
        "foremost"
        "sleuthkit"
        "autopsy"
    )
    
    log_info "Installing system packages..."
    
    for package in "${packages[@]}"; do
        if dpkg -l | grep -q "^ii  ${package}"; then
            log_info "${package} is already installed"
        else
            log_info "Installing ${package}..."
            apt-get install -y "${package}" >> "${LOG_FILE}" 2>&1 || {
                log_warning "Failed to install ${package}"
                continue
            }
            log_success "Installed ${package}"
        fi
    done
}

install_volatility3() {
    print_header "Installing Volatility 3"
    
    log_info "Installing Volatility 3 via pip..."
    
    python3 -m pip install --upgrade pip >> "${LOG_FILE}" 2>&1
    python3 -m pip install volatility3 >> "${LOG_FILE}" 2>&1 || {
        log_error "Failed to install Volatility 3"
        return 1
    }
    
    # Verify installation
    if python3 -c "import volatility3" 2>/dev/null; then
        log_success "Volatility 3 installed successfully"
        return 0
    else
        log_error "Volatility 3 installation verification failed"
        return 1
    fi
}

install_ghidra() {
    print_header "Installing Ghidra"
    
    local ghidra_url="https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_${GHIDRA_VERSION}_build/ghidra_${GHIDRA_VERSION}_PUBLIC_20230928.zip"
    local download_path="${DOWNLOADS_DIR}/ghidra.zip"
    local install_path="${TOOLS_DIR}/ghidra"
    
    # Check for Java
    if ! command -v java &> /dev/null; then
        log_info "Java not found, installing OpenJDK 17..."
        apt-get install -y openjdk-17-jdk >> "${LOG_FILE}" 2>&1 || {
            log_error "Failed to install Java"
            return 1
        }
    fi
    
    log_info "Downloading Ghidra..."
    wget -q --show-progress "${ghidra_url}" -O "${download_path}" || {
        log_error "Failed to download Ghidra"
        return 1
    }
    
    log_info "Extracting Ghidra..."
    mkdir -p "${install_path}"
    unzip -q "${download_path}" -d "${install_path}" || {
        log_error "Failed to extract Ghidra"
        return 1
    }
    
    log_success "Ghidra installed successfully"
    return 0
}

install_radare2() {
    print_header "Installing Radare2"
    
    log_info "Cloning Radare2 repository..."
    
    local radare_dir="${TOOLS_DIR}/radare2"
    
    if [[ -d "${radare_dir}" ]]; then
        log_info "Radare2 directory exists, removing..."
        rm -rf "${radare_dir}"
    fi
    
    git clone --depth 1 https://github.com/radareorg/radare2 "${radare_dir}" >> "${LOG_FILE}" 2>&1 || {
        log_error "Failed to clone Radare2"
        return 1
    }
    
    log_info "Building and installing Radare2..."
    cd "${radare_dir}"
    sys/install.sh >> "${LOG_FILE}" 2>&1 || {
        log_error "Failed to install Radare2"
        cd - > /dev/null
        return 1
    }
    cd - > /dev/null
    
    # Verify installation
    if command -v radare2 &> /dev/null; then
        log_success "Radare2 installed successfully"
        return 0
    else
        log_error "Radare2 installation verification failed"
        return 1
    fi
}

install_yara() {
    print_header "Installing YARA"
    
    log_info "Installing YARA and Python bindings..."
    
    apt-get install -y yara python3-yara >> "${LOG_FILE}" 2>&1 || {
        log_error "Failed to install YARA"
        return 1
    }
    
    if command -v yara &> /dev/null; then
        log_success "YARA installed successfully"
        return 0
    else
        log_error "YARA installation verification failed"
        return 1
    fi
}

install_strings_tools() {
    print_header "Installing String Analysis Tools"
    
    log_info "Installing strings and related tools..."
    
    apt-get install -y binutils strings floss >> "${LOG_FILE}" 2>&1 || {
        log_warning "Some string analysis tools failed to install"
    }
    
    log_success "String analysis tools installed"
    return 0
}

install_network_tools() {
    print_header "Installing Network Analysis Tools"
    
    local tools=(
        "tcpdump"
        "wireshark"
        "tshark"
        "nmap"
        "netcat"
        "dsniff"
    )
    
    log_info "Installing network analysis tools..."
    
    for tool in "${tools[@]}"; do
        apt-get install -y "${tool}" >> "${LOG_FILE}" 2>&1 || {
            log_warning "Failed to install ${tool}"
            continue
        }
        log_success "Installed ${tool}"
    done
    
    return 0
}

install_forensic_tools() {
    print_header "Installing Forensic Tools"
    
    local tools=(
        "sleuthkit"
        "autopsy"
        "foremost"
        "scalpel"
        "binwalk"
        "exiftool"
        "pff-tools"
    )
    
    log_info "Installing forensic tools..."
    
    for tool in "${tools[@]}"; do
        apt-get install -y "${tool}" >> "${LOG_FILE}" 2>&1 || {
            log_warning "Failed to install ${tool}"
            continue
        }
        log_success "Installed ${tool}"
    done
    
    return 0
}

verify_installations() {
    print_header "Verifying Installations"
    
    local tools_to_verify=(
        "python3:Python 3"
        "tcpdump:TCPDump"
        "tshark:TShark/Wireshark"
        "volatility:Volatility"
        "yara:YARA"
        "radare2:Radare2"
    )
    
    local verified=0
    local total=${#tools_to_verify[@]}
    
    for tool_info in "${tools_to_verify[@]}"; do
        IFS=':' read -r cmd name <<< "${tool_info}"
        
        if command -v "${cmd}" &> /dev/null; then
            log_success "${name} verified ✓"
            ((verified++))
        else
            log_error "${name} verification failed ✗"
        fi
    done
    
    log_info "Verification: ${verified}/${total} tools verified"
    
    return 0
}

generate_report() {
    local results=$1
    local report_path="${LOGS_DIR}/installation_report_${TIMESTAMP}.txt"
    
    cat > "${report_path}" << EOF
============================================================
FORENSIC TOOLS INSTALLATION REPORT (Linux)
============================================================

Installation Date: $(date +"%Y-%m-%d %H:%M:%S")
System: $(uname -a)

Installation Results:
------------------------------------------------------------
${results}

============================================================
Detailed logs: ${LOG_FILE}
============================================================
EOF
    
    log_info "Installation report saved to: ${report_path}"
    echo "${report_path}"
}

main() {
    print_header "AUTOMATED FORENSIC TOOLS INSTALLATION (Linux)"
    
    # Check prerequisites
    check_root
    check_internet || exit 1
    
    # Initialize
    create_directories
    log_info "Starting automated tool installation"
    
    # Update system
    update_system
    
    # Track results
    declare -A results
    
    # Install tools
    install_system_dependencies && results[SystemDeps]="SUCCESS" || results[SystemDeps]="FAILED"
    install_volatility3 && results[Volatility3]="SUCCESS" || results[Volatility3]="FAILED"
    install_ghidra && results[Ghidra]="SUCCESS" || results[Ghidra]="FAILED"
    install_radare2 && results[Radare2]="SUCCESS" || results[Radare2]="FAILED"
    install_yara && results[YARA]="SUCCESS" || results[YARA]="FAILED"
    install_strings_tools && results[StringTools]="SUCCESS" || results[StringTools]="FAILED"
    install_network_tools && results[NetworkTools]="SUCCESS" || results[NetworkTools]="FAILED"
    install_forensic_tools && results[ForensicTools]="SUCCESS" || results[ForensicTools]="FAILED"
    
    # Verify installations
    verify_installations
    
    # Generate report
    print_header "INSTALLATION SUMMARY"
    
    local report_content=""
    for tool in "${!results[@]}"; do
        local status="${results[$tool]}"
        if [[ "${status}" == "SUCCESS" ]]; then
            echo -e "${GREEN}✓${NC} ${tool}: ${status}"
            report_content+="✓ ${tool}: ${status}\n"
        else
            echo -e "${RED}✗${NC} ${tool}: ${status}"
            report_content+="✗ ${tool}: ${status}\n"
        fi
    done
    
    local report_path=$(generate_report "${report_content}")
    
    print_header "INSTALLATION COMPLETE"
    echo -e "Detailed logs: ${YELLOW}${LOG_FILE}${NC}"
    echo -e "Report: ${YELLOW}${report_path}${NC}"
    
    log_info "Installation process completed"
}

# Execute main function
main "$@"
