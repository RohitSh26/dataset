import os
import ast
import json
from collections import defaultdict
from typing import List, Dict, Any

class PydanticFieldExtractor(ast.NodeVisitor):
    def __init__(self):
        self.numeric_fields = defaultdict(list)

    def visit_ClassDef(self, node: ast.ClassDef):
        print(f"Visiting class: {node.name}")
        is_pydantic_model = any(
            isinstance(base, ast.Name) and base.id == "BaseModel" or
            isinstance(base, ast.Attribute) and base.attr == "BaseModel"
            for base in node.bases
        )
        
        if is_pydantic_model:
            print(f"Identified Pydantic model: {node.name}")
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                    field_name = stmt.target.id
                    field_type = self.get_field_type(stmt.annotation)
                    print(f"Found field: {field_name} with type: {field_type}")
                    if field_type in {"int", "float"}:
                        self.numeric_fields[node.name].append({"field": field_name, "type": field_type})
        self.generic_visit(node)

    def get_field_type(self, annotation):
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Subscript):
            if isinstance(annotation.value, ast.Name):
                return annotation.value.id
            elif isinstance(annotation.value, ast.Attribute):
                return annotation.value.attr
        return None

def extract_numeric_fields_from_file(file_path: str) -> Dict[str, List[Dict[str, str]]]:
    print(f"Parsing file: {file_path}")
    with open(file_path, "r") as file:
        tree = ast.parse(file.read())
    
    extractor = PydanticFieldExtractor()
    extractor.visit(tree)
    
    return extractor.numeric_fields

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