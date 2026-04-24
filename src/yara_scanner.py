
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

from paths import ARTIFACTS_DIR, INDIVIDUAL_REPORTS_DIR, RULES_DIR

try:
    import yara
    YARA_AVAILABLE = True
except ImportError:
    YARA_AVAILABLE = False
    print("⚠️  YARA not installed. Install with: pip install yara-python")

logger = logging.getLogger(__name__)

REPORTS_DIR = INDIVIDUAL_REPORTS_DIR

def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

class YARAScanner:

    def __init__(self, rules_path=None):
        if not YARA_AVAILABLE:
            logger.error("YARA is not installed")
            self.rules = None
            return

        if rules_path is None:
            rules_path = RULES_DIR / "malware_rules.yar"

        self.rules_path = Path(rules_path)
        self.rules = None
        self.load_rules()

    def load_rules(self):
        try:
            if not self.rules_path.exists():
                logger.error(f"YARA rules file not found: {self.rules_path}")
                return False

            logger.info(f"Loading YARA rules from: {self.rules_path}")
            self.rules = yara.compile(filepath=str(self.rules_path))
            logger.info("✓ YARA rules loaded successfully")
            return True

        except yara.SyntaxError as e:
            logger.error(f"YARA rule syntax error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load YARA rules: {e}")
            return False

    def scan_string(self, data_string):
        if not self.rules:
            return []

        try:
            matches = self.rules.match(data=data_string)
            return matches
        except Exception as e:
            logger.error(f"Error scanning string: {e}")
            return []

    def scan_file(self, file_path):
        if not self.rules:
            return []

        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return []

            logger.info(f"Scanning file: {file_path}")
            matches = self.rules.match(filepath=str(file_path))

            if matches:
                logger.warning(f"[THREAT]  Threats detected in {file_path.name}: {len(matches)} matches")
            else:
                logger.info(f"[CLEAN] No threats detected in {file_path.name}")

            return matches

        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {e}")
            return []

def scan_artifacts_directory(artifacts_dir):
    logger.info("Starting YARA scan of captured artifacts...")

    scanner = YARAScanner()
    if not scanner.rules:
        logger.error("[ERROR] YARA rules not loaded, skipping scan")
        return None

    results = {
        'total_files_scanned': 0,
        'files_with_threats': 0,
        'total_threats': 0,
        'threats': []
    }

    artifacts_path = Path(artifacts_dir)
    if not artifacts_path.exists():
        logger.error(f"[ERROR] Artifacts directory not found: {artifacts_path}")
        return results

    for artifact_file in artifacts_path.rglob("*.txt"):
        try:
            results['total_files_scanned'] += 1
            matches = scanner.scan_file(artifact_file)

            if matches:
                results['files_with_threats'] += 1
                results['total_threats'] += len(matches)

                for match in matches:
                    threat_info = {
                        'file': str(artifact_file.relative_to(artifacts_path)),
                        'rule': match.rule,
                        'severity': match.meta.get('severity', 'UNKNOWN') if hasattr(match, 'meta') else 'UNKNOWN',
                        'category': match.meta.get('category', 'UNKNOWN') if hasattr(match, 'meta') else 'UNKNOWN',
                        'description': match.meta.get('description', 'No description') if hasattr(match, 'meta') else 'No description'
                    }
                    results['threats'].append(threat_info)

        except Exception as e:
            logger.error(f"Error scanning {artifact_file}: {e}")
            continue

    logger.info(f"YARA scan complete: {results['total_files_scanned']} files scanned, {results['total_threats']} threats found")

    return results

