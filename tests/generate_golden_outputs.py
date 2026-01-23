#!/usr/bin/env python
"""Generate golden output files for regression testing.

This script runs create_image.py with various character files and options,
capturing the prompt outputs to use as baseline for testing.

Usage:
    python tests/generate_golden_outputs.py [--custom-path PATH]
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(args, output_file):
    """Run create_image.py and save output to file."""
    print(f"Generating: {output_file.name}...")
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(result.stdout, encoding='utf-8')
        print(f"  ✓ Saved to {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error: {e.stderr}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate golden output files for testing")
    parser.add_argument(
        "--custom-path",
        type=Path,
        help="Path to Custom character files (OneDrive location)"
    )
    args = parser.parse_args()
    
    # Paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    create_image = repo_root / "create_image.py"
    golden_dir = script_dir / "golden_outputs"
    
    # Git-tracked standees path
    standees_path = repo_root.parent / "shattered_citadel" / "assets" / "standees"
    
    # Custom path (OneDrive)
    custom_path = args.custom_path
    if not custom_path:
        # Try default locations
        candidates = [
            Path.home() / "OneDrive" / "3D Printing" / "SoB" / "Custom",
            Path("C:/Users/clugtu/OneDrive/3D Printing/SoB/Custom"),
        ]
        for candidate in candidates:
            if candidate.exists():
                custom_path = candidate
                break
    
    if not create_image.exists():
        print(f"Error: create_image.py not found at {create_image}", file=sys.stderr)
        return 1
    
    success_count = 0
    total_count = 0
    
    # ==== TIER 1: Player Denizens (Git) ====
    if standees_path.exists():
        player_json = standees_path / "player_denizen_standees.json"
        if player_json.exists():
            print("\n=== Player Denizens (Tier 1) ===")
            
            # All characters, all poses
            total_count += 1
            if run_command(
                [sys.executable, str(create_image), str(player_json), "--all", "--prompt-only", "--no-base"],
                golden_dir / "player_denizens_all.txt"
            ):
                success_count += 1
            
            # Individual poses (1:1, 1:2, 2:1, 2:2, etc.)
            for char_id in [1, 2]:
                for pose_id in [1, 2]:
                    total_count += 1
                    if run_command(
                        [sys.executable, str(create_image), str(player_json), f"{char_id}:{pose_id}", "--prompt-only", "--no-base"],
                        golden_dir / f"player_denizen_{char_id}_{pose_id}.txt"
                    ):
                        success_count += 1
    else:
        print(f"Warning: Standees path not found: {standees_path}", file=sys.stderr)
    
    # ==== TIER 1: Garou (OneDrive) ====
    if custom_path and custom_path.exists():
        garou_json = custom_path / "Garou" / "garou.json"
        if garou_json.exists():
            print("\n=== Garou (Tier 1) ===")
            
            # All characters, all forms
            total_count += 1
            if run_command(
                [sys.executable, str(create_image), str(garou_json), "--all", "--prompt-only"],
                golden_dir / "garou_all.txt"
            ):
                success_count += 1
            
            # Sample individual character forms
            test_cases = [
                ("The Howling Wind", "human"),
                ("The Howling Wind", "crinos"),
                ("The Iron Fang", "human"),
                ("The Iron Fang", "glabro"),
            ]
            
            for char_name, form in test_cases:
                total_count += 1
                safe_char = char_name.lower().replace(" ", "_")
                if run_command(
                    [sys.executable, str(create_image), str(garou_json), f"{char_name}:{form}", "--prompt-only"],
                    golden_dir / f"garou_{safe_char}_{form}.txt"
                ):
                    success_count += 1
            
            # Reference sheets
            for page in [1, 2]:
                total_count += 1
                if run_command(
                    [sys.executable, str(create_image), str(garou_json), "--page", str(page), "--prompt-only"],
                    golden_dir / "reference_sheets" / f"garou_page_{page}.txt"
                ):
                    success_count += 1
    else:
        print(f"Warning: Custom path not found or not specified. Use --custom-path", file=sys.stderr)
    
    # ==== TIER 2: Enemy Denizens (Git) ====
    if standees_path.exists():
        enemy_json = standees_path / "enemy_denizens_standees.json"
        if enemy_json.exists():
            print("\n=== Enemy Denizens (Tier 2) ===")
            
            # Sample a few enemies
            for char_id in [1, 2, 3]:
                for pose_id in [1, 2]:
                    total_count += 1
                    if run_command(
                        [sys.executable, str(create_image), str(enemy_json), f"{char_id}:{pose_id}", "--prompt-only", "--no-base"],
                        golden_dir / f"enemy_denizen_{char_id}_{pose_id}.txt"
                    ):
                        success_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Golden outputs generated: {success_count}/{total_count}")
    print(f"Output directory: {golden_dir}")
    
    if success_count < total_count:
        print(f"\n⚠️  Some outputs failed to generate. Check errors above.")
        return 1
    
    print(f"\n✓ All golden outputs generated successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
