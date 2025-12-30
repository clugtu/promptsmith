"""Add explicit 'form' field to all refinements in garou.json"""
import json
from pathlib import Path

def add_form_references(json_path: Path):
    """Add 'form' field to each refinement based on its name."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get available forms from thematic_rules
    forms = data.get('thematic_rules', {}).get('forms', {})
    form_names = set(forms.keys())
    
    # Process each character
    for char in data.get('characters', []):
        for ref in char.get('refinements', []):
            ref_name = ref.get('name', '').lower()
            # Add form field if the refinement name matches a form definition
            if ref_name in form_names:
                # Insert 'form' field right after 'name'
                ref_items = list(ref.items())
                new_ref = {}
                for key, value in ref_items:
                    new_ref[key] = value
                    if key == 'name':
                        new_ref['form'] = ref_name
                ref.clear()
                ref.update(new_ref)
    
    # Write back to file with proper formatting
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Added 'form' references to {json_path}")

if __name__ == '__main__':
    garou_path = Path(r"D:\OneDrive\3D Printing\SoB\Custom\Garou\garou.json")
    add_form_references(garou_path)
