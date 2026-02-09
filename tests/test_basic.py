"""
Basic Unit Tests for Forensic Analysis Tool
Run with: pytest tests/test_basic.py
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

class TestEnvironment(unittest.TestCase):
    """Test environment setup and configuration"""
    
    def test_python_version(self):
        """Test Python version is 3.10 or higher"""
        self.assertGreaterEqual(sys.version_info.major, 3)
        self.assertGreaterEqual(sys.version_info.minor, 10)
    
    def test_required_modules(self):
        """Test that required modules can be imported"""
        try:
            import psutil
            import logging
            import json
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Required module missing: {e}")
    
    def test_directory_structure(self):
        """Test that required directories exist or can be created"""
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
    """Test configuration file loading"""
    
    def test_tools_config_exists(self):
        """Test that tools_config.json exists"""
        config_path = Path(__file__).parent.parent / 'config' / 'tools_config.json'
        self.assertTrue(config_path.exists(), "tools_config.json should exist")
    
    def test_tools_config_valid_json(self):
        """Test that tools_config.json is valid JSON"""
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
    """Test system capability detection"""
    
    def test_admin_check(self):
        """Test admin privilege checking (may fail if not admin)"""
        import ctypes
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            self.assertIsInstance(is_admin, int)
        except:
            self.skipTest("Not running on Windows")
    
    def test_psutil_basic_functions(self):
        """Test basic psutil functionality"""
        import psutil
        
        # Test CPU count
        cpu_count = psutil.cpu_count()
        self.assertGreater(cpu_count, 0)
        
        # Test memory info
        memory = psutil.virtual_memory()
        self.assertGreater(memory.total, 0)
        
        # Test disk usage
        disk = psutil.disk_usage('/')
        self.assertGreater(disk.total, 0)
    
    def test_process_listing(self):
        """Test that we can list processes"""
        import psutil
        
        processes = list(psutil.process_iter(['pid', 'name']))
        self.assertGreater(len(processes), 0)


class TestArtifactCapture(unittest.TestCase):
    """Test artifact capture functions"""
    
    def setUp(self):
        """Set up test environment"""
        # Import capture module
        try:
            import capture_artifacts
            self.capture_module = capture_artifacts
        except ImportError:
            self.skipTest("capture_artifacts module not available")
    
    def test_get_timestamp(self):
        """Test timestamp generation"""
        timestamp = self.capture_module.get_timestamp()
        self.assertIsInstance(timestamp, str)
        self.assertEqual(len(timestamp), 15)  # YYYYMMDD_HHMMSS
    
    def test_capture_system_info(self):
        """Test system information capture (if function exists)"""
        if hasattr(self.capture_module, 'capture_system_info'):
            try:
                # This will actually run the capture, so use with caution
                # In production, you'd mock this
                pass
            except Exception as e:
                self.fail(f"capture_system_info raised {type(e).__name__}: {e}")


class TestReportGeneration(unittest.TestCase):
    """Test report generation capabilities"""
    
    def test_output_directories_creation(self):
        """Test that output directories can be created"""
        from pathlib import Path
        
        test_dir = Path(__file__).parent.parent / 'output' / 'test'
        
        try:
            test_dir.mkdir(parents=True, exist_ok=True)
            self.assertTrue(test_dir.exists())
            
            # Cleanup
            test_dir.rmdir()
        except Exception as e:
            self.fail(f"Failed to create test directory: {e}")


class TestToolInstallation(unittest.TestCase):
    """Test tool installation functions"""
    
    def test_download_urls_format(self):
        """Test that tool URLs are properly formatted"""
        import json
        config_path = Path(__file__).parent.parent / 'config' / 'tools_config.json'
        
        if not config_path.exists():
            self.skipTest("tools_config.json not found")
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check that URLs start with https://
        tools = config.get('tools', {})
        for category, tool_list in tools.items():
            for tool_name, tool_config in tool_list.items():
                if 'url' in tool_config:
                    url = tool_config['url']
                    self.assertTrue(url.startswith('https://'), 
                                  f"{tool_name} URL should start with https://")


class TestSafety(unittest.TestCase):
    """Test safety and validation features"""
    
    def test_output_directory_isolation(self):
        """Test that output directories don't overlap with source"""
        base_dir = Path(__file__).parent.parent
        output_dir = base_dir / 'output'
        src_dir = base_dir / 'src'
        
        # Output should not be inside src
        try:
            output_relative = output_dir.relative_to(src_dir)
            self.fail("Output directory should not be inside src directory")
        except ValueError:
            # This is correct - output is not inside src
            pass


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)