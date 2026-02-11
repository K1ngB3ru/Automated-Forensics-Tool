"""
BitProbe — Scan: Build Script
Create Standalone Executable using PyInstaller

Usage:
    python build_executable.py
    
Output:
    dist/BitProbe-Scan.exe - Standalone executable
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

# Get project root directory (parent of src directory)
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = Path(__file__).parent

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    spec = importlib.util.find_spec("PyInstaller")
    if spec is not None:
        print("✓ PyInstaller is installed")
        return True
    else:
        print("✗ PyInstaller not found")
        print("  Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed")
        return True

def create_spec_file():
    """Create PyInstaller spec file for custom build"""
    # Use absolute paths for source files
    forensic_master = str(SRC_DIR / 'forensic_master.py')
    install_tools = str(SRC_DIR / 'install_tools.py')
    capture_artifacts = str(SRC_DIR / 'capture_artifacts.py')
    icon_path = str(PROJECT_ROOT / 'icon.ico') if (PROJECT_ROOT / 'icon.ico').exists() else None
    icon_line = f"    icon=r'{icon_path}'," if icon_path else "    icon=None,"
    
    spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    [r'{forensic_master}'],
    pathex=[r'{SRC_DIR}'],
    binaries=[],
    datas=[
        (r'{install_tools}', '.'),
        (r'{capture_artifacts}', '.'),
    ],
    hiddenimports=[
        'psutil',
        'wmi',
        'pywin32',
        'win32com',
        'win32api',
        'win32con',
        'pywintypes',
        'winreg',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BitProbe-Scan',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
{icon_line}
    uac_admin=True,  # Request admin privileges
)
"""
    
    spec_file = PROJECT_ROOT / 'forensic_tool.spec'
    with open(spec_file, 'w') as f:
        f.write(spec_content)
    
    print("✓ Spec file created")

def build_executable():
    """Build the executable using PyInstaller"""
    print("\n" + "="*60)
    print("Building Forensic Analysis Tool Executable")
    print("="*60 + "\n")
    
    # Check dependencies
    if not check_pyinstaller():
        print("✗ Failed to install PyInstaller")
        return False
    
    # Create spec file
    create_spec_file()
    
    # Build using spec file
    print("\nBuilding executable (this may take a few minutes)...")
    
    try:
        spec_file = PROJECT_ROOT / 'forensic_tool.spec'
        cmd = [
            'pyinstaller',
            '--clean',
            '--noconfirm',
            str(spec_file)
        ]
        
        # Run from project root directory
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
        
        if result.returncode == 0:
            exe_path = PROJECT_ROOT / 'dist' / 'BitProbe-Scan.exe'
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024*1024)
                print(f"\n{'='*60}")
                print("✓ BUILD SUCCESSFUL!")
                print(f"{'='*60}")
                print(f"\nExecutable Location: {exe_path.absolute()}")
                print(f"File Size: {size_mb:.2f} MB")
                print(f"\nUsage:")
                print(f"  1. Copy BitProbe-Scan.exe to target system")
                print(f"  2. Run as Administrator")
                print(f"  3. All dependencies will be installed automatically")
                print(f"  4. Artifacts and reports will be generated")
                return True
            else:
                print("✗ Executable not found after build")
                return False
        else:
            print(f"✗ Build failed")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Build error: {e}")
        return False

def create_simple_build():
    """Simple build command without spec file"""
    print("\nAttempting simple build...")
    
    forensic_master = SRC_DIR / 'forensic_master.py'
    install_tools = SRC_DIR / 'install_tools.py'
    capture_artifacts = SRC_DIR / 'capture_artifacts.py'
    
    cmd = [
        'pyinstaller',
        '--onefile',
        '--name=BitProbe-Scan',
        '--uac-admin',
        '--console',
        '--clean',
        '--add-data', f'{install_tools};.',
        '--add-data', f'{capture_artifacts};.',
        '--hidden-import=psutil',
        '--hidden-import=wmi',
        '--hidden-import=win32com',
        '--hidden-import=winreg',
        str(forensic_master)
    ]
    
    try:
        # Run from project root directory
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
        
        if result.returncode == 0:
            print("✓ Simple build successful")
            return True
        else:
            print(f"✗ Simple build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         FORENSIC ANALYSIS TOOL - EXECUTABLE BUILDER         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    success = build_executable()
    
    if not success:
        print("\nTrying alternative build method...")
        success = create_simple_build()
    
    if success:
        print("\n✓ Build complete! Check the 'dist' folder.")
    else:
        print("\n✗ Build failed. Check errors above.")
        print("\nTroubleshooting:")
        print("  1. Ensure all Python scripts are in the src/ directory")
        print("  2. Install missing packages: pip install -r requirements.txt")
        print("  3. Try running from project root: python src/build_executable.py")
    
    sys.exit(0 if success else 1)
