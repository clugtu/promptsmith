"""Refactor garou.json to use reference-based thematic_snippet lists"""
import json
from pathlib import Path

def refactor_thematic_snippets(json_path: Path):
    """Convert thematic_snippet strings to reference lists and remove form field."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get available forms from thematic_rules
    forms = data.get('thematic_rules', {}).get('forms', {})
    
    # Build a mapping of snippet text to form name
    snippet_to_form = {}
    for form_name, form_data in forms.items():
        snippet = form_data.get('prompt_snippet', '').strip()
        if snippet:
            snippet_to_form[snippet] = form_name
    
    # Process each character
    for char in data.get('characters', []):
        for ref in char.get('refinements', []):
            # Remove 'form' field if present
            if 'form' in ref:
                del ref['form']
            
            # Convert thematic_snippet to list of references
            if 'thematic_snippet' in ref:
                snippet_value = ref['thematic_snippet']
                if isinstance(snippet_value, list):
                    # Already converted, check each item
                    new_list = []
                    for item in snippet_value:
                        item_stripped = item.strip()
                        if item_stripped in snippet_to_form:
                            new_list.append(snippet_to_form[item_stripped])
                        else:
                            new_list.append(item_stripped)
                    ref['thematic_snippet'] = new_list
                else:
                    # String value, convert to list
                    snippet_stripped = snippet_value.strip()
                    # Check if it matches a known form snippet
                    if snippet_stripped in snippet_to_form:
                        ref['thematic_snippet'] = [snippet_to_form[snippet_stripped]]
                    else:
                        # Keep as is but wrap in list (could be custom snippet)
                        ref['thematic_snippet'] = [snippet_stripped]
    
    # Write back to file with proper formatting
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Refactored thematic snippets in {json_path}")

if __name__ == '__main__':
    garou_path = Path(r"D:\OneDrive\3D Printing\SoB\Custom\Garou\garou.json")
    refactor_thematic_snippets(garou_path)
