#!/usr/bin/env python3
"""Script to update golden test expected outputs."""

import argparse
import sys
from pathlib import Path
import shutil

from golden_runner import run_golden_case, discover_cases, load_spec


def update_golden_case(case_dir: str, verbose: bool = False):
    """
    Update expected outputs for a golden test case.
    
    Args:
        case_dir: Path to test case directory
        verbose: Print detailed information
    
    Returns:
        True if update successful
    """
    case_path = Path(case_dir)
    
    if verbose:
        print(f"Updating {case_path}...")
    
    # Run the test to generate actual outputs
    spec = load_spec(case_path / "config.yaml")
    result = run_golden_case(case_dir, spec=spec, save_artifacts=True)
    
    # Copy artifacts to expected files
    artifacts_dir = case_path / "artifacts"
    
    if artifacts_dir.exists():
        actual_output = artifacts_dir / "actual_output.csv"
        actual_report = artifacts_dir / "actual_report.json"
        
        if actual_output.exists():
            shutil.copy(actual_output, case_path / "expected_output.csv")
            if verbose:
                print(f"  Updated expected_output.csv")
        
        if actual_report.exists():
            shutil.copy(actual_report, case_path / "expected_report.json")
            if verbose:
                print(f"  Updated expected_report.json")
        
        return True
    else:
        print(f"  WARNING: No artifacts found for {case_path}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Update golden test expected outputs"
    )
    parser.add_argument(
        "cases",
        nargs="*",
        help="Specific test cases to update (updates all if none specified)"
    )
    parser.add_argument(
        "--marketplace",
        choices=["mercado_livre", "shopee", "amazon"],
        help="Update only tests for specific marketplace"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed information"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes"
    )
    
    args = parser.parse_args()
    
    # Determine which cases to update
    if args.cases:
        cases = args.cases
    else:
        cases = discover_cases()
        
        # Filter by marketplace if specified
        if args.marketplace:
            cases = [c for c in cases if args.marketplace in c]
    
    if not cases:
        print("No test cases found")
        return 1
    
    # Update cases
    print(f"Updating {len(cases)} test case(s)...")
    
    if args.dry_run:
        print("DRY RUN - no files will be modified")
        for case in cases:
            print(f"  Would update: {case}")
        return 0
    
    success_count = 0
    for case in cases:
        if update_golden_case(case, verbose=args.verbose):
            success_count += 1
    
    print(f"\nUpdated {success_count}/{len(cases)} test cases successfully")
    
    return 0 if success_count == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())