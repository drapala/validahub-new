#!/usr/bin/env python3
"""
Dependency checker for ValidaHub Backend
Verifies all required packages are installed with correct versions
"""

import sys
import importlib.metadata
from typing import Dict, List, Tuple

# Required packages with minimum versions
REQUIRED_PACKAGES = {
    "fastapi": "0.100.0",
    "uvicorn": "0.20.0",
    "pydantic": "2.0.0",
    "pydantic-settings": "2.0.0",
    "pandas": "2.0.0",
    "python-multipart": "0.0.5",
    "python-dotenv": "1.0.0",
}

# Optional packages for development
OPTIONAL_PACKAGES = {
    "pytest": "7.0.0",
    "pytest-asyncio": "0.20.0",
    "black": "23.0.0",
    "ruff": "0.1.0",
}


def parse_version(version_str: str) -> Tuple[int, ...]:
    """Parse version string to tuple for comparison"""
    try:
        return tuple(int(x) for x in version_str.split(".")[:3])
    except:
        return (0, 0, 0)


def check_package(package: str, min_version: str) -> Tuple[bool, str]:
    """Check if package is installed and meets minimum version"""
    try:
        installed_version = importlib.metadata.version(package)
        installed_tuple = parse_version(installed_version)
        required_tuple = parse_version(min_version)
        
        if installed_tuple >= required_tuple:
            return True, installed_version
        else:
            return False, f"{installed_version} (requires >= {min_version})"
    except importlib.metadata.PackageNotFoundError:
        return False, "Not installed"


def main():
    """Main dependency checker"""
    print("🔍 Checking ValidaHub Backend Dependencies\n")
    print("=" * 50)
    
    all_ok = True
    missing_required = []
    outdated_required = []
    
    # Check required packages
    print("\n📦 Required Packages:")
    print("-" * 30)
    
    for package, min_version in REQUIRED_PACKAGES.items():
        is_ok, status = check_package(package, min_version)
        
        if is_ok:
            print(f"  ✅ {package:20} {status}")
        else:
            all_ok = False
            if "Not installed" in status:
                missing_required.append(package)
                print(f"  ❌ {package:20} {status}")
            else:
                outdated_required.append(f"{package} {status}")
                print(f"  ⚠️  {package:20} {status}")
    
    # Check optional packages
    print("\n📦 Optional Packages (Development):")
    print("-" * 30)
    
    for package, min_version in OPTIONAL_PACKAGES.items():
        is_ok, status = check_package(package, min_version)
        
        if is_ok:
            print(f"  ✅ {package:20} {status}")
        else:
            print(f"  ⭕ {package:20} {status}")
    
    # Summary and recommendations
    print("\n" + "=" * 50)
    
    if all_ok:
        print("✅ All required dependencies are installed and up to date!")
        return 0
    else:
        print("❌ Dependency issues found:\n")
        
        if missing_required:
            print(f"Missing packages: {', '.join(missing_required)}")
        
        if outdated_required:
            print(f"Outdated packages: {', '.join(outdated_required)}")
        
        print("\n💡 To fix, run:")
        print("   pip install -r requirements.txt --upgrade")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())