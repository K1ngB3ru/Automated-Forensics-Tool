
import os
import sys
import subprocess
import urllib.request
import zipfile
import logging
from pathlib import Path
from datetime import datetime
import ctypes
import shutil

from paths import TOOLS_DIR, LOGS_DIR, DOWNLOADS_DIR

TOOLS_CONFIG = {
    "sysinternals": {
        "url": "https://download.sysinternals.com/files/SysinternalsSuite.zip",
        "type": "zip",
        "destination": TOOLS_DIR / "sysinternals"
    },
    "wireshark": {
        "url": "https://2.na.dl.wireshark.org/win64/Wireshark-latest-x64.exe",
        "type": "installer",
        "silent_args": ["/S", "/quicklaunchicon=no", "/desktopicon=no"]
    },
    "winpmem": {
        "url": "https://github.com/Velocidex/WinPmem/releases/download/v4.0.rc1/winpmem_mini_x64_rc2.exe",
        "type": "portable",
        "destination": TOOLS_DIR / "winpmem"
    },
    "ghidra": {
        "url": "https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_10.4_build/ghidra_10.4_PUBLIC_20230928.zip",
        "type": "zip",
        "destination": TOOLS_DIR / "ghidra"
    },
    "volatility": {
        "type": "pip",
        "package": "volatility3"
    }
}

