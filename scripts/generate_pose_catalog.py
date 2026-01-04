#!/usr/bin/env python
"""Generate pose catalog documentation and ChatGPT pose study prompts.

This script reads from the pose library JSON file and can:
1. Generate a markdown table catalog of all poses with their properties
2. Create ChatGPT image prompts for pose study reference sheets with mannequins

Usage:
    # Generate markdown catalog
    python generate_pose_catalog.py
    
    # Generate pose study prompt for specific poses
    python generate_pose_catalog.py 1-9
    python generate_pose_catalog.py 1,3,5-7,10
    
    # Copy prompt to clipboard
    python generate_pose_catalog.py 1-9 --copy
"""

import json
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
POSE_LIB = ROOT / "rules" / "pose_library.json"
OUT_MD = ROOT / "rules" / "pose.md"


def shorten(text: str, limit: int = 140) -> str:
    """Truncate text to a maximum length with ellipsis.
    
    Args:
        text: The text to shorten
        limit: Maximum character length (default: 140)
    
    Returns:
        Shortened text with ellipsis if truncated, or original if within limit
    """
    if not text:
        return ""
    t = " ".join(text.split())
    return t if len(t) <= limit else t[: limit - 1].rstrip() + "…"


def parse_range(range_str: str, max_poses: int) -> list[int]:
    """Parse range string into list of zero-based pose indices.
    
    Supports comma-separated values and hyphenated ranges.
    
    Args:
        range_str: Range specification (e.g., '1-9', '1,3,5-7', '1,2,3')
        max_poses: Maximum number of available poses for validation
    
    Returns:
        List of zero-based indices for selected poses
        
    Examples:
        >>> parse_range('1-3', 10)
        [0, 1, 2]
        >>> parse_range('1,3,5', 10)
        [0, 2, 4]
        >>> parse_range('1-3,7-9', 10)
        [0, 1, 2, 6, 7, 8]
    """
    indices = []
    for part in range_str.split(','):
        if '-' in part:
            start, end = part.split('-')
            indices.extend(range(int(start) - 1, int(end)))
        else:
            indices.append(int(part) - 1)
    return [i for i in indices if 0 <= i < max_poses]


def generate_pose_study_prompt(poses: list[dict], indices: list[int]) -> str:
    """Generate a ChatGPT DALL-E image prompt for pose study reference sheet.
    
    Creates a detailed prompt for generating a grid layout of wooden artist mannequins
    demonstrating selected poses. Each mannequin is labeled with its pose name and
    includes detailed pose instructions.
    
    Args:
        poses: List of pose dictionaries from pose_library.json
        indices: Zero-based indices of poses to include in the study
    
    Returns:
        Formatted prompt string ready for ChatGPT image generation
    """
    selected = [poses[i] for i in indices]
    
    prompt_parts = [
        "Create a pose study reference sheet showing mannequins in different poses.",
        f"\n\nGenerate {len(selected)} Anatomical Neutral 'Grey Man' mannequins arranged in a grid layout (3-4 per row).",
        "Each mannequin should be clearly labeled with its pose name below it.",
        "\n\nPoses to display:\n"
    ]
    
    for i, pose in enumerate(selected, 1):
        name = pose.get('name', f'pose_{i}')
        pose_prompt = pose.get('pose_prompt', '')
        figure_type = pose.get('figure_type', '')
        support_points = ', '.join(pose.get('support_points', []))
        
        prompt_parts.append(
            f"{i}. **{name}** ({figure_type}): {pose_prompt}"
        )
        if support_points:
            prompt_parts.append(f"   - Support: {support_points}")
        prompt_parts.append("")
    
    prompt_parts.extend([
        "\nStyle requirements:",
        "- Clean white background",
        "- Consistent lighting from top-left",
        "- Each mannequin shown in 3/4 view to display pose clearly",
        "- Anatomical Neutral 'Grey Man' style: featureless grey humanoid with accurate human proportions and joint articulation",
        "- Clear pose name label beneath each figure",
        "- Professional reference sheet layout"
    ])
    
    return '\n'.join(prompt_parts)


