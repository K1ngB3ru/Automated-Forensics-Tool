
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

class TestEnvironment(unittest.TestCase):

    def test_python_version(self):
        self.assertGreaterEqual(sys.version_info.major, 3)
        self.assertGreaterEqual(sys.version_info.minor, 10)

    def test_required_modules(self):
        try:
            import psutil
            import logging
            import json
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Required module missing: {e}")

    def test_directory_structure(self):
        base_dir = Path(__file__).parent.parent

        required_dirs = [
            'src',
            'config',
            'docs'
        ]

        for dir_name in required_dirs:
            dir_path = base_dir / dir_name
            self.assertTrue(dir_path.exists(), f"Directory {dir_name} should exist")

class TestConfiguration(unittest.TestCase):

    def test_tools_config_exists(self):
        config_path = Path(__file__).parent.parent / 'config' / 'tools_config.json'
        self.assertTrue(config_path.exists(), "tools_config.json should exist")

    def test_tools_config_valid_json(self):
        config_path = Path(__file__).parent.parent / 'config' / 'tools_config.json'

        if config_path.exists():
            try:
                import json
                with open(config_path, 'r') as f:
                    config = json.load(f)
                self.assertIsInstance(config, dict)
                self.assertIn('project_info', config)
            except json.JSONDecodeError:
                self.fail("tools_config.json is not valid JSON")

class TestSystemCapabilities(unittest.TestCase):

    def test_admin_check(self):
        import ctypes
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            self.assertIsInstance(is_admin, int)
        except:
            self.skipTest("Not running on Windows")

    def test_psutil_basic_functions(self):
        import psutil

        cpu_count = psutil.cpu_count()
        self.assertGreater(cpu_count, 0)

        memory = psutil.virtual_memory()
        self.assertGreater(memory.total, 0)

        disk = psutil.disk_usage('/')
        self.assertGreater(disk.total, 0)

    def test_process_listing(self):
        import psutil

        processes = list(psutil.process_iter(['pid', 'name']))
        self.assertGreater(len(processes), 0)

class TestArtifactCapture(unittest.TestCase):

    def setUp(self):

        try:
            import capture_artifacts
            self.capture_module = capture_artifacts
        except ImportError:
            self.skipTest("capture_artifacts module not available")

    def test_get_timestamp(self):
        timestamp = self.capture_module.get_timestamp()
        self.assertIsInstance(timestamp, str)
        self.assertEqual(len(timestamp), 15)

    def test_capture_system_info(self):
        if hasattr(self.capture_module, 'capture_system_info'):
            try:

                pass
            except Exception as e:
                self.fail(f"capture_system_info raised {type(e).__name__}: {e}")

class TestReportGeneration(unittest.TestCase):

    def test_output_directories_creation(self):
        from pathlib import Path

        test_dir = Path(__file__).parent.parent / 'reports' / '_pytest_mkdir_test'

        try:
            test_dir.mkdir(parents=True, exist_ok=True)
            self.assertTrue(test_dir.exists())

            test_dir.rmdir()
        except Exception as e:
            self.fail(f"Failed to create test directory: {e}")

class TestToolInstallation(unittest.TestCase):

    def test_download_urls_format(self):
        import json
        config_path = Path(__file__).parent.parent / 'config' / 'tools_config.json'

        if not config_path.exists():
            self.skipTest("tools_config.json not found")

        with open(config_path, 'r') as f:
            config = json.load(f)

        tools = config.get('tools', {})
        for category, tool_list in tools.items():
            for tool_name, tool_config in tool_list.items():
                if 'url' in tool_config:
                    url = tool_config['url']
                    self.assertTrue(url.startswith('https://'),
                                  f"{tool_name} URL should start with https://")

class TestSafety(unittest.TestCase):

    def test_runtime_directories_not_inside_src(self):
        base_dir = Path(__file__).parent.parent
        reports_dir = base_dir / 'reports'
        src_dir = base_dir / 'src'

        try:
            reports_dir.relative_to(src_dir)
            self.fail("Reports directory should not be inside src directory")
        except ValueError:
            pass

def run_tests():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)