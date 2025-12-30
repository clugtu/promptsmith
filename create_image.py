"""create_image.py

Generate an image from prompts stored in a JSON file (garou.json).

Usage examples (PowerShell):
  python create_image.py garou.json 1:1
  python create_image.py myproject.json alpha:human --dry-run
  python create_image.py garou.json --character 1 --form human
  python create_image.py garou.json 1 --all
  python create_image.py garou.json --list

Notes:
- First argument is the JSON filename (required)
- API calls require an OpenAI API key in the environment:
        $env:OPENAI_API_KEY = "..."
- If you only want a copy/paste prompt for ChatGPT, use --prompt-only (no API key needed).
- Supports nested refinements: use 1:1 or alpha:human or mixed (1:human, alpha:1)
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


FORMS = {"human", "glabro", "crinos", "hispo", "wolf"}


def format_for_chat(prompt: str) -> str:
    """Format a prompt for copy/paste into ChatGPT."""
    return prompt.strip()


def copy_to_clipboard_windows(text: str) -> None:
    """Copy text to Windows clipboard using PowerShell."""
    try:
        # Pipe text to PowerShell's Set-Clipboard cmdlet via stdin
        result = subprocess.run(
            ["powershell", "-Command", "$input | Set-Clipboard"],
            input=text.encode('utf-8'),
            check=True,
            timeout=5,
            capture_output=True
        )
    except Exception as e:
        # Silently fail if clipboard copy doesn't work
        print(f"Warning: Could not copy to clipboard: {e}", file=sys.stderr)


@dataclass
class CharacterData:
    """Holds JSON data for a character."""
    data: Dict[str, Any]
    generic_snippet: str
    miniature_snippet: str

    def get_id(self) -> int:
        return self.data.get("id", 0)

    def get_name(self) -> str:
        return self.data.get("name", "")

    def get_refinements(self) -> List[Dict[str, Any]]:
        return self.data.get("refinements", [])


def load_json_data(json_path: Path) -> Dict[str, Any]:
    """Load and parse the JSON file."""
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_generic_snippet(json_data: Dict[str, Any]) -> str:
    """Extract the generic render rules prompt snippet from JSON."""
    return json_data.get("generic_render_rules", {}).get("prompt_snippet", "")


def extract_miniature_snippet(json_data: Dict[str, Any]) -> str:
    """Extract the miniature scale rules prompt snippet from JSON."""
    return json_data.get("miniature_scale_rules", {}).get("prompt_snippet", "")


def extract_thematic_snippet(json_data: Dict[str, Any]) -> str:
    """Extract the general thematic rules prompt snippet from JSON."""
    return json_data.get("thematic_rules", {}).get("prompt_snippet", "")


def extract_thematic_forms(json_data: Dict[str, Any]) -> Dict[str, str]:
    """Extract form definitions from thematic_rules.forms.
    Returns a dict mapping form names to their prompt_snippet."""
    forms = json_data.get("thematic_rules", {}).get("forms", {})
    return {name: form.get("prompt_snippet", "") for name, form in forms.items()}


def remove_base_language(miniature_snippet: str) -> str:
    """Remove 'mounted on a ... base' phrase from the 40mm snippet.

    This keeps the rest of the 40mm miniature styling (materials, lighting, scale cues)
    while avoiding a physical base being depicted.
    """
    s = miniature_snippet

    # Remove common base phrases used in JSON and likely variants.
    base_patterns = [
        r",\s*mounted on a round gaming base\s*\(about 32mm\)\s*",
        r",\s*mounted on a round gaming base\s*",
        r",\s*on a round gaming base\s*\(about 32mm\)\s*",
        r",\s*on a round gaming base\s*",
        r",\s*mounted on a gaming base\s*",
        r",\s*on a gaming base\s*",
        r",\s*mounted on a base\s*",
        r",\s*on a base\s*",
        r",\s*round base\s*\(about 32mm\)\s*",
        r",\s*round base\s*",
        r",\s*display base\s*",
        r",\s*plinth\s*",
    ]
    for pat in base_patterns:
        s = re.sub(pat, ", ", s, flags=re.IGNORECASE)

    # Also remove any remaining comma-separated segments that still mention base/plinth.
    parts = [p.strip() for p in s.split(",") if p.strip()]
    parts = [
        p
        for p in parts
        if not re.search(r"\b(base|based|gaming base|round base|plinth)\b", p, flags=re.IGNORECASE)
    ]
    return ", ".join(parts)


class PromptNotFoundError(RuntimeError):
    pass


def find_character_by_id_or_name(
    json_data: Dict[str, Any], identifier: Union[int, str]
) -> Optional[Dict[str, Any]]:
    """Find a character by numeric ID or string name."""
    characters = json_data.get("characters", [])
    
    # Try as integer ID first
    if isinstance(identifier, int):
        for char in characters:
            if char.get("id") == identifier:
                return char
    
    # Try as string (name or string representation of number)
    id_str = str(identifier).lower()
    
    # Try as numeric string
    try:
        num_id = int(identifier)
        for char in characters:
            if char.get("id") == num_id:
                return char
    except (ValueError, TypeError):
        pass
    
    # Try as name
    for char in characters:
        if char.get("name", "").lower() == id_str:
            return char
    
    return None


def find_refinement_by_id_or_name(
    refinements: List[Dict[str, Any]], identifier: Union[int, str]
) -> Optional[Dict[str, Any]]:
    """Find a refinement by numeric ID or string name."""
    # Try as integer ID
    if isinstance(identifier, int):
        for ref in refinements:
            if ref.get("id") == identifier:
                return ref
    
    # Try as string
    id_str = str(identifier).lower()
    
    # Try as numeric string
    try:
        num_id = int(identifier)
        for ref in refinements:
            if ref.get("id") == num_id:
                return ref
    except (ValueError, TypeError):
        pass
    
    # Try as name
    for ref in refinements:
        if ref.get("name", "").lower() == id_str:
            return ref
    
    return None


def parse_refinement_path(path_str: str) -> List[str]:
    """Parse a refinement path like '1:1' or 'alpha:human' into components."""
    return [p.strip() for p in path_str.split(":") if p.strip()]


def resolve_prompt_from_json(
    json_data: Dict[str, Any], 
    character: Optional[Union[int, str]] = None,
    form: Optional[str] = None,
    refinement_path: Optional[str] = None
) -> Tuple[str, List[str]]:
    """Resolve a prompt from JSON using various addressing methods.
    
    Args:
        json_data: The loaded JSON data
        character: Character ID (int) or name (str)
        form: Form/refinement name
        refinement_path: Full path like '1:1' or 'alpha:human'
    
    Returns:
        Tuple of (prompt string, list of thematic snippets from refinement path)
    """
    # Extract form definitions once
    thematic_forms = extract_thematic_forms(json_data)
    
    # Parse refinement_path if provided
    if refinement_path:
        parts = parse_refinement_path(refinement_path)
        if len(parts) >= 1:
            character = parts[0]
        if len(parts) >= 2:
            form = parts[1]
    
    if character is None:
        raise PromptNotFoundError("Character must be specified")
    
    # Find the character
    char_data = find_character_by_id_or_name(json_data, character)
    if not char_data:
        raise PromptNotFoundError(f"Character not found: {character}")
    
    # If no form specified, return character description or first refinement
    if form is None:
        refinements = char_data.get("refinements", [])
        if not refinements:
            raise PromptNotFoundError(
                f"No refinements found for character: {character}"
            )
        # Return the first refinement's prompt and its thematic snippet
        first_ref = refinements[0]
        thematic = []
        if "thematic_snippet" in first_ref:
            snippet_val = first_ref["thematic_snippet"]
            if isinstance(snippet_val, list):
                # List of references - resolve each one
                for ref in snippet_val:
                    if ref in thematic_forms and thematic_forms[ref]:
                        thematic.append(thematic_forms[ref])
                    else:
                        # Not a form reference, use as-is
                        thematic.append(ref)
            else:
                # Legacy: single string value
                thematic.append(snippet_val)
        return first_ref.get("prompt", ""), thematic
    
    # Find the refinement (form)
    refinements = char_data.get("refinements", [])
    refinement = find_refinement_by_id_or_name(refinements, form)
    
    if not refinement:
        available = [f"{r.get('id')}:{r.get('name')}" for r in refinements]
        raise PromptNotFoundError(
            f"Refinement '{form}' not found for character '{character}'. "
            f"Available: {', '.join(available)}"
        )
    
    # Collect thematic snippet from this refinement
    thematic = []
    if "thematic_snippet" in refinement:
        snippet_val = refinement["thematic_snippet"]
        if isinstance(snippet_val, list):
            # List of references - resolve each one
            for ref in snippet_val:
                if ref in thematic_forms and thematic_forms[ref]:
                    thematic.append(thematic_forms[ref])
                else:
                    # Not a form reference, use as-is
                    thematic.append(ref)
        else:
            # Legacy: single string value
            thematic.append(snippet_val)
    
    return refinement.get("prompt", ""), thematic


def build_final_prompt(
    base_prompt: str,
    *,
    thematic_snippets: List[str] = None,
    thematic_general: str = "",
    generic_snippet: str,
    miniature_snippet: str,
    include_generic: bool,
    include_miniature: bool,
    no_base: bool = False,
) -> str:
    base_prompt = base_prompt.strip().rstrip(",")

    parts = [base_prompt]
    
    # Add thematic snippets from refinements
    if thematic_snippets:
        parts.extend(thematic_snippets)
    
    # Add general thematic snippet
    if thematic_general:
        parts.append(thematic_general)
    
    if include_generic and generic_snippet:
        parts.append(generic_snippet)
    if include_miniature and miniature_snippet:
        parts.append(miniature_snippet)

    if no_base:
        parts.append(
            "no base, no stand, not mounted, no plinth, no pedestal, no ground plane"
        )

    return ", ".join(p.strip().rstrip(",") for p in parts if p.strip())


def list_available_from_json(json_data: Dict[str, Any]) -> str:
    """Return a human-friendly listing of available characters and refinements."""
    characters = json_data.get("characters", [])
    lines: List[str] = []
    
    total_refinements = sum(len(c.get("refinements", [])) for c in characters)
    lines.append(f"Total characters: {len(characters)}")
    lines.append(f"Total refinements: {total_refinements}")
    lines.append("")
    
    for char in characters:
        char_id = char.get("id", "?")
        char_name = char.get("name", "unknown")
        char_title = char.get("title", "")
        
        lines.append(f"{char_id} ({char_name}): {char_title}")
        
        refinements = char.get("refinements", [])
        for ref in refinements:
            ref_id = ref.get("id", "?")
            ref_name = ref.get("name", "?")
            ref_desc = ref.get("description", "")
            lines.append(f"  {char_id}:{ref_id} or {char_name}:{ref_name} - {ref_desc}")
        
        lines.append("")
    
    return "\n".join(lines)


def resolve_prompt(prompts: Dict[PromptKey, str], character: int, form: str) -> str:
    key = PromptKey(character=character, form=form.lower())
    try:
        return prompts[key]
    except KeyError as e:
        available = sorted(
            (k for k in prompts.keys() if k.character == character),
            key=lambda k: k.form,
        )
        available_forms = ", ".join(k.form for k in available) if available else "(none)"
        raise PromptNotFoundError(
            f"No prompt found for character={character} form={form!r}. "
            f"Available for that character: {available_forms}"
        ) from e


def generate_image_openai(prompt: str, *, model: str, size: str) -> bytes:
    """Call OpenAI Images API and return PNG bytes.

    Uses the official OpenAI Python SDK.
    """
    try:
        from openai import OpenAI  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "Missing dependency 'openai'. Install with: pip install openai"
        ) from e

    client = OpenAI()

    result = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
    )

    # The SDK can return either base64 or URLs depending on configuration/model.
    # Prefer b64_json when available.
    data0 = result.data[0]

    if getattr(data0, "b64_json", None):
        return base64.b64decode(data0.b64_json)

    url = getattr(data0, "url", None)
    if url:
        # Fall back to downloading the URL.
        # Avoid adding extra dependency; use urllib.
        import urllib.request

        with urllib.request.urlopen(url) as resp:
            return resp.read()

    raise RuntimeError("Unexpected images response format: no b64_json or url")


def build_output_path(
    out_dir: Path, *, character: Union[int, str], form: str
) -> Path:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_form = str(form).lower()
    safe_char = str(character).replace(":", "_")
    filename = f"garou_{safe_char}_{safe_form}_{ts}.png"
    return out_dir / filename


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="create_image",
        description=(
            "Read prompts from a JSON file and generate an image for a given character + form. "
            "Supports nested refinements using path syntax like '1:1' or 'alpha:human'."
        ),
    )
    parser.add_argument(
        "filename",
        type=str,
        help="JSON file containing character definitions (e.g., garou.json, myproject.json)",
    )
    parser.add_argument(
        "character_positional",
        nargs="?",
        type=str,
        help="Character ID (number or name) or full path like '1:1' or 'alpha:human'. Can also use --character flag.",
    )
    parser.add_argument(
        "--character",
        "-c",
        type=str,
        help="Character ID (number or name) or full path like '1:1' or 'alpha:human'. Required unless using --list.",
    )
    parser.add_argument(
        "--form",
        "-f",
        type=str,
        help="Form/refinement: human, glabro, crinos, hispo, wolf (or ID/name). Not needed if using path syntax in --character.",
    )
    parser.add_argument(
        "--json",
        "-j",
        type=Path,
        help="Alternative way to specify JSON file (overrides positional filename argument)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("out"),
        help="Output directory for images (default: ./out)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-image-1",
        help="OpenAI image model (default: gpt-image-1)",
    )
    parser.add_argument(
        "--size",
        type=str,
        default="1024x1024",
        help="Image size (default: 1024x1024)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the resolved prompt only; do not call the API",
    )

    parser.add_argument(
        "--prompt-only",
        action="store_true",
        help="Print the resolved prompt only (alias of --dry-run).",
    )

    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy prompt-only output to the clipboard (Windows).",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List available characters/forms found in the JSON and exit.",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate (or print) all forms for the given --character.",
    )

    parser.add_argument(
        "--no-miniature",
        action="store_true",
        help="Do not append the shared 40mm-miniature snippet to prompts.",
    )

    parser.add_argument(
        "--no-base",
        action="store_true",
        help="Do not include a miniature base in the 40mm snippet (keeps the 40mm look).",
    )

    parser.add_argument(
        "--no-generic",
        action="store_true",
        help="Do not append the shared generic rendering rules snippet to prompts.",
    )

    args = parser.parse_args(argv)

    if args.prompt_only:
        args.dry_run = True

    # Determine JSON file path (--json flag overrides positional filename)
    json_path = args.json if args.json else Path(args.filename)
    if not json_path.suffix:
        json_path = json_path.with_suffix(".json")

    # Load JSON data
    json_data = load_json_data(json_path)
    generic_snippet = extract_generic_snippet(json_data)
    miniature_snippet = extract_miniature_snippet(json_data)
    thematic_general = extract_thematic_snippet(json_data)
    thematic_forms = extract_thematic_forms(json_data)
    
    include_miniature = not args.no_miniature
    include_generic = not args.no_generic

    if include_miniature and args.no_base and miniature_snippet:
        miniature_snippet = remove_base_language(miniature_snippet)

    if args.list:
        print(list_available_from_json(json_data))
        return 0

    # Handle positional or flag-based character argument
    character_arg = args.character_positional or args.character
    
    if character_arg is None:
        parser.error("Character argument is required unless using --list. Use positional argument or --character flag.")

    # Parse character - could be path like "1:1" or "alpha:human"
    character_id = None
    form_id = None
    
    if ":" in character_arg:
        # Path syntax
        parts = parse_refinement_path(character_arg)
        if len(parts) >= 1:
            character_id = parts[0]
        if len(parts) >= 2:
            form_id = parts[1]
        
    else:
        character_id = character_arg
    
    # If form is also specified as argument, it overrides path
    if args.form:
        form_id = args.form

    if args.all and form_id:
        parser.error("Use either --all or specify a form, not both")

    # Basic key check early for nicer UX.
    if not args.dry_run and not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not set. In PowerShell: $env:OPENAI_API_KEY=\"...\""
        )

    # If no form specified, generate all refinements (--all is now default behavior)
    if not form_id or args.all:
        # Generate (or print) all refinements for this character
        char_data = find_character_by_id_or_name(json_data, character_id)
        if not char_data:
            raise PromptNotFoundError(f"Character not found: {character_id}")
        
        refinements = char_data.get("refinements", [])
        if not refinements:
            raise PromptNotFoundError(
                f"No refinements found for character: {character_id}"
            )

        if args.dry_run:
            blocks: list[str] = []
            for ref in refinements:
                ref_name = ref.get("name", "")
                p0 = ref.get("prompt", "")
                thematic_snip = []
                if "thematic_snippet" in ref:
                    snippet_val = ref["thematic_snippet"]
                    if isinstance(snippet_val, list):
                        # List of references - resolve each one
                        for ref_item in snippet_val:
                            if ref_item in thematic_forms and thematic_forms[ref_item]:
                                thematic_snip.append(thematic_forms[ref_item])
                            else:
                                # Not a form reference, use as-is
                                thematic_snip.append(ref_item)
                    else:
                        # Legacy: single string value
                        thematic_snip.append(snippet_val)
                p = build_final_prompt(
                    p0,
                    thematic_snippets=thematic_snip,
                    thematic_general=thematic_general,
                    generic_snippet=generic_snippet,
                    miniature_snippet=miniature_snippet,
                    include_generic=include_generic,
                    include_miniature=include_miniature,
                    no_base=args.no_base,
                )
                blocks.append(f"[{character_id}:{ref_name}]\n{format_for_chat(p)}")

            out_text = "\n\n".join(blocks).strip() + "\n"
            if args.copy:
                copy_to_clipboard_windows(out_text)
            print(out_text, end="")
            return 0

        args.out.mkdir(parents=True, exist_ok=True)
        for ref in refinements:
            ref_name = ref.get("name", "")
            p0 = ref.get("prompt", "")
            thematic_snip = []
            if "thematic_snippet" in ref:
                snippet_val = ref["thematic_snippet"]
                if isinstance(snippet_val, list):
                    # List of references - resolve each one
                    for ref_item in snippet_val:
                        if ref_item in thematic_forms and thematic_forms[ref_item]:
                            thematic_snip.append(thematic_forms[ref_item])
                        else:
                            # Not a form reference, use as-is
                            thematic_snip.append(ref_item)
                else:
                    # Legacy: single string value
                    thematic_snip.append(snippet_val)
            p = build_final_prompt(
                p0,
                thematic_snippets=thematic_snip,
                thematic_general=thematic_general,
                generic_snippet=generic_snippet,
                miniature_snippet=miniature_snippet,
                include_generic=include_generic,
                include_miniature=include_miniature,
                no_base=args.no_base,
            )
            png_bytes = generate_image_openai(p, model=args.model, size=args.size)
            out_path = build_output_path(
                args.out, character=character_id, form=ref_name
            )
            out_path.write_bytes(png_bytes)
            print(str(out_path))
        return 0

    # Single (character, form) - form_id must be specified to reach here
    prompt0, thematic_snip = resolve_prompt_from_json(
        json_data, character=character_id, form=form_id
    )
    prompt = build_final_prompt(
        prompt0,
        thematic_snippets=thematic_snip,
        thematic_general=thematic_general,
        generic_snippet=generic_snippet,
        miniature_snippet=miniature_snippet,
        include_generic=include_generic,
        include_miniature=include_miniature,
        no_base=args.no_base,
    )
    
    if args.dry_run:
        out_text = "create image: " + format_for_chat(prompt) + "\n"
        if args.copy:
            copy_to_clipboard_windows(out_text)
        print(out_text, end="")
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    png_bytes = generate_image_openai(prompt, model=args.model, size=args.size)
    out_path = build_output_path(args.out, character=character_id, form=form_id)
    out_path.write_bytes(png_bytes)
    print(str(out_path))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