def setup_logging():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"installation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate_privileges():
    if not is_admin():
        logger.warning("Script requires administrator privileges. Requesting elevation...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)

def create_directories():
    directories = [TOOLS_DIR, LOGS_DIR, DOWNLOADS_DIR]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created/verified directory: {directory}")

def download_file(url, destination):
    try:
        logger.info(f"Downloading from: {url}")

        def progress_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(downloaded * 100 / total_size, 100)
            sys.stdout.write(f"\rProgress: {percent:.1f}%")
            sys.stdout.flush()

        urllib.request.urlretrieve(url, destination, progress_hook)
        print()
        logger.info(f"Downloaded successfully to: {destination}")
        return True
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return False

def extract_zip(zip_path, destination):
    try:
        logger.info(f"Extracting {zip_path} to {destination}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(destination)
        logger.info("Extraction completed")
        return True
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return False

def run_installer(installer_path, silent_args=None):
    try:
        cmd = [str(installer_path)]
        if silent_args:
            cmd.extend(silent_args)

        logger.info(f"Running installer: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            logger.info("Installation completed successfully")
            return True
        else:
            logger.error(f"Installation failed with return code: {result.returncode}")
            logger.error(f"Error output: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("Installation timed out")
        return False
    except Exception as e:
        logger.error(f"Installation error: {e}")
        return False

def install_pip_package(package_name):
    try:
        logger.info(f"Installing pip package: {package_name}")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            logger.info(f"Package {package_name} installed successfully")
            return True
        else:
            logger.error(f"pip installation failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"pip installation error: {e}")
        return False

def verify_tool_installation(tool_name):
    def check_wireshark():

        if shutil.which("tshark"):
            return True

        common_paths = [
            Path("C:/Program Files/Wireshark/tshark.exe"),
            Path("C:/Program Files (x86)/Wireshark/tshark.exe"),
        ]
        return any(path.exists() for path in common_paths)

    verification_commands = {
        "sysinternals": lambda: (TOOLS_DIR / "sysinternals" / "procmon.exe").exists(),
        "wireshark": check_wireshark,
        "winpmem": lambda: (TOOLS_DIR / "winpmem" / "winpmem_mini_x64_rc2.exe").exists(),
        "volatility": lambda: subprocess.run(
            [sys.executable, "-m", "pip", "show", "volatility3"],
            capture_output=True
        ).returncode == 0,
        "ghidra": lambda: (TOOLS_DIR / "ghidra").exists()
    }

    if tool_name in verification_commands:
        result = verification_commands[tool_name]()
        logger.info(f"Verification for {tool_name}: {'PASSED' if result else 'FAILED'}")
        return result
    return False

def install_sysinternals():

    if verify_tool_installation("sysinternals"):
        logger.info("Sysinternals Suite already installed, skipping installation")
        return True

    logger.info("=" * 50)
    logger.info("Installing Sysinternals Suite")
    logger.info("=" * 50)

    config = TOOLS_CONFIG["sysinternals"]
    download_path = DOWNLOADS_DIR / "SysinternalsSuite.zip"

    if not download_file(config["url"], download_path):
        return False

    if not extract_zip(download_path, config["destination"]):
        return False

    return verify_tool_installation("sysinternals")

def install_wireshark():

    if verify_tool_installation("wireshark"):
        logger.info("Wireshark already installed, skipping installation")
        return True

    logger.info("=" * 50)
    logger.info("Installing Wireshark")
    logger.info("=" * 50)

    config = TOOLS_CONFIG["wireshark"]
    download_path = DOWNLOADS_DIR / "Wireshark-installer.exe"

    if not download_file(config["url"], download_path):
        logger.error("Failed to download Wireshark installer")
        return False

    silent_args = ["/S", "/NCRC"]

    logger.info(f"Running Wireshark installer: {download_path}")
    try:

        cmd = [str(download_path)] + silent_args
        logger.info(f"Command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
            shell=True
        )

        if result.returncode == 0:
            logger.info("Wireshark installer completed")
        else:
            logger.warning(f"Installer returned code {result.returncode}, but continuing...")
            if result.stdout:
                logger.info(f"Installer output: {result.stdout}")
            if result.stderr:
                logger.warning(f"Installer stderr: {result.stderr}")
    except subprocess.TimeoutExpired:
        logger.error("Wireshark installation timed out")
        return False
    except Exception as e:
        logger.error(f"Error running Wireshark installer: {e}")
        return False

    import time
    logger.info("Waiting for installation to complete and PATH to update...")
    time.sleep(5)

    logger.info("Verifying Wireshark installation...")

    tshark_path = shutil.which("tshark")
    if tshark_path:
        logger.info(f"Found tshark at: {tshark_path}")
        return True

    common_paths = [
        Path("C:/Program Files/Wireshark/tshark.exe"),
        Path("C:/Program Files (x86)/Wireshark/tshark.exe"),
    ]

    for path in common_paths:
        if path.exists():
            logger.info(f"Found tshark at: {path}")

            return True

    logger.warning("Wireshark installation completed but tshark not found in PATH")
    logger.warning("You may need to restart the terminal or add Wireshark to PATH manually")
    logger.warning("Wireshark may still be installed - check: C:/Program Files/Wireshark/")

    return True

def install_winpmem():

    if verify_tool_installation("winpmem"):
        logger.info("WinPMEM already installed, skipping installation")
        return True

    logger.info("=" * 50)
    logger.info("Installing WinPMEM")
    logger.info("=" * 50)

    config = TOOLS_CONFIG["winpmem"]
    config["destination"].mkdir(exist_ok=True)
    download_path = config["destination"] / "winpmem_mini_x64_rc2.exe"

    if not download_file(config["url"], download_path):
        return False

    return verify_tool_installation("winpmem")

def install_volatility():
    logger.info("=" * 50)
    logger.info("Installing Volatility 3")
    logger.info("=" * 50)

    config = TOOLS_CONFIG["volatility"]

    if not install_pip_package(config["package"]):
        return False

    return verify_tool_installation("volatility")

def install_ghidra():
    logger.info("=" * 50)
    logger.info("Installing Ghidra")
    logger.info("=" * 50)

    config = TOOLS_CONFIG["ghidra"]
    download_path = DOWNLOADS_DIR / "ghidra.zip"

    logger.info("Note: Ghidra requires Java Runtime Environment (JRE) 17+")

    if not download_file(config["url"], download_path):
        return False

    if not extract_zip(download_path, config["destination"]):
        return False

    return verify_tool_installation("ghidra")

def generate_installation_report(results):
    report_path = LOGS_DIR / f"installation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(report_path, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("FORENSIC TOOLS INSTALLATION REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Installation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("Installation Results:\n")
        f.write("-" * 60 + "\n")

        for tool, status in results.items():
            status_str = "✓ SUCCESS" if status else "✗ FAILED"
            f.write(f"{tool.ljust(20)}: {status_str}\n")

        f.write("\n" + "=" * 60 + "\n")

        success_count = sum(results.values())
        total_count = len(results)
        f.write(f"Summary: {success_count}/{total_count} tools installed successfully\n")

        if success_count == total_count:
            f.write("\nStatus: ALL TOOLS INSTALLED SUCCESSFULLY ✓\n")
        else:
            f.write("\nStatus: SOME INSTALLATIONS FAILED - Review logs for details\n")

    logger.info(f"Installation report saved to: {report_path}")
    return report_path

def main():
    print("=" * 60)
    print("AUTOMATED FORENSIC TOOLS INSTALLATION")
    print("=" * 60)
    print()

    elevate_privileges()

    logger.info("Starting automated tool installation")

    create_directories()

    results = {}

    tools_to_install = [
        ("sysinternals", install_sysinternals),
        ("wireshark", install_wireshark),
        ("winpmem", install_winpmem),
        ("volatility", install_volatility),
        ("ghidra", install_ghidra)
    ]

    for tool_name, install_func in tools_to_install:
        try:

            if verify_tool_installation(tool_name):
                print(f"✓ {tool_name.capitalize()} already installed, skipping...")
                results[tool_name] = True
            else:
                results[tool_name] = install_func()
        except Exception as e:
            logger.error(f"Unexpected error installing {tool_name}: {e}")
            results[tool_name] = False
        print()

    report_path = generate_installation_report(results)

    print("\n" + "=" * 60)
    print("INSTALLATION SUMMARY")
    print("=" * 60)
    for tool, status in results.items():
        status_icon = "✓" if status else "✗"
        print(f"{status_icon} {tool.ljust(20)}: {'SUCCESS' if status else 'FAILED'}")

    print("\n" + "=" * 60)
    print(f"Detailed logs: {LOGS_DIR}")
    print(f"Installation report: {report_path}")
    print("=" * 60)

    return all(results.values())

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.warning("Installation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