def generate_markdown():
    """Generate markdown catalog table of all poses.
    
    Reads pose_library.json and creates a comprehensive markdown table with all
    pose properties including pose_id, name, figure_type, support_points, hand
    configurations, and truncated pose prompts. Output is written to rules/pose.md.
    """
    data = json.loads(POSE_LIB.read_text(encoding="utf-8"))
    poses = data.get("poses", [])

    header = (
        "# Pose Catalog\n\n"
        "Auto-generated from rules/pose_library.json.\n\n"
        "| pose_id | name | figure_type | pose_style | support_points | base_contact_plan | handedness_mode | prop_visibility_mode | main_hand | off_hand | prompt (short) |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|\n"
    )

    rows = []
    for p in poses:
        main_hand = p.get("main_hand", {})
        off_hand = p.get("off_hand", {})

        def fmt_hand(h: dict) -> str:
            return ", ".join(
                f"{k}:{'/'.join(v) if isinstance(v, list) else v}"
                for k, v in [
                    ("slot", h.get("prop_slot", "")),
                    ("class", h.get("prop_class", [])),
                    ("action", h.get("action", "")),
                    ("orientation", h.get("orientation", "")),
                    ("vis", h.get("prop_visibility_mode", "")),
                ]
                if v not in (None, "", [])
            )

        row = "| {pose_id} | {name} | {figure_type} | {pose_style} | {support_points} | {base_contact_plan} | {handedness_mode} | {prop_visibility_mode} | {main_hand} | {off_hand} | {prompt} |".format(
            pose_id=p.get("pose_id", ""),
            name=p.get("name", ""),
            figure_type=p.get("figure_type", ""),
            pose_style=p.get("pose_style", ""),
            support_points="/".join(p.get("support_points", [])),
            base_contact_plan=p.get("base_contact_plan", ""),
            handedness_mode=p.get("handedness_mode", ""),
            prop_visibility_mode=p.get("prop_visibility_mode", ""),
            main_hand=fmt_hand(main_hand),
            off_hand=fmt_hand(off_hand),
            prompt=shorten(p.get("pose_prompt", "")),
        )
        rows.append(row)

    OUT_MD.write_text(header + "\n".join(rows) + "\n", encoding="utf-8")
    print(f"Generated markdown catalog: {OUT_MD}")


def main():
    """Main entry point for the pose catalog generator.
    
    Parses command-line arguments and either generates a markdown catalog
    or creates a ChatGPT pose study prompt based on the provided range.
    """
    parser = argparse.ArgumentParser(
        description='Generate pose catalog markdown or pose study prompts'
    )
    parser.add_argument(
        'range',
        nargs='?',
        help='Pose range for study (e.g., "1-9" or "1,3,5-7"). If omitted, generates markdown catalog.'
    )
    parser.add_argument(
        '--copy',
        action='store_true',
        help='Copy the prompt to clipboard (Windows only)'
    )
    
    args = parser.parse_args()
    
    data = json.loads(POSE_LIB.read_text(encoding="utf-8"))
    poses = data.get("poses", [])
    
    if args.range:
        # Generate pose study prompt
        indices = parse_range(args.range, len(poses))
        if not indices:
            print(f"Error: No valid poses found in range '{args.range}'")
            return
        
        prompt = generate_pose_study_prompt(poses, indices)
        print(prompt)
        print(f"\n--- Pose study prompt for poses: {args.range} ---")
        
        if args.copy:
            try:
                import subprocess
                subprocess.run(['clip'], input=prompt.encode('utf-16le'), check=True)
                print("\n✓ Copied to clipboard")
            except Exception as e:
                print(f"\n✗ Failed to copy to clipboard: {e}")
    else:
        # Generate markdown catalog (original behavior)
        generate_markdown()


if __name__ == "__main__":
    main()
