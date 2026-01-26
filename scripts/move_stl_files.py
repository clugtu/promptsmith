#!/usr/bin/env python
"""Find all .stl files in subdirectories and move them to the current directory."""

import os
import shutil
from pathlib import Path


def move_stl_files(dry_run=False):
    """Find and move all .stl files from subdirectories to current directory.
    
    Renames files using sequential numbers based on existing file count.
    
    Args:
        dry_run: If True, only print what would be done without moving files
    """
    current_dir = Path.cwd()
    stl_files = []
    
    # Find all .stl files in subdirectories (not in current directory)
    for stl_file in current_dir.rglob("*.stl"):
        if stl_file.parent != current_dir:
            stl_files.append(stl_file)
    
    if not stl_files:
        print("No .stl files found in subdirectories.")
        return
    
    # Count existing .stl files in current directory
    existing_stl_count = len(list(current_dir.glob("*.stl")))
    print(f"Found {len(stl_files)} .stl file(s) in subdirectories")
    print(f"Existing .stl files in current directory: {existing_stl_count}\n")
    
    moved_count = 0
    next_number = existing_stl_count + 1
    
    for stl_file in stl_files:
        # Generate numbered filename
        target = current_dir / f"{next_number}.stl"
        relative_path = stl_file.relative_to(current_dir)
        
        # Find next available number if file exists
        while target.exists():
            next_number += 1
            target = current_dir / f"{next_number}.stl"
        
        if dry_run:
            print(f"Would move: {relative_path} -> {next_number}.stl")
        else:
            print(f"Moving: {relative_path} -> {next_number}.stl")
            shutil.move(str(stl_file), str(target))
            moved_count += 1
        
        next_number += 1
    
    print(f"\n{'Would move' if dry_run else 'Moved'}: {moved_count} file(s)")


if __name__ == "__main__":
    import sys
    
    # Check for --dry-run flag
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    
    if dry_run:
        print("=== DRY RUN MODE ===\n")
    
    try:
        move_stl_files(dry_run=dry_run)
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(1)