def generate_yara_report(scan_results):
    if not scan_results:
        logger.error("No scan results to report")
        return None

    timestamp = get_timestamp()

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORTS_DIR / f"yara_scan_report_{timestamp}.txt"

    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("YARA MALWARE DETECTION REPORT\n")
            f.write("="*80 + "\n\n")
            f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Files Scanned: {scan_results['total_files_scanned']}\n")
            f.write(f"Files with Threats: {scan_results['files_with_threats']}\n")
            f.write(f"Total Threats Detected: {scan_results['total_threats']}\n\n")

            if scan_results['total_threats'] == 0:
                f.write("✓ NO THREATS DETECTED\n")
                f.write("\nAll scanned artifacts appear clean.\n")
            else:
                f.write("⚠️  THREATS DETECTED!\n\n")
                f.write("="*80 + "\n")
                f.write("THREAT DETAILS\n")
                f.write("="*80 + "\n\n")

                critical = [t for t in scan_results['threats'] if t['severity'] == 'CRITICAL']
                high = [t for t in scan_results['threats'] if t['severity'] == 'HIGH']
                medium = [t for t in scan_results['threats'] if t['severity'] == 'MEDIUM']
                low = [t for t in scan_results['threats'] if t['severity'] == 'LOW']

                if critical:
                    f.write(f"\n🔴 CRITICAL Threats ({len(critical)}):\n")
                    f.write("-"*80 + "\n")
                    for threat in critical:
                        f.write(f"\nRule: {threat['rule']}\n")
                        f.write(f"File: {threat['file']}\n")
                        f.write(f"Category: {threat['category']}\n")
                        f.write(f"Description: {threat['description']}\n")

                if high:
                    f.write(f"\n🟠 HIGH Severity Threats ({len(high)}):\n")
                    f.write("-"*80 + "\n")
                    for threat in high:
                        f.write(f"\nRule: {threat['rule']}\n")
                        f.write(f"File: {threat['file']}\n")
                        f.write(f"Category: {threat['category']}\n")
                        f.write(f"Description: {threat['description']}\n")

                if medium:
                    f.write(f"\n🟡 MEDIUM Severity Threats ({len(medium)}):\n")
                    f.write("-"*80 + "\n")
                    for threat in medium:
                        f.write(f"\nRule: {threat['rule']}\n")
                        f.write(f"File: {threat['file']}\n")
                        f.write(f"Category: {threat['category']}\n")
                        f.write(f"Description: {threat['description']}\n")

                if low:
                    f.write(f"\n🟢 LOW Severity Threats ({len(low)}):\n")
                    f.write("-"*80 + "\n")
                    for threat in low:
                        f.write(f"\nRule: {threat['rule']}\n")
                        f.write(f"File: {threat['file']}\n")
                        f.write(f"Category: {threat['category']}\n")
                        f.write(f"Description: {threat['description']}\n")

            f.write("\n" + "="*80 + "\n")
            f.write("RECOMMENDATIONS\n")
            f.write("="*80 + "\n\n")

            if scan_results['total_threats'] > 0:
                f.write("1. Investigate all flagged artifacts immediately\n")
                f.write("2. Isolate affected systems from network\n")
                f.write("3. Perform deep malware analysis on suspicious files\n")
                f.write("4. Check for lateral movement indicators\n")
                f.write("5. Review all user accounts and privileges\n")
                f.write("6. Update antivirus and run full system scan\n")
            else:
                f.write("1. Continue regular security monitoring\n")
                f.write("2. Maintain up-to-date antivirus definitions\n")
                f.write("3. Perform periodic forensic analysis\n")

            f.write("\n" + "="*80 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*80 + "\n")

        logger.info(f"YARA report generated: {report_file}")
        return report_file

    except Exception as e:
        logger.error(f"Failed to generate YARA report: {e}")
        return None

def run_yara_analysis():
    if not YARA_AVAILABLE:
        logger.warning("YARA not available, skipping malware scan")
        return None

    logger.info("="*60)
    logger.info("Starting YARA Malware Analysis")
    logger.info("="*60)

    artifacts_dir = ARTIFACTS_DIR
    scan_results = scan_artifacts_directory(artifacts_dir)

    if not scan_results:
        logger.error("YARA scan failed")
        return None

    report_file = generate_yara_report(scan_results)

    print(f"\n{'='*60}")
    print("YARA SCAN SUMMARY")
    print(f"{'='*60}")
    print(f"Files Scanned: {scan_results['total_files_scanned']}")
    print(f"Threats Found: {scan_results['total_threats']}")

    if scan_results['total_threats'] > 0:
        print(f"\n⚠️  WARNING: {scan_results['total_threats']} potential threats detected!")
        print(f"Check report: {report_file}")
    else:
        print(f"\n✓ No threats detected - System appears clean")

    print(f"{'='*60}\n")

    return report_file

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_yara_analysis()
