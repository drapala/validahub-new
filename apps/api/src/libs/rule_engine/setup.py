from setuptools import setup, find_packages

setup(
    name="rule_engine",
    version="0.1.0",
    description="ValidaHub Rule Engine - Interpretative YAML-based validation engine",
    author="ValidaHub Team",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0",
    ],
    python_requires=">=3.8",
)