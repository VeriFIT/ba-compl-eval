#!/usr/bin/env python3
"""
Script to run hoaba on pairs of HOA automata with timeout.

Reads an input file containing pairs of automata paths (separated by semicolon)
and runs hoaba on each pair with a 20-second timeout.
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path


def run_hoaba_with_timeout(hoaba_path, aut1_path, aut2_path, timeout=20):
    """
    Run hoaba on a pair of automata with a timeout.
    
    Args:
        hoaba_path: Path to the hoaba executable
        aut1_path: Path to the first automaton file
        aut2_path: Path to the second automaton file
        timeout: Timeout in seconds (default: 20)
    
    Returns:
        tuple: (success, return_code, stdout, stderr, timed_out)
    """
    cmd = [hoaba_path, aut1_path, aut2_path]
    
    try:
        result = subprocess.run(
            cmd,
            timeout=timeout,
            capture_output=True,
            text=True
        )
        return (True, result.returncode, result.stdout, result.stderr, False)
    
    except subprocess.TimeoutExpired as e:
        return (False, None, e.stdout if e.stdout else "", e.stderr if e.stderr else "", True)
    
    except Exception as e:
        return (False, None, "", str(e), False)


def parse_input_file(input_file, base_dir=None):
    """
    Parse input file containing pairs of automata paths.
    
    Args:
        input_file: Path to the input file
        base_dir: Base directory for resolving relative paths (default: input file's directory)
    
    Returns:
        list: List of tuples (aut1_path, aut2_path)
    """
    if base_dir is None:
        base_dir = Path(input_file).parent
    else:
        base_dir = Path(base_dir)
    
    pairs = []
    
    with open(input_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Split by semicolon
            parts = line.split(';')
            if len(parts) != 2:
                print(f"Warning: Line {line_num} does not contain exactly 2 paths (separated by ';'). Skipping.", 
                      file=sys.stderr)
                continue
            
            aut1 = parts[0].strip()
            aut2 = parts[1].strip()
            
            # Resolve paths relative to base_dir
            aut1_path = base_dir / aut1
            aut2_path = base_dir / aut2
            
            pairs.append((str(aut1_path), str(aut2_path)))
    
    return pairs


def main():
    parser = argparse.ArgumentParser(
        description='Run hoaba on pairs of HOA automata with timeout'
    )
    parser.add_argument(
        'input_file',
        help='Input file containing pairs of automata paths (separated by semicolon)'
    )
    parser.add_argument(
        '--hoaba',
        default='./hoaba',
        help='Path to hoaba executable (default: ./hoaba)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=20,
        help='Timeout in seconds for each hoaba run (default: 20)'
    )
    parser.add_argument(
        '--base-dir',
        help='Base directory for resolving relative paths (default: input file directory)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print detailed output for each run'
    )
    parser.add_argument(
        '--continue-on-error',
        action='store_true',
        help='Continue processing even if a pair fails'
    )
    
    args = parser.parse_args()
    
    # Check if hoaba exists
    if not os.path.exists(args.hoaba):
        print(f"Error: hoaba executable not found at: {args.hoaba}", file=sys.stderr)
        print(f"Please compile hoaba or specify correct path with --hoaba", file=sys.stderr)
        return 1
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        return 1
    
    # Parse input file
    try:
        pairs = parse_input_file(args.input_file, args.base_dir)
    except Exception as e:
        print(f"Error parsing input file: {e}", file=sys.stderr)
        return 1
    
    if not pairs:
        print("Warning: No valid pairs found in input file", file=sys.stderr)
        return 0
    
    print(f"Found {len(pairs)} pairs to process")
    print(f"Timeout: {args.timeout} seconds")
    print(f"hoaba: {args.hoaba}")
    print("-" * 80)
    
    # Process each pair
    success_count = 0
    timeout_count = 0
    error_count = 0
    
    for idx, (aut1, aut2) in enumerate(pairs, 1):
        print(f"\n[{idx}/{len(pairs)}] Processing pair:")
        print(f"  First:  {aut1}")
        print(f"  Second: {aut2}")
        
        # Check if files exist
        if not os.path.exists(aut1):
            print(f"  ERROR: First automaton file not found!")
            error_count += 1
            if not args.continue_on_error:
                return 1
            continue
        
        if not os.path.exists(aut2):
            print(f"  ERROR: Second automaton file not found!")
            error_count += 1
            if not args.continue_on_error:
                return 1
            continue
        
        # Run hoaba
        success, returncode, stdout, stderr, timed_out = run_hoaba_with_timeout(
            args.hoaba, aut1, aut2, args.timeout
        )
        
        if timed_out:
            print(f"  TIMEOUT after {args.timeout} seconds")
            timeout_count += 1
            if args.verbose and stderr:
                print(f"  stderr: {stderr}")
        elif not success:
            print(f"  ERROR: {stderr}")
            error_count += 1
            if not args.continue_on_error:
                return 1
        elif returncode != 0:
            print(f"  FAILED with return code {returncode}")
            if args.verbose and stderr:
                print(f"  stderr: {stderr}")
            error_count += 1
            if not args.continue_on_error:
                return 1
        else:
            print(f"  SUCCESS")
            success_count += 1
            if args.verbose:
                if stdout:
                    print(f"  stdout: {stdout}")
                if stderr:
                    print(f"  stderr: {stderr}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print(f"  Total pairs:    {len(pairs)}")
    print(f"  Successful:     {success_count}")
    print(f"  Timeouts:       {timeout_count}")
    print(f"  Errors:         {error_count}")
    print("=" * 80)
    
    return 0 if error_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
