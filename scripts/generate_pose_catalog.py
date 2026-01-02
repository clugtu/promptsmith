import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSE_LIB = ROOT / "rules" / "pose_library.json"
OUT_MD = ROOT / "rules" / "pose.md"


def shorten(text: str, limit: int = 140) -> str:
    if not text:
        return ""
    t = " ".join(text.split())
    return t if len(t) <= limit else t[: limit - 1].rstrip() + "…"


def main():
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


if __name__ == "__main__":
    main()
