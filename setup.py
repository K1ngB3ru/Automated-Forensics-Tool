"""
Setup configuration for Automated Malware Analysis Tool
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="bitprobe-scan",
    version="1.0.0",
    author="MetaProbe Team",
    author_email="your.email@example.com",
    description="BitProbe — Scan: Simplifying digital forensics through automated bit-level inspection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/K1ngB3ru/Automated-Forensics-Tool",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
    ],
    python_requires='>=3.10',
    install_requires=[
        'psutil>=5.9.5',
        'WMI>=1.5.1',
        'pywin32>=305',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'pylint>=2.17.0',
            'autopep8>=2.0.0',
        ],
        'build': [
            'pyinstaller>=5.13.0',
        ],
        'full': [
            'volatility3>=2.5.0',
            'yara-python>=4.3.1',
            'pefile>=2023.2.7',
        ]
    },
    entry_points={
        'console_scripts': [
            'bitprobe=forensic_master:main',
            'bitprobe-build=build_executable:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.json', '*.ini', '*.md'],
    },
    project_urls={
        'Documentation': 'https://github.com/K1ngB3ru/Automated-Forensics-Tool/wiki',
        'Source': 'https://github.com/K1ngB3ru/Automated-Forensics-Tool',
        'Tracker': 'https://github.com/K1ngB3ru/Automated-Forensics-Tool/issues',
    },
)