import os
import re
import json
from collections import defaultdict

def extract_numeric_fields_from_file(file_path: str) -> Dict[str, List[Dict[str, str]]]:
    with open(file_path, "r") as file:
        content = file.read()
    
    # Regex patterns to match Pydantic classes and their fields
    class_pattern = re.compile(r'class\s+(\w+)\(.*BaseModel.*\):')
    field_pattern = re.compile(r'\s*(\w+):\s*(int|float)')
    
    numeric_fields = defaultdict(list)
    
    for class_match in class_pattern.finditer(content):
        class_name = class_match.group(1)
        class_start = class_match.end()
        
        # Find fields within the class body
        for field_match in field_pattern.finditer(content, class_start):
            field_name, field_type = field_match.groups()
            numeric_fields[class_name].append({"field": field_name, "type": field_type})
    
    return numeric_fields

def extract_numeric_fields_from_directory(directory_path: str) -> Dict[str, List[Dict[str, str]]]:
    all_numeric_fields = defaultdict(list)
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                file_numeric_fields = extract_numeric_fields_from_file(file_path)
                for class_name, fields in file_numeric_fields.items():
                    all_numeric_fields[class_name].extend(fields)
    return all_numeric_fields

if __name__ == "__main__":
    directory_path = os.path.join(os.getcwd(), "src/shared/view")  # Adjust the path here
    numeric_fields = extract_numeric_fields_from_directory(directory_path)
    print(json.dumps(numeric_fields, indent=4))