from __future__ import annotations

import sys
from pathlib import Path


def project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


ARTIFACTS_DIR = project_root() / "artifacts"
REPORTS_DIR = project_root() / "reports"
INDIVIDUAL_REPORTS_DIR = REPORTS_DIR / "individual"
MASTER_REPORTS_DIR = REPORTS_DIR / "master"
LOGS_DIR = ARTIFACTS_DIR / "logs"
DOWNLOADS_DIR = project_root() / "downloads"
TOOLS_DIR = project_root() / "tools"
RULES_DIR = project_root() / "rules"
